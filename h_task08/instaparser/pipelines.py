# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import scrapy


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.update({'_id': item['_id']}, item, True)
        return item

class ToIntPipeline:
    def process_item(self, item, spider):
        item['follow_id'] = int(item['follow_id'])
        item['follower_id'] = int(item['follower_id'])
        return item

class UserPhotoPipelines(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['follower_pic_url']:
            try:
                yield scrapy.Request(item['follower_pic_url'], meta={'id': item['follower_id']})
            except Exception as e:
                print(e)
        if item['follow_pic_url']:
            try:
                yield scrapy.Request(item['follow_pic_url'], meta={'id': item['follow_id']})
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        if results:
            item['follower_pic_url'] = results[0][1] if results[0][0] else item['follower_pic_url']
            item['follow_pic_url'] = results[1][1] if results[1][0] else item['follow_pic_url']
        return item

    def file_path(self, request, response=None, info=None):
        image_name = request.meta['id']
        return f'/{image_name}.jpg'
