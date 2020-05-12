""" Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл."""

import requests
import json
import datetime

V = 5.103
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/81.0.4044.129 Safari/537.36'}
CLIENT_ID = 7462021
CLIENT_SECRET = '7XFPrMAZsrL3alpNvh6p'

# вопрос: в процессе авторизвции надо уопировать код или токен из адресной строки. Это можно автоматизировать?
# Я так и не придумала как.

class VkAuthorize:
    def __init__(self):
        self.oauth_link = 'https://oauth.vk.com/'
        self.redirect_uri = 'https://oauth.vk.com/blank.html'
        self.display = 'page'
        self.params = None
        self.response = None
        self.code = None
        self.access_token = None

    def get_code(self, scope='wall,friends'):
        self.params = {'client_id': CLIENT_ID,
                       'display': self.display,
                       'redirect_uri': self.redirect_uri,
                       'scope': scope,
                       'response_type': 'code',
                       'v': V}
        self.response = requests.get(f'{self.oauth_link}authorize', params=self.params, headers=HEADER)
        return print(self.response.url)

    def get_token(self, scope='wall,friends,offline'):
        self.get_code()
        self.code = input('Перейдите по ссылке, авторизуйтесь и введите код (из адресной строки): ')
        self.params = {'client_id': CLIENT_ID,
                       'display': self.display,
                       'redirect_uri': self.redirect_uri,
                       'scope': scope,
                       'v': V,
                       'client_secret': CLIENT_SECRET,
                       'code': self.code}
        self.response = requests.get(f'{self.oauth_link}access_token', params=self.params, headers=HEADER)
        if self.response.ok:
            with open(f'response_token.json', 'w') as f:
                json.dump(self.response.json(), f)
            self.access_token = json.loads(self.response.text)['access_token']
            return self.access_token
        else:
            return None


try:
    with open(f'response_token.json', 'r') as f:
        access_token = json.load(f)['access_token']
except Exception as e:
    print(e)
    auth = VkAuthorize()
    access_token = auth.get_token()

url = 'https://api.vk.com/method/wall.get'
params = {'access_token': access_token,
          'v': V,
          'domain': 'biz_motiv',
          'extended': 1}

response = requests.get(url, params=params, headers=HEADER)


def print_posts(response):
    items = response.json()['response']['items']
    for p in items:
        if p['text']:
            print(datetime.datetime.fromtimestamp(p['date']), '\n', p['text'], '\n')


if response.ok:
    print_posts(response)
else:
    auth = VkAuthorize()
    access_token = auth.get_token()
    response = requests.get(url, params=params, headers=HEADER)
    print_posts(response)
