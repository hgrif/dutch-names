# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NameItem(scrapy.Item):
    name = scrapy.Field()
    total_male = scrapy.Field()
    total_female = scrapy.Field()


class DetailedNameItem(scrapy.Item):
    name = scrapy.Field()
    name_type = scrapy.Field()
    gender = scrapy.Field()
    first_count = scrapy.Field()
    first_percent = scrapy.Field()
    follow_count = scrapy.Field()
    follow_percent = scrapy.Field()
    year = scrapy.Field()
    value = scrapy.Field()
    step_size = scrapy.Field()
    step_total_value = scrapy.Field()
    step_total_approximation = scrapy.Field()
    approximation = scrapy.Field()
