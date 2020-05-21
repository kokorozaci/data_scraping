"""
1) Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и
реализовать функцию, записывающую собранные вакансии в созданную БД
3*)Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта
"""

from pymongo import MongoClient
import argparse
from bs_hh_sjob import VacancyScraper as vs

client = MongoClient('localhost', 27017)

db = client['vacancy']

hh = db.hh
sj = db.sj

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--vacancy", type=str)
parser.add_argument("-p", "--page", type=str)
args = parser.parse_args()
if args.vacancy:
    vacancy = args.vacancy
    page = int(args.page)
else:
    vacancy = input('Введите запрос для поиска вакансий: ')
    page = int(input('Введите число страниц для отображения (все: -1): '))

data = vs.get_vacancy(vacancy, page)


def insert_new(data):
    for dat in data:
        if dat['source'] == 'superjob.ru' and not sj.find_one({"_id": dat['_id']}):
            sj.insert_one(dat)
        elif dat['source'] == 'hh.ru' and not hh.find_one({"_id": dat['_id']}):
            hh.insert_one(dat)


def insert_or_update(data, verbose=False):
    for dat in data:
        if dat['source'] == 'superjob.ru':
            try:
                sj.insert_one(dat)
            except Exception as e:
                if verbose:
                    print(e)
                sj.update_one({'_id': dat['_id']}, {'$set': dat})
        if dat['source'] == 'superjob.ru':
            try:
                hh.insert_one(dat)
            except Exception as e:
                if verbose:
                    print(e)
                hh.update_one({'_id': dat['_id']}, {'$set': dat})

insert_or_update(data)
print(len(list(hh.find({}))))
