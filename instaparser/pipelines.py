# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class InstaparserPipeline:

    # def __init__(self):
    #     db = MongoClient('localhost', 27017)
    #     self.db = db.instagram_user_parse


    def process_item(self, item, spider):
        print()
        return item
