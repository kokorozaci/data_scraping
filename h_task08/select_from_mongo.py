"""
4) Написать запрос к базе, который вернет список подписчиков указанного пользователя
5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
"""


from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)

db = client['instagram']

user_name = input('Введите имя пользователя: ')
inst = db.instagram
i = 0
for user in inst.find({'follower_name': user_name}, {'follow_full_name': 1,
                                                     'follow_id': 1,
                                                     'follow_name': 1,
                                                     'follow_pic_url': 1,
                                                     '_id': 0}):
    i += 1
    pprint(user)
print(i)

i = 0
for user in inst.find({'follow_name': user_name}, {'follower_full_name': 1,
                                                   'follower_id': 1,
                                                   'follower_name': 1,
                                                   'follower_pic_url': 1,
                                                   '_id': 0}):
    i += 1
    pprint(user)
print(i)