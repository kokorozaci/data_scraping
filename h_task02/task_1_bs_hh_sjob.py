"""1) Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайта
superjob.ru и hh.ru. Приложение должно анализировать несколько страниц сайта(также вводим через input или аргументы).
Получившийся список должен содержать в себе минимум:
*Наименование вакансии
*Предлагаемую зарплату (отдельно мин. отдельно макс. и отдельно валюту)
*Ссылку на саму вакансию
*Сайт откуда собрана вакансия
По своему желанию можно добавить еще работодателя и расположение. Данная структура должна быть одинаковая для вакансий
с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas."""

import argparse
from bs4 import BeautifulSoup as bs
import requests
from time import sleep
from pprint import pprint
import re
import pandas as pd
from pandas.io.json import json_normalize


class VacancyScraper:
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/81.0.4044.129 Safari/537.36',
              'Accept': '*/*'}
    link_hh = 'https://hh.ru'
    link_superjob = 'https://russia.superjob.ru'

    @staticmethod
    def parse_salary(text):
        text_list = text.split()
        if 'договор' in text:
            return None, None, None
        elif 'от' in text:
            sal = ''.join(re.findall('\d*', ''.join(text_list)))
            izm = [i for i in re.findall('\D*', ' '.join(text_list[1:])) if len(i) > 1][0]
            return int(sal), None, izm[1:]
        elif 'до' in text:
            sal = ''.join(re.findall('\d*', ''.join(text_list)))
            izm = [i for i in re.findall('\D*', ' '.join(text_list[1:])) if len(i) > 1][0]
            return None, int(sal), izm[1:]
        elif '-' in text:
            text = ''.join(text_list).split('-')
            sal_min = text[0]
            sal_max = [i for i in re.findall('\d*', text[1]) if len(i) > 0][0]
            text = ' '.join(text_list).split('-')
            izm = [i for i in re.findall('\D*', text[1]) if len(i) > 1][0]
            return int(sal_min), int(sal_max), izm[1:]
        elif '—' in text:
            text = ''.join(text_list).split('—')
            sal_min = text[0]
            sal_max = [i for i in re.findall('\d*', text[1]) if len(i) > 0][0]
            text = ' '.join(text_list).split('—')
            izm = [i for i in re.findall('\D*', text[1]) if len(i) > 1][0]
            return int(sal_min), int(sal_max), izm[1:]
        else:
            return None, None, None

    @classmethod
    def request_hh(cls, params):
        request = requests.get(cls.link_hh + '/search/vacancy', params=params, headers=cls.header).text
        soup = bs(request, 'lxml')
        has_next_page = soup.find('a', {'data-qa': 'pager-next'})
        vacancy_block = soup.find('div', {'class': 'vacancy-serp'})
        return vacancy_block, has_next_page

    @classmethod
    def request_superjob(cls, params):
        request = requests.get(cls.link_superjob + '/vacancy/search/', params=params, headers=cls.header).text
        soup = bs(request, 'lxml')
        page_block = soup.find('div', {'class': 'L1p51'})
        if page_block:
            has_next_page = page_block.find(text='Дальше')
        else:
            has_next_page = None
        vacancy_block = soup.find_all('div', {'class': 'iJCa5 _2gFpt _1znz6 _2nteL'})
        return vacancy_block, has_next_page

    @classmethod
    def parse_hh(cls, text, page):
        params = {'page': page,
                  'text': text}
        vacancy_block, has_next = cls.request_hh(params)
        vacancy_list = []
        for vacancy in vacancy_block.findChildren(recursive=False):
            vacancy_data = {}
            name = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
            if name:
                vacancy_data['name'] = name.getText()
            else:
                continue
            salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            if salary:
                vacancy_data['salary_min'], vacancy_data['salary_max'], vacancy_data['currency'] = \
                    cls.parse_salary(salary.getText())
            else:
                vacancy_data['salary_min'], vacancy_data['salary_max'], vacancy_data['currency'] = None, None, None

            link = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']
            vacancy_data['link'] = link[:link.index('?')]
            vacancy_data['source'] = 'hh.ru'
            employer = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
            if employer:
                vacancy_data['employer'] = employer.getText()
            address = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-address'})
            if address:
                vacancy_data['address'] = address.getText()
            vacancy_list.append(vacancy_data)
        return vacancy_list, has_next

    @classmethod
    def parse_superjob(cls, text, page):
        params = {'page': page,
                  'keywords': text}
        vacancy_block, has_next = cls.request_superjob(params)
        vacancy_list = []
        for vacancy in vacancy_block:
            vacancy_data = {}
            name = vacancy.find('a', {'class': '_1UJAN'})
            if name:
                vacancy_data['name'] = name.getText()
            else:
                continue
            salary = vacancy.find('span', {'class': '_2VHxz'})
            if salary:
                vacancy_data['salary_min'], vacancy_data['salary_max'], vacancy_data['currency'] = \
                    cls.parse_salary(salary.getText())
            else:
                vacancy_data['salary_min'], vacancy_data['salary_max'], vacancy_data['currency'] = None, None, None

            vacancy_data['link'] = cls.link_superjob + vacancy.find('a', {'class': '_1UJAN'})['href']
            vacancy_data['source'] = 'superjob.ru'
            employer = vacancy.find('a', {'class': '_25-u7'})
            if employer:
                vacancy_data['employer'] = employer.getText()
            address = vacancy.find('span', {'class': 'clLH5'}).find_next_sibling()
            if address:
                vacancy_data['address'] = address.getText()
            vacancy_list.append(vacancy_data)
        return vacancy_list, has_next

    @classmethod
    def get_vacancy(cls, text, page):
        i = 0
        vacancy, next_page = cls.parse_hh(text, i)
        all = vacancy
        while next_page and (i+1) != page:
            i += 1
            vacancy, next_page = cls.parse_hh(text, i)
            all.extend(vacancy)
            sleep(0.1 if i % 10 != 0 else 2)

        i = 1
        vacancy, next_page = cls.parse_superjob(text, i)
        all.extend(vacancy)
        while next_page and i != page:
            i += 1
            vacancy, next_page = cls.parse_superjob(text, i)
            all.extend(vacancy)
            sleep(0.1 if i % 10 != 0 else 2)

        return all


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vacancy", type=str)
    parser.add_argument("-p", "--page", type=str)
    args = parser.parse_args()
    if args.vacancy:
        vacancy = args.vacancy
        page = args.page
    else:
        vacancy = input('Введите запрос для поиска вакансий: ')
        page = input('Введите число страниц зля отображения (все: -1): ')
    data = VacancyScraper.get_vacancy(vacancy, page)
    pprint(data[-5:])  # не все строки, для наглядноси
    df = json_normalize(data)  # не очень красиво получается распечатывать
    pd.set_option('display.max_columns', None)
    print(df.head())
    print(f'Всего вакансий: {len(data)}')
