from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from bookparser import settings
from bookparser.spiders.labirint import LabirintSpider
from bookparser.spiders.book24 import Book24Spider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    # answer = input('Введите вакансию')

    process.crawl(LabirintSpider, subject='программирование')
    process.crawl(Book24Spider, subject='программирование')
    process.start()