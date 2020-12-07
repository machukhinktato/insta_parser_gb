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
    insta_login_link = 'https://www.instagram.com/login/ajax/'
    insta_login = LOGIN
    insta_pass = PASS
    parse_user = 'ai_machine_ learning'
    graphql_url = 'https://www.instagram.com/qraphql/query/?'
    posts_hash = 'eddbde960fed6bde675388aac39a3657'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.insta_login_link,
            method='POST',
            callback=self.auth,
            formdata={
                'username': self.insta_login,
                'enc_password': '#PWD_INSTAGRAM_BROWSER:10:1607363859:AXZQAKe4+LkKk5ihE5V9+LJiHaZiyhb/VnrzSA+XYSaXsHoDEvoUiOQlbLP5Za2zRHrGvf1cV3JNFU0TfgylqiCCsAjmFBHwgA9Jn/3fSxJmeqN8njZY38TtptDxtA6ETcKpB+2jXOqTFHRTO/Xjcg==',
            },
            headers={'x-csrftoken': csrf}
        )

        def auth(self, response: HtmlResponse):
            print()

        def fetch_csrf_token(self, text):
            matched = re.search('\"csrf-token\":\"\\w+\"', text).group()
            return matched.split(':').pop().replace(r'"', '')
