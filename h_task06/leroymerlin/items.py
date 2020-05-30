# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.loader.processors import TakeFirst, MapCompose
import scrapy
from lxml import html


def to_int(num):
    return int(num)

def params_to_dict(param):
    key = html.fromstring(param).xpath('//dt/text()')[0]
    value = html.fromstring(param).xpath('./dd/text()')[0]
    value = ' '.join(list(filter(None, value.replace('\n', '').split(' '))))
    if '.' in value:
        value = float(value)
    elif value.isdigit():
        value = int(value)
    params = {key: value}
    return params


class LeroymerlinItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field(input_processor=MapCompose(to_int), output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field()
    unit_price = scrapy.Field()
    currency = scrapy.Field()
    unit = scrapy.Field()
    second_price = scrapy.Field()
    second_unit = scrapy.Field()
    second_currency = scrapy.Field()
    parameters = scrapy.Field(input_processor=MapCompose(params_to_dict))
    photo = scrapy.Field()

