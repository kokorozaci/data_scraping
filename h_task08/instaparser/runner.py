"""
1)Написать приложение, которое будет проходиться по указанному списку пользователей и собирать данные о его подписчиках и подписках.
2) По каждому пользователю, который является подписчиком или на которого подписан исследуемый объект нужно извлечь имя, id и фото (остальные данные по желанию). Фото можно дополнительно скачать.
3) Собранные данные необходимо сложить в базу данных.
"""

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instaparser.spiders.instagram import InstagramSpider
from instaparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)

    users = ['go_chatbot', '_.the_lashes._']
    process.crawl(InstagramSpider, users=users)

    process.start()