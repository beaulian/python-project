# -*- coding: utf-8 -*-

from scrapy.item import Item, Field


class NewsItem(Item):
    title = Field()
    time_pub = Field()
    time_get = Field()
    author = Field()
    publisher = Field()
    source = Field()
    source_name = Field()
    classf = Field()
    body = Field()
    url = Field()     # 用来实现增量式爬虫




