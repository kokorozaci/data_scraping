# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = ''
    insta_pass = ''
    inst_login_link = 'https://instagram.com/accounts/login/ajax/'

    hash_posts = '7c8a1055f69ff97dc201e752cf6f0093'
    hash_post = '552bb33f4e58c7805d13d4f95da7d3a1'
    hash_followers = 'c76146de99bb02f6415203be841dd25a'
    hash_follows = 'd04b0a864b4b54837c0d870b0e77e076'
    graphql_url = 'https://www.instagram.com/graphql/query/?'

    def __init__(self, users):
        self.users_list = users

    def parse(self, response):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.parse_user,
            formdata={'username': self.insta_login,
                      'enc_password': self.insta_pass},
            headers={'X-CSRFToken': csrf_token}
        )

        pass

    def parse_user(self, response):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.users_list:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'user': user}
                )

    def user_data_parse(self, response: HtmlResponse, user):
        # ответ распарсила более подробно,
        # чтобы добавлять в базу подписки и подписчиков в едином формате (потом удобнее в SQL переводить будет)
        # '_id' формируется как follow_follower id
        user_info = response.xpath("//script[contains(text(), 'csrf_token')]/text()") \
            .extract_first().replace("window._sharedData = ", '').replace(";", '')
        user_info = json.loads(user_info).get('entry_data', {}) \
            .get('ProfilePage', {})[0] \
            .get('graphql', {}) \
            .get('user', {})
        # get с {} тут используется т.к. ,без них вернётся None, и цепочка get выдаст ошибку
        info = {
            'user': user,
            'user_id': user_info.get('id'),
            'pic_url': user_info.get('profile_pic_url'),
            'is_private': user_info.get('is_private'),
            'full_name': user_info.get('full_name')
        }
        variables = {"id": info['user_id'],
                     "first": 50
                     }
        url_followers = f'{self.graphql_url}query_hash={self.hash_followers}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.followers_parse,
            cb_kwargs={'info': info,
                       'variables': deepcopy(variables)}
        )
        url_follows = f'{self.graphql_url}query_hash={self.hash_follows}&{urlencode(variables)}'
        yield response.follow(
            url_follows,
            callback=self.follows_parse,
            cb_kwargs={'info': info,
                       'variables': deepcopy(variables)}
        )

    def followers_parse(self, response, info, variables):
        j_body = json.loads(response.text)
        page_info = j_body.get('data', {}).get('user', {}).get('edge_followed_by', {}).get('page_info', {})
        followers = j_body.get('data', {}).get('user', {}).get('edge_followed_by', {}).get('edges', {})
        for follower in followers:
            item = InstaparserItem(
                _id=f"{info['user_id']}_{follower['node']['id']}",
                follow_id=info['user_id'],
                follow_name=info['user'],
                follow_full_name=info['is_private'],
                follow_pic_url=info['pic_url'],
                follow_is_private=info['full_name'],
                follower_id=follower['node']['id'],
                follower_name=follower['node']['username'],
                follower_full_name=follower['node']['full_name'],
                follower_pic_url=follower['node']['profile_pic_url'],
                follower_is_private=follower['node']['is_private']
            )

            yield item

        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']

            url_posts = f'{self.graphql_url}query_hash={self.hash_followers}&{urlencode(variables)}'

            yield response.follow(
                url_posts,
                callback=self.followers_parse,
                cb_kwargs={'info': info,
                           'variables': deepcopy(variables)}
            )

    def follows_parse(self, response, info, variables):
        j_body = json.loads(response.text)
        page_info = j_body.get('data', {}).get('user', {}).get('edge_follow', {}).get('page_info', {})
        follows = j_body.get('data', {}).get('user', {}).get('edge_follow', {}).get('edges', {})
        for foll in follows:
            item = InstaparserItem(
                _id=f"{foll['node']['id']}_{info['user_id']}",
                follower_id=info['user_id'],
                follower_name=info['user'],
                follower_full_name=info['is_private'],
                follower_pic_url=info['pic_url'],
                follower_is_private=info['full_name'],
                follow_id=foll['node']['id'],
                follow_name=foll['node']['username'],
                follow_full_name=foll['node']['full_name'],
                follow_pic_url=foll['node']['profile_pic_url'],
                follow_is_private=foll['node']['is_private']
            )
            yield item
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']

            url_posts = f'{self.graphql_url}query_hash={self.hash_follows}&{urlencode(variables)}'

            yield response.follow(
                url_posts,
                callback=self.follows_parse,
                cb_kwargs={'info': info,
                           'variables': deepcopy(variables)}
            )

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
