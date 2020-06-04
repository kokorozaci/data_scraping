""""
1) Написать программу, которая собирает входящие письма из своего
или тестового почтового ящика и сложить данные о письмах в базу данных
(от кого, дата отправки, тема письма, текст письма полный)"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from datetime import datetime


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

    if not date_str[date_str.index(',') - 2: date_str.index(',') - 1].isdigit():
        date_str = date_str.split(',')
        date_str = ''.join(date_str[0] + ' 2020,' + date_str[1])

    for k, v in RU_MONTH_VALUES.items():
        date_str = date_str.replace(k, v)

    return date_str


driver = webdriver.Chrome()

client = MongoClient('localhost', 27017)
mongo_base = client.mail
collection = mongo_base['mail_ru']

driver.get('https://mail.ru/')
elem = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'mailbox:login'))
)
elem.send_keys('study.ai_172@mail.ru')
elem.send_keys(Keys.RETURN)
elem = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'mailbox:password'))
)
elem.send_keys('NextPassword172')
elem.send_keys(Keys.RETURN)
a = None
links = set()
el = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'js-letter-list-item'))
)
while True:
    mails = driver.find_elements_by_class_name("js-letter-list-item")
    if a == mails[-1]:
        break
    a = mails[-1]
    [links.add(mail.get_attribute('href')) for mail in mails]
    actions = ActionChains(driver)
    actions.move_to_element(mails[-1])
    actions.perform()
links = list(links)
for link in links:
    driver.get(link)
    author = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'letter-contact'))
    )
    author = author.get_attribute('title')
    date = int_value_from_ru_month(driver.find_element_by_class_name('letter__date').text)
    date = datetime.strptime(date, "%d %m %Y, %H:%M")
    subject = driver.find_element_by_tag_name('h2').text
    text = driver.find_element_by_class_name('letter__body').text
    collection.insert_one({'author': author, 'date': date, 'subject': subject, 'text': text})

driver.quit()
