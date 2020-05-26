# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    base_price = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()
    authors = scrapy.Field()
    rating = scrapy.Field()
    currency = scrapy.Field()


