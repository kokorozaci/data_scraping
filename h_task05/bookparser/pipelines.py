# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

class BookparserStr:
    def process_item(self, item, spider):
        item['currency'] = item['currency'].strip()
        if spider.name == 'labirint':
            item['name'] = item['name'][item['name'].index(':')+2:]
        if spider.name == 'book24' and item['base_price'] and item['currency'] in item['base_price']:
            print(item['base_price'])
            item['base_price'] = item['base_price'].replace(item['currency'], '')
        if item['base_price']:
            item['base_price'] = item['base_price'].strip()
            item['base_price'] = int(item['base_price'])
        item['price'] = item['price'].replace(' ', '')
        item['price'] = int(item['price'])
        if item['rating']:
            if ',' in item['rating']:
                item['rating'] = item['rating'].replace(',', '.')
            item['rating'] = float(item['rating'])
        return item


class BookparserInsertDB:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.books

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
