"""
1)Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex.news
Для парсинга использовать xpath. Структура данных должна содержать:
* название источника,
* наименование новости,
* ссылку на новость,
* дата публикации

"""

from lxml import html
from pprint import pprint
from datetime import datetime, timedelta
import requests
import re
from time import sleep


class Scraper:
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.61 Safari/537.36'}

    def __init__(self, link, params=None):
        self.main_link = link
        self.params = params

    def _response(self, refer=''):
        return requests.get(self.main_link+refer, headers=self.HEADER)

    def dom(self, refer=''):
        return html.fromstring(self._response(refer).text)


class MailNewsParser(Scraper):
    MAIN_LINK = 'https://news.mail.ru'

    def __init__(self, params=None):
        super().__init__(self.MAIN_LINK, params)

    def _get_info(self, refer=''):
        news = []
        news_blocks = self.dom(refer).xpath("//div[@data-module='TrackBlocks']")
        blocks = []
        for block in news_blocks:
            xpath_str = ".//a[contains(@href, 'politics')] |" \
                        " //a[contains(@href, 'sportmail')] | " \
                        "//a[contains(@href, 'society')] |" \
                        " //a[contains(@href, 'economics')] | " \
                        "//a[contains(@href, 'incident')]"
            blocks.extend(block.xpath(xpath_str))
        links = []
        for block in blocks:
            url = block.xpath("./@href")
            if re.search(r'\d', ''.join(url)) and not '/rss/' in url[0]:
                links.append(self.MAIN_LINK + url[0] if 'https://' not in url[0] else url[0])
        i = 0
        links = list(set(links))
        for link in links:
            i += 1
            sleep(0.1 if i // 10 != 0 else 1)
            data = {}
            data['link'] = link
            data['date'], data['source'], data['name'] = self._get_subinfo(link=link)
            news.append(data)
        return news

    def _get_subinfo(self, link):
        data = html.fromstring(requests.get(link, headers=self.HEADER).text).xpath("//span[@class='note']//@datetime | "
                                                                                   "//span[@class='note']//span[@class='link__text']/text() | "   #//span[@class='note']//@href |
                                                                                   "//h1[@class='hdr__inner']/text()")
        date = datetime.strptime(data[0], "%Y-%m-%dT%H:%M:%S%z")
        source = data[1]
        name = data[2]
        return date, source, name

    @property
    def news(self):
        return self._get_info()


class LentaRuParser(Scraper):
    MAIN_LINK = 'https://lenta.ru'

    def __init__(self, params=None):
        super().__init__(self.MAIN_LINK, params)

    @staticmethod
    def int_value_from_ru_month(date_str):
        RU_MONTH_VALUES = {
            'января': '01',
            'февраля': '02',
            'марта': '03',
            'апреля': '04',
            'мая': '05',
            'июня': '06',
            'июля': '07',
            'августа': '08',
            'сентября': '09',
            'октября': '10',
            'ноября': '11',
            'декабря': '12'
        }
        for k, v in RU_MONTH_VALUES.items():
            date_str = date_str.replace(k, v)

        return date_str

    def _get_info(self, refer=''):
        news = []
        blocks = self.dom(refer).xpath("//a[time]")
        for block in blocks:
            data = {}
            data['name'] = block.xpath("./text()")[0].replace('\xa0', ' ')
            data['link'] = self.MAIN_LINK + block.xpath("./@href")[0]
            data['date'] = datetime.strptime(self.int_value_from_ru_month(block.xpath("./time/@datetime")[0]), " %H:%M, %d %m %Y")
            data['source'] = 'Lenta.ru'
            news.append(data)
        return news

    @property
    def news(self):
        return self._get_info()


class YandexNewsParser(Scraper):
    MAIN_LINK = 'https://yandex.ru'

    def __init__(self, params=None):
        super().__init__(self.MAIN_LINK+'/news', params)

    @staticmethod
    def parse_source(text):
        text = text.replace('\xa0', ' ')
        source = text[:-6]
        if 'вчера в' in source:
            source = source.replace('вчера в', '')[:-1]
            date = datetime.strptime(str((datetime.now()-timedelta(days=1)).date()) + text[-6:] + '+03:00', "%Y-%m-%d %H:%M%z")
        else:
            date = datetime.strptime(str(datetime.now().date()) + text[-6:] + '+03:00', "%Y-%m-%d %H:%M%z")
        return source, date

    @staticmethod
    def parse_link(link):
        link = link.split('?')
        return link[0]


    def _get_info(self, refer=''):
        news = []
        blocks = self.dom(refer).xpath("//td[@class = 'stories-set__item'] | //div[@class = 'story__content']")
        for block in blocks:
            data = {}
            data['name'] = block.xpath(".//h2//a/text()")[0].replace('\xa0', ' ')
            data['link'] = self.MAIN_LINK + self.parse_link(block.xpath(".//h2//a/@href")[0])
            data['source'],  data['date'] = self.parse_source(block.xpath(".//div[@class='story__date']/text()")[0])
            news.append(data)
        return news

    @property
    def news(self):
        return self._get_info()


class NewsScraper:
    def __init__(self):
        self.mail = MailNewsParser()
        self.lenta = LentaRuParser()
        self.yandex = YandexNewsParser()

    @property
    def news(self):
        all_news = self.mail.news
        all_news.extend(self.lenta.news)
        all_news.extend(self.yandex.news)
        return all_news


if __name__=='__main__':
    news = NewsScraper()
    pprint(news.news)

