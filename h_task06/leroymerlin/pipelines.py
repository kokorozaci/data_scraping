# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from urllib.parse import urlparse
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import hashlib

class LeroymerlinPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlin

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.update({'_id': item['_id']}, item, True)
        return item


class LeroymerlinPhotoPipelines(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            for img in item['photo']:
                try:
                    yield scrapy.Request(img, meta=item)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photo'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None):
        image_dir = request.meta['name']
        image_guid = hashlib.sha1(request.url.encode('utf-8')).hexdigest()
        return f'{image_dir}/{image_guid}.jpg'

    def thumb_path(self, request, thumb_id, response=None, info=None):
        image_dir = request.meta['name']
        thumb_guid = hashlib.sha1(request.url.encode('utf-8')).hexdigest()
        return f'{image_dir}/{thumb_id}/{thumb_guid}.jpg'


class StringsProcessingPipelines:
    def process_item(self, item, spider):
        item['price'] = float('.'.join(item['price']).replace(' ', ''))
        item['unit'] = ' '.join(item['unit'])
        item['currency'] = ' '.join(item['currency'])
        if 'second_price' in item:
            item['second_price'] = float('.'.join(item['second_price']).replace(' ', ''))
            item['second_unit'] = ' '.join(item['second_unit'])
            item['second_currency'] = ' '.join(item['second_currency'])
        return item


