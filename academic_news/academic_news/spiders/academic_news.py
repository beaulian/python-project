# coding=utf-8

import datetime
from scrapy.contrib.spiders import Rule, CrawlSpider
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader
from ..items import AcademicNewsItem


class NewsSpider(CrawlSpider):
    name = "academicnews"
    allowed_domains = ["news.cqu.edu.cn"]
    start_urls = ["http://news.cqu.edu.cn/news/article/list.php?catid=47"]

    rules = (
        Rule(LinkExtractor(allow='\/article\/article_\d+\.html'), callback="parse_page", follow=False),
        Rule(LinkExtractor(allow='\/article\/show\.php\?itemid=\d+'), callback="parse_page", follow=False),
    )

    def parse_page(self, response):
        el = ItemLoader(item=AcademicNewsItem(), response=response)
        el.add_xpath('title', "//div[@class='title']/h1/text()")
        el.add_xpath('time_pub', "//span[@class='datetime']/text()")
        el.add_value('time_get', datetime.datetime.today().__format__("%Y-%m-%d %H:%M:%S"))
        el.add_xpath('author', "//div[@class='clear author']/text()")
        el.add_xpath('publisher', "//div[@class='clear author']/a[@target='_blank']/text()")
        el.add_xpath('source', "//div[@class='clear author']/a[@target='_blank']/text()")
        el.add_xpath('classf', "//div[@id='location']/a/text()")
        # soup = BeautifulSoup(response.body)
        el.add_xpath('body', "//div[@id='zoom']")
        el.add_value('url', response.url)
        return el.load_item()
