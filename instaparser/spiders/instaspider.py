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
            'first': 1,
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
            posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')

        if self.query_hash_followers in response.url:
            print()
            j_data = response.json()
            page_info = j_data.get('data').get('user').get(
                'edge_followed_by'
            ).get('page_info')
            if page_info.get('has_next_page'):
                variables['after'] = page_info.get('end_cursor')
                url_followers = f'{self.graphql_url}query_hash={self.query_hash_followers}&{urlencode(variables)}'
                yield response.follow(
                    url_followers,
                    callback=self.posts_parse,
                    cb_kwargs={
                        'username': username,
                        'user_id': user_id,
                        'variables': deepcopy(variables)
                    }
                )
            followers = j_data.get('data').get('user').get('edge_followed_by').get('edges')

        if self.query_hash_following in response.url:
            print()
            j_data = response.json()
            page_info = j_data.get('data').get('user').get(
                'edge_follow'
            ).get('page_info')
            if page_info.get('has_next_page'):
                variables['after'] = page_info.get('end_cursor')
                url_following = f'{self.graphql_url}query_hash={self.query_hash_following}&{urlencode(variables)}'
                yield response.follow(
                    url_following,
                    callback=self.posts_parse,
                    cb_kwargs={
                        'username': username,
                        'user_id': user_id,
                        'variables': deepcopy(variables)
                    }
                )

            following = j_data.get('data').get('user').get('edge_follow').get('edges')

        loader = ItemLoader(item=InstaparserItem(), response=response)

        if self.query_hash_posts in response.url:
            for post in posts:
                loader.add_value('user_id', user_id)
                loader.add_value('username', username)
                loader.add_value('photo', post['node']['display_url'])
                loader.add_value('data', 'user')
                loader.add_value('url', self.start_urls[0] + 'p/' + post['node']['shortcode'])
                yield loader.load_item()

        if self.query_hash_followers in response.url:
            for follower in followers:
                loader.add_value('user_id', follower['node']['id'])
                loader.add_value('username', follower['node']['username'])
                loader.add_value('photo', follower['node']['profile_pic_url'])
                loader.add_value('data', 'follower')
                loader.add_value('url', self.start_urls[0] + follower['node']['username'])
                yield loader.load_item()

        if self.query_hash_following in response.url:
            for follow in following:
                loader.add_value('user_id', follow['node']['id'])
                loader.add_value('username', follow['node']['username'])
                loader.add_value('photo', follow['node']['profile_pic_url'])
                loader.add_value('data', 'follow')
                loader.add_value('url', self.start_urls[0] + follow['node']['username'])
                yield loader.load_item()
