# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class AcademicNewsItem(Item):
    # define the fields for your item here like:
    title = Field()
    time_pub = Field()
    time_get = Field()
    author = Field()
    publisher = Field()
    source = Field()
    classf = Field()
    body = Field()
    url = Field()     # 用来实现增量式爬虫
