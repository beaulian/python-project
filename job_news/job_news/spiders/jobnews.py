# coding=utf-8

import datetime
from scrapy.contrib.spiders import Rule, CrawlSpider
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader
from scrapy.selector import Selector
from ..items import JobNewsItem


class NewsSpider(CrawlSpider):
    name = "jobnews"
    allowed_domains = ["job.cqu.edu.cn"]
    start_urls = ["http://job.cqu.edu.cn/jyxt/zczphxxlistlogin.do"]

    rules = (
        Rule(LinkExtractor(allow='zczphxxlogin.do\?pkValue=\d+'), callback="parse_page", follow=False),
    )

    def parse_page(self, response):
        hxs = Selector(response)
        time = hxs.xpath("//table/tr/td[@align='left']/text()").extract()[0].strip()
        el = ItemLoader(item=JobNewsItem(), response=response)
        el.add_xpath('source', "//p[@class='jyzd_qymc qymc_bg']/text()")
        el.add_xpath('industry', "//div[@style='float: left']/text()")
        el.add_xpath('scale', "//div[@style='float: left']/text()")
        el.add_value('recruit_time', self.handle(time))
        el.add_xpath('recruit_addr', "//table/tr/td[@align='left']/text()")
        el.add_xpath('note', "//table/tr/td[@align='left']/text()")
        el.add_xpath('recruit_explain', "//table/tr/td[@align='left']")
        el.add_xpath('introduction', '//div[@style="width: 100%;margin-left: 10px;margin-right: 10px "]')
        el.add_value('url', response.url)

        return el.load_item()

    def handle(self, time):
        first = filter(lambda x: x.isdigit() or x == "-", time)
        second = first[:10]
        return second

