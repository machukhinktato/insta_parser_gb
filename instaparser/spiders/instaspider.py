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
    start_urls = ['http://instagram.com/']
    insta_login = LOGIN
    insta_psw = PASS
    insta_login_link = 'https://www.instagram.com/login/ajax/'
    parse_user = 'ai_machine_ learning'
    graphql_url = 'https://www.instagram.com/qraphql/query/?'
    posts_hash = 'eddbde960fed6bde675388aac39a3657'

    def parse(self, response):
        pass
