""""
Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from time import sleep

chrome_options = Options()
chrome_options.add_argument('start-maximized')


driver = webdriver.Chrome(options=chrome_options)

client = MongoClient('localhost', 27017)
mongo_base = client.m_video
collection = mongo_base['m_video']

driver.get('https://www.mvideo.ru/')
sleep(5)

while True:
    sleep(1)
    button = driver.find_elements_by_class_name('sel-hits-button-next')[2]
    if button.get_attribute('class') == 'next-btn sel-hits-button-next disabled':
        break
    button.click()

hit = driver.find_elements_by_class_name('sel-hits-block')[1]
products = hit.find_elements_by_class_name('gallery-list-item')

for i in products:
    link = i.find_element_by_tag_name('a').get_attribute('href')
    name = i.find_element_by_tag_name('a').get_attribute('data-track-label')
    data = i.find_element_by_tag_name('a').get_attribute('data-product-info').replace('\n', '').replace('\n', '')
    collection.insert_one({'link': link, 'name': name, 'data': data})

driver.quit()
