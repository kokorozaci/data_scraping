# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']

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
        link = response.url
        base_price = response.xpath("//div[@class = 'buying-priceold-val']/span/text()").extract_first()
        authors = response.xpath("//div[contains(text(), 'Автор:')]/a/text()").extract()
        if not base_price:
            price = response.xpath("//div[@class='buying-price-val']/span/text()").extract_first()
        else:
            price = response.xpath("//div[@class='buying-pricenew-val']/span/text()").extract_first()
        rating = response.xpath("//div[@id='rate']/text()").extract_first()
        currency = response.xpath("//span[@class='buying-pricenew-val-currency']/text()").extract_first()
        yield BookparserItem(name=name, link=link, price=price,
                             authors=authors, base_price=base_price,
                             rating=rating, currency=currency)
