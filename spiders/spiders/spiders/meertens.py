# -*- coding: utf-8 -*-
import itertools
import pandas
import scrapy
import string
from ..items import DetailedNameItem
from ..items import NameItem
from scrapy import log
from scrapy import Request
from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.shell import inspect_response
from werkzeug import urls


NAME_TYPES = {'eerstenaam': 'first', 'volgnaam': 'follow'}
DOMAIN = 'http://www.meertens.knaw.nl/'
LIST_URL = DOMAIN + 'nvb/naam/begintmet/'
LIST_PATTERN = DOMAIN + 'nvb/naam/pagina.*/begintmet/'
DETAILS_URL = (DOMAIN +
               'nvb/populariteit/absoluut/{gender}/{name_type}/{name}#data')

PATHS = {'list': "//table[@class='namelist']",
         'name': "//div[@class='name']/text()",
         'table': "//table[@class='nameinfo']",
         'graph': "//script"}
DATA_PATHS = {'man': '../data/scrapeable_males.csv',
              'vrouw': '../data/scrapeable_females.csv'}


class MeertensListSpider(CrawlSpider):
    """ Parse all pages listing names.
    """

    name = "meertens_list"
    allowed_domains = ["meertens.knaw.nl"]
    start_urls = [LIST_URL + letter for letter in string.ascii_lowercase]
    # Following line is used for debugging
    # start_urls = [BASE_URL + letter for letter in ['Anne-B']]
    rules = (
        Rule(LinkExtractor(allow=(LIST_PATTERN, )),
             callback='parse_item', follow=True),
    )

    def parse_start_url(self, response):
        """ Parse the start URLs also containing names.
        :param response: Response object
        :return: Items
        :rtype: ..item.NameItem
        """
        for item in self.parse_item(response):
            yield item

    def parse_item(self, response):
        """ Parse a listing page.
        :param response: Response object
        :return: Item
        :rtype: ..item.NameItem
        """
        extracted_table = response.xpath(PATHS['list']).extract()
        if extracted_table:
            # Using pandas for parsing is easier than using xpath.
            table = pandas.read_html(extracted_table[0], header=0,
                                     index_col=0)[0]
            for name, values in table.iterrows():
                item = NameItem()
                item['name'] = name
                item['total_male'] = values['Mannen']
                item['total_female'] = values['Vrouwen']
                yield item
        else:
            self.log("No table on page: " + response.url, level=log.ERROR)


