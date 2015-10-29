# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class JobNewsItem(Item):
    source = Field()
    industry = Field()
    scale = Field()
    recruit_time = Field()
    recruit_addr = Field()
    note = Field()
    recruit_explain = Field()
    introduction = Field()
    url = Field()
