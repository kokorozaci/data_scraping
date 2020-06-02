# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.loader.processors import TakeFirst, MapCompose
import scrapy


def to_int(num):
    return int(num)


def params_clear(text):
    text = ' '.join(list(filter(None, text.replace('\n', '').split(' '))))
    if '.' in text:
        text = float(text)
    elif text.isdigit():
        text = int(text)
    return text

class LeroymerlinItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field(input_processor=MapCompose(to_int), output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field()
    currency = scrapy.Field()
    key = scrapy.Field(input_processor=MapCompose(params_clear))
    value = scrapy.Field(input_processor=MapCompose(params_clear))
    unit = scrapy.Field()
    parameters = scrapy.Field()
    second_price = scrapy.Field()
    second_unit = scrapy.Field()
    second_currency = scrapy.Field()
    photo = scrapy.Field()