class MeertensDetailsSpider(scrapy.Spider):
    """ Parse details page.
    """

    name = "meertens_details"
    allowed_domains = ["meertens.knaw.nl"]

    def start_requests(self):
        """ Generate all requests by reading CSV with names.
        :return:
        """
        for gender, path in DATA_PATHS.iteritems():
            names = pandas.read_csv(path, index_col=False, encoding='utf-8',
                                    names=['name'])
            # names = pandas.read_csv(path, index_col=False, encoding='utf-8',
                                    # names=['name']).iloc[:20]
            names = names[(names.name == 'Anne')]
            self.log(str(names))
            for name_type, name in itertools.product(NAME_TYPES, names.values):
                self.log('type' + name_type)
                self.log('name' + name)
                self.log('gender' + gender)
                yield self._generate_request(gender, name_type, name[0])

    def _generate_request(self, gender, name_type, name):
        """ Generate a request for a given gender, type and name.
        :param gender: Gender
        :type: str
        :param name_type: Name type
        :type: str
        :param name: Name
        :type: str
        :return: Request
        :rtype scrapy.Request
        """
        url = DETAILS_URL.format(gender=gender, name_type=name_type,
                                 name=urls.url_fix(name))
        self.log('Generated URL: ' + url)
        request = Request(url)
        return request

    def parse(self, response):
        """ Parse a page.
        :param response: Response object
        :return: Item object
        :rtype: ..item.DetailedNameItem
        """
        item = DetailedNameItem()
        item['name'] = response.xpath(PATHS['name']).extract()[0]
        item['name_type'] = self._get_name_type(response)
        item['gender'] = self._get_gender(response)
        item = self._parse_table(response, item)
        # Graph with year data is not available for all names.
        item['has_details'] = self._contains_graph(response)
        if item['has_details']:
            item = self._parse_graph(response, item)
        yield item

    def _get_name_type(self, response):
        """ Get name type from URL.
        :param response: Response object
        :return: 'first' or 'follow'
        :rtype: str
        """
        split_url = response.url.split('populariteit/absoluut/')
        name_type = split_url[1].split('/')[1]
        return name_type

    def _get_gender(self, response):
        """ Get gender from URL.
        :param response: Response object
        :return: Gender
        :rtype: str
        """
        split_url = response.url.split('populariteit/absoluut/')
        gender = split_url[1].split('/')[0]
        return gender

    def _parse_table(self, response, item):
        """ Parse table and store in item.
        :param response: Response object
        :param item: Item object (with key gender in ('male', 'female')
        :return: Updated item
        :rtype ..items.NameItem
        """
        html_table = response.xpath(PATHS['table']).extract()[0]
        parsed_table = pandas.read_html(html_table)[0]
        if item['gender'] == 'man':
            offset = 0
        elif item['gender'] == 'vrouw':
            offset = 3
        else:
            self.log("Unknown gender: " + item['gender'])
            return item
        item['first_count'] = parsed_table.ix[1 + offset, 2]
        item['first_percent'] = parsed_table.ix[1 + offset, 4]
        item['follow_count'] = parsed_table.ix[2 + offset, 2]
        item['follow_percent'] = parsed_table.ix[2 + offset, 4]
        # TODO: add flag if sufficient stats for first and follow
        return item

    def _contains_graph(self, response):
        """ Check body text if the page contains a graph.
        :param response: Response object
        :return: True if page contains graph
        :rtype: bool
        """
        has_data = ('Te weinig gegevens voor het tonen van populariteit' not in
                    response.body)
        return has_data

    def _parse_graph(self, response, item):
        """ Parse the graph.
        :param response: Response object
        :param item: Item object
        :return: Updated item
        :rtype ..item.NameItem
        """
        graph = self._get_graph(response)
        if graph:
            graph_data = self._parse_graph_javascript(graph)
            item.update(graph_data)
        return item

    def _get_graph(self, response):
        """ Get Javascript code containing the graph.
        :param response: Response object
        :return: Graph code
        :rtype: str
        """
        graph_list = [g for g in response.xpath(PATHS['graph']).extract()
                      if 'var year_list = new Array(' in g]
        graph = None
        if len(graph_list) == 1:
            graph = graph_list[0]
        elif len(graph_list) > 0:
            self.log("Found multiple graphs for URL: " + response.url)
        else:
            self.log("Found no graphs for URL: " + response.url)
        return graph

    def _parse_graph_javascript(self, graph):
        """ Parse Javascript code from the graph to get name stats.
        :param graph: Graph code (see _get_graph())
        :type: str
        :return: Data parsed from the graph
        :rtype: dict
        """
        data = {}
        for line in graph.split('\n'):
            if 'var year_list = ' in line:
                data['year'] = self._convert_array_string(line)
            elif 'var value_list = ' in line:
                data['value'] = self._convert_array_string(line)
            elif 'var stepsize_list' in line:
                data['step_size'] = self._convert_array_string(line)
            elif 'var steptotal_value_list = ' in line:
                data['step_total_value'] = self._convert_array_string(line)
            elif 'var steptotal_approximation_list = ' in line:
                data['step_total_approximation'] = self._convert_array_string(line)
            elif 'var approximation_list = ' in line:
                data['approximation'] = self._convert_array_string(line)
        return data

    def _convert_array_string(self, s):
        """ Convert string with Array(); to a list.
        :param s: String containing Array definition
        :type: str
        :return: Elements in the Array
        :rtype: list

        Note: only works for this specific case for a line consisting of only
        one Array definition (e.g. a = new Array(3, 1); but not
        a = new Array(3, 1); b = new Array(3, 1);)
        """
        i_start = s.find('Array(') + len('Array(')
        i_end = s.rfind(');')
        array_string = s[i_start:i_end]
        return array_string.split(',')
