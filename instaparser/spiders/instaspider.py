import scrapy
import re
import json
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
from urllib.parse import urlencode
from copy import deepcopy
from .VARIABLES import *


class InstaspiderSpider(scrapy.Spider):
    name = 'instaspider'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    insta_login = LOGIN
    insta_pass = PASS
    parse_user = 'ai_machine_ learning'
    graphql_url = 'https://www.instagram.com/qraphql/query/?'
    posts_hash = 'eddbde960fed6bde675388aac39a3657'

    def parse(self, response:HtmlResponse):
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
                f'/{self.parse_user}',
                callback=self.user_data_parse,
            )
        print()


    def fetch_csrf_token(self, data):
        matched = re.search('\"csrf_token\":\"\\w+\"', data).group()
        return matched.split(':').pop().replace(r'"', '')


    def user_data_parse(self, response:HtmlResponse):
        pass