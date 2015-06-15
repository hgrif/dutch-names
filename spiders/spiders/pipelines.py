# -*- coding: utf-8 -*-

# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from items import DetailedNameItem
from items import NameItem
from scrapy import exceptions
from scrapy import log


class ItemParserPipeline(object):

    def process_item(self, item, spider):

        if isinstance(item, NameItem):
            item = self._process_name(item)
        elif isinstance(item, DetailedNameItem):
            item = self._process_details(item)
        else:
            raise exceptions.DropItem("Unknown item: %s" % item)
        return item

    def _process_name(self, item):
        item['total_male'] = self._parse_total_number(item['total_male'])
        item['total_female'] = self._parse_total_number(item['total_female'])
        return item

    def _process_details(self, item):
        item = self._parse_name_type(item)
        item = self._parse_gender(item)
        item = self._parse_summary_stats(item)
        if item['has_details']:
            item = self._parse_yearly_stats(item)
        return item

    def _parse_total_number(self, s):
        """ Parse string with total stats for a name.
        :param s: String with number
        :type: str
        :return: Number
        :rtype: int
        """
        if s == '< 5':
            n = -1
        elif s == '-':
            n = 0
        else:
            n = int(s)
        return n

    def _parse_name_type(self, item):
        name_type_nl = item['name_type']
        if name_type_nl == 'eerstenaam':
            name_type = 'first'
        elif name_type_nl == 'volgnaam':
            name_type = 'follow'
        else:
            log.msg('Unknown name type %s for name: %s' % (name_type_nl,
                                                           item['name']))
            name_type = name_type_nl
        item['name_type'] = name_type
        return item

    def _parse_gender(self, item):
        gender_nl = item['gender']
        if gender_nl in('vrouw', 'female'):
            gender = 'female'
        elif gender_nl in('man', 'male'):
            gender = 'male'
        else:
            log.msg('Unknown gender %s for URL: %s' % (gender_nl,
                                                       item['name']))
            gender = gender_nl
        item['gender'] = gender
        return item

    def _parse_summary_stats(self, item):
        item['first_count'] = self._parse_count(item['first_count'])
        item['first_percent'] = self._parse_percent(item['first_percent'])
        item['follow_count'] = self._parse_count(item['follow_count'])
        item['follow_percent'] = self._parse_percent(item['follow_percent'])
        return item

    def _parse_count(self, count):
        if count == '--':
            c = 0
        elif count == '5':
            c = -1
        else:
            c = int(count)
        return int(c)

    def _parse_percent(self, percent):
        if percent == '--':
            p = 0
        elif percent == '0.0001%':
            p = -1
        else:
            p = float(percent[:-1])
        return p

    def _parse_yearly_stats(self, item):
        item['year'] = map(int, item['year'])
        item['value'] = map(float, item['value'])
        item['step_size'] = map(int, item['step_size'])
        item['step_total_value'] = map(int, item['step_total_value'])
        item['step_total_approximation'] = map(float,
                                               item['step_total_approximation'])
        item['approximation'] = map(float, item['approximation'])
        return item
