# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class JobNewsPipeline(object):
    def __init__(self, mongo_uri, mongo_port, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db
        self.collection_name = "JobNewsItem"

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
        item["source"] = item["source"][0]
        item["industry"] = item["industry"][1].encode("utf-8").split("\xef\xbc\x9a")[1]
        item["scale"] = item["scale"][2].encode("utf-8").split("\xef\xbc\x9a")[1].strip()
        item["recruit_time"] = item["recruit_time"][0]
        item["recruit_addr"] = item["recruit_addr"][1].strip()
        item["note"] = item["note"][2].strip()
        item["recruit_explain"] = item["recruit_explain"][3][20:-6]
        item["introduction"] = item["introduction"][0]
        item['url'] = item['url'][0]
        try:
            self.db[self.collection_name].insert(dict(item))
        except DuplicateKeyError:
            print "skip %s" % item['url']

        return item
