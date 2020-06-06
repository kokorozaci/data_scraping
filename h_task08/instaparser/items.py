# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    follow_id = scrapy.Field()
    follow_name = scrapy.Field()
    follower_id = scrapy.Field()
    follower_name = scrapy.Field()
    follow_full_name = scrapy.Field()
    follow_pic_url = scrapy.Field()
    follow_is_private = scrapy.Field()
    follower_full_name = scrapy.Field()
    follower_pic_url = scrapy.Field()
    follower_is_private = scrapy.Field()



