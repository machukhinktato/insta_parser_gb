import scrapy
import re
import json
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
from urllib.parse import urlencode
from copy import deepcopy

class InstaspiderSpider(scrapy.Spider):
    name = 'instaspider'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']

    def parse(self, response):
        pass
