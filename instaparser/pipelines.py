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

    def __init__(self):
        db = MongoClient('localhost', 27017)
        self.db = db.instagram_parsing

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        try:
            item['_id'] = collection.count_documents({}) + 1
        except:
            item['_id'] = 0
        collection.insert_one(item)

        return item


class InstaPhotoPipline(ImagesPipeline):
    def get_media_requests(self, item, info):
        print()
        if item['photo']:
            for img in item['photo']:
                print()
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

        return item

    def item_completed(self, results, item, info):
        if results:
            item['photo'] = [itm[1] for itm in results if itm[0]]

        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return str(item['username'][0]) + '/' + os.path.basename(urlparse(request.url).path)
