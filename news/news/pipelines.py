# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class NewsPipeline(object):
    def __init__(self, mongo_uri, mongo_port, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db
        self.collection_name = "NewsItem"

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_port=crawler.settings.get("MONGO_PORT"),
            mongo_db=crawler.settings.get("MONGO_DB")
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri, self.mongo_port)
        self.db = self.client[self.mongo_db]
        self.db[self.collection_name].ensure_index('url', unique=True)    # 设置url为唯一索引,从而实现增量式爬虫

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item['title'] = item['title'][0]
        item['time_pub'] = item['time_pub'][0].split(" ")[0]
        item['time_get'] = item['time_get'][0]
        item['author'] = item['author'][0].split("\r\n")[1][3:]
        item['publisher'] = item['publisher'][0]
        item['source'] = item['source'][1]
        item['classf'] = item['classf'][1]
        item['body'] = item['body'][0]
        item['url'] = item['url'][0]
        try:
            self.db[self.collection_name].insert(dict(item))
        except DuplicateKeyError:
            print "skip %s" % item['url']

        return item
