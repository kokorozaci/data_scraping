"""
2) Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введенной суммы
"""

from pymongo import MongoClient
import argparse

client = MongoClient('localhost', 27017)

db = client['vacancy']

hh = db.hh
sj = db.sj

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--salary", type=str)
args = parser.parse_args()
if args.salary:
    salary = int(args.salary)
else:
    salary = int(input('Введите мин з/п: '))


def search_salary(salary):

    for i in hh.find({'$or': [{'salary_min': {'$gte': salary}}, {'salary_max': {'$gte': salary}}]},
                     {'name': 1, 'salary_min': 1, 'salary_max': 1, 'currency': 1, '_id': 0}):

        print(f"{i['name']}: {i['salary_min'] if i['salary_min'] else ''} - "
              f"{i['salary_max'] if i['salary_max'] else ''} "
              f"{i['currency']}")

    for i in sj.find({'$or': [{'salary_min': {'$gte': salary}}, {'salary_max': {'$gte': salary}}]},
                     {'name': 1, 'salary_min': 1, 'salary_max': 1, 'currency': 1, '_id': 0}):

        print(f"{i['name']}: {i['salary_min'] if i['salary_min'] else ''} - "
              f"{i['salary_max'] if i['salary_max'] else ''} "
              f"{i['currency']}")


search_salary(salary)