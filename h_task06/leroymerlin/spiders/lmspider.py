# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from leroymerlin.items import LeroymerlinItem


class LmspiderSpider(scrapy.Spider):
    name = 'lmspider'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, text):
        # self.start_urls = [f'https://leroymerlin.ru/search/?q={text}']
        self.start_urls = [f'https://leroymerlin.ru/catalogue/{text}/']

    def parse(self, response):
        next_page = response.xpath("//div[@class='service-panel clearfix']"
                                   "//a[contains(@class,'next-paginator-button')]/@href").extract_first()
        product_links = response.xpath("//div[@class='ui-product-card']/@data-product-url").extract()
        for link in product_links:
            yield response.follow(link, callback=self.parse_product)
        yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('_id', "//span[@slot='article']/@content")
        loader.add_xpath('photo', "//source[@media=' only screen and (min-width: 1024px)']/@srcset")
        loader.add_xpath('key', "//dl/div//dt/text()")
        loader.add_xpath('value', "//dl/div/dd/text()")
        loader.add_xpath('price', "//uc-pdp-price-view[@slot = 'primary-price']/span[@slot='price']/text() | "
                         "//uc-pdp-price-view[@slot = 'primary-price']/span[@slot='fract']/text()")
        loader.add_xpath('currency', "//uc-pdp-price-view[@slot = 'primary-price']/span[@slot='currency']/text()")
        loader.add_xpath('unit', "//uc-pdp-price-view[@slot = 'primary-price']/span[@slot='unit']/text()")
        loader.add_xpath('second_price', "//uc-pdp-price-view[@slot = 'second-price']/span[@slot='price']/text() | "
                         "//uc-pdp-price-view[@slot = 'second-price']/span[@slot='fract']/text()")
        loader.add_xpath('second_currency', "//uc-pdp-price-view[@slot = 'second-price']/span[@slot='currency']/text()")
        loader.add_xpath('second_unit', "//uc-pdp-price-view[@slot = 'second-price']/span[@slot='unit']/text()")
        loader.add_value('link', response.url)

        yield loader.load_item()
