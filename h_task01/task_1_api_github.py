""" Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json"""

import requests
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--user", type=str)
args = parser.parse_args()

main_link = 'https://api.github.com/graphql'
token = '44258d592d3574ced48a7500f6cf057b3f3cbf10'  # public access
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/81.0.4044.129 Safari/537.36',
          'Authorization': f'bearer {token}'}

if args.user:
    user_name = args.user  # через консоль
else:
    user_name = input('Введите имя пользователя на GitHub: ')  # из файла

query = {'query': f'query {{user (login: "{user_name}") {{repositories (last: 100, orderBy: '
                  f'{{field: CREATED_AT, direction: DESC}}) {{edges {{node {{name}}}}}}}}}}'}

response = requests.post(main_link, json=query, headers=header)
if response.ok:
    data = json.loads(response.text)
    with open(f'response_{user_name}.json', 'w') as f:
        json.dump(data, f)
    print(f'Репозитории пользователя {user_name} на GitHub:')
    for node in data['data']['user']['repositories']['edges']:
        print('- ', node['node']['name'])
else:
    print(f'Что-то пошло не так {response.status_code}')
