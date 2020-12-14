import scrapy
import re
import json
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
from urllib.parse import urlencode
from copy import deepcopy
from scrapy.loader import ItemLoader
from instaparser.items import InstaparserItem
from .VARIABLES import *


class InstaspiderSpider(scrapy.Spider):
    name = 'instaspider'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    insta_login = LOGIN
    insta_pass = PASS
    # fst_parse_user = 'ai_machine_learning'
    fst_parse_user = 'maxim_spiryakin'
    scd_parse_user = 'n_delya'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    query_hash_posts = '003056d32c2554def87228bc3fd9668a'
    query_hash_followers = 'c76146de99bb02f6415203be841dd25a'
    query_hash_following = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.insta_login_link,
            method='POST',
            callback=self.auth,
            formdata={
                'username': self.insta_login,
                'enc_password': self.insta_pass
            },
            headers={'X-CSRFToken': csrf}
        )

    def auth(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            yield response.follow(
                f'/{self.fst_parse_user}',
                callback=self.user_data_parse,
                cb_kwargs={'username': self.fst_parse_user}
            )
            yield response.follow(
                f'/{self.scd_parse_user}',
                callback=self.user_data_parse,
                cb_kwargs={'username': self.scd_parse_user}
            )

    def fetch_csrf_token(self, data):
        matched = re.search('\"csrf_token\":\"\\w+\"', data).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def user_data_parse(self, response: HtmlResponse, username):
        print()
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            'id': user_id,
            'first': 12,
        }

        url_posts = f'{self.graphql_url}query_hash={self.query_hash_posts}&{urlencode(variables)}'
        url_followers = f'{self.graphql_url}query_hash={self.query_hash_followers}&{urlencode(variables)}'
        url_following = f'{self.graphql_url}query_hash={self.query_hash_following}&{urlencode(variables)}'

        yield response.follow(
            url_posts,
            callback=self.posts_parse,
            cb_kwargs={
                'username': username,
                'user_id': user_id,
                'variables': deepcopy(variables)
            }
        )

        yield response.follow(
            url_followers,
            callback=self.posts_parse,
            cb_kwargs={
                'username': username,
                'user_id': user_id,
                'variables': deepcopy(variables)
            }
        )

        yield response.follow(
            url_following,
            callback=self.posts_parse,
            cb_kwargs={
                'username': username,
                'user_id': user_id,
                'variables': deepcopy(variables)
            }
        )

    def posts_parse(self, response: HtmlResponse, username, user_id, variables):
        print()
        if self.query_hash_posts in response.url:
            j_data = response.json()
            page_info = j_data.get('data').get('user').get(
                'edge_owner_to_timeline_media'
            ).get('page_info')
            if page_info.get('has_next_page'):
                variables['after'] = page_info.get('end_cursor')

                url_posts = f'{self.graphql_url}query_hash={self.query_hash_posts}&{urlencode(variables)}'

                yield response.follow(
                    url_posts,
                    callback=self.posts_parse,
                    cb_kwargs={
                        'username': username,
                        'user_id': user_id,
                        'variables': deepcopy(variables)
                    }
                )

        if self.query_hash_followers in response.url:



        posts = j_data.get('data').get('user').get(
            'edge_owner_to_timeline_media').get('edges')



        for post in posts:
            item = InstaparserItem(
                user_id=user_id,
                username=username,
                photo=post['node']['display_url'],
                # post_data=post['node']
            )
            yield item
