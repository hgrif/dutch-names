# Dutch Name Statistics

Scrape Dutch names stats, enrich them with cohort tables and serve them via a web app.

The goal of this project is to obtain the expected number of people alive with a given name. Birth rates per name are scraped from the [Nederlandse Voornamenbank](http://meertens.knaw.nl/nvb/) (set up by the [Meertens Instituut](http://www.meertens.knaw.nl/)). The expected number of people alive for a given name & gender are calculated using yearly life expectancies give by the [CBS](http://www.cbs.nl). This project is inspired by/copied from FiveThirtyEight's excellent article [How to Tell Someone’s Age When All You Know Is Her Name](http://fivethirtyeight.com/features/how-to-tell-someones-age-when-all-you-know-is-her-name/).


# Status
<li> Scraping: done </li>
<li> Data manipulation: done/WIP </li>
<li> Web app: WIP (see branch <code>website</code>) </li>


# Usage


#### Scraping

Scraping is done with <code>scrapy</code> and consists of two stages. First all the names on the website are collected with their summary statistics. From those statistics the subset of names can with yearly rates are determined and are then scraped.

<li> Change directory to <code>[dutch-names/spiders](spiders)</code>: </li>

<code> cd spiders </code>

<li> Scrape names listed on websites: </li>
<code> scrapy crawl meertens_list -o list.json </code>

<li> Scrape names listed on websites: </li>
<code> scrapy crawl meertens_details -o details.json </code>


#### Data manipulation
IPython Notebook [Dutch Name Stats](Dutch%20Name%20Stats.ipynb)


#### Web app (WIP)
<code> python app/app.py </code>


# Tools

The project  uses the following tools:

<li> [d3.js](http://d3js.org/) </li>
<li> [IPython Notebook](http://ipython.org/notebook.html) </li>
<li> [Flask](http://flask.pocoo.org/) </li>
<li> [MongoDB](https://www.mongodb.org/) </li>
<li> [pandas](http://pandas.pydata.org/) </li>
<li> [Scrapy](http://scrapy.org/) </li>
