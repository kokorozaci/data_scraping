# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['https://www.labirint.ru/']

    def __init__(self, subject):
        self.start_urls = [
            f'https://www.labirint.ru/search/{subject}/']

    def parse(self, response:HtmlResponse):
        next_page = response.xpath("//div[@class='pagination-next']/a/@href").extract_first()
        book_links = response.xpath("//a[@class='product-title-link']/@href").extract()
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)
        yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response:HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        price = response.xpath("//span[@class='buying-pricenew-val-number']/text()").extract()
        yield BookparserItem(name=name, price=price)
