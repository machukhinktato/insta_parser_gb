# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
import os

from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from urllib.parse import urlparse


class InstaparserPipeline:

    # def __init__(self):
    #     db = MongoClient('localhost', 27017)
    #     self.db = db.instagram_user_parse

    def process_item(self, item, spider):
        print()
        return item


class InstaPhotoPipline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            for img in item['photo']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

        return item

    def item_completed(self, results, item, info):
        print()
        if results:
            item['photo'] = [itm[1] for itm in results if itm[0]]

        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return str((item['name'])) + '/' + os.path.basename(urlparse(request.url).path)
