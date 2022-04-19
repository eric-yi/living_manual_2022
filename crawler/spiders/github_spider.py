#!/usr/bin/env python
# -*- coding:utf-8 -*-

try:
    from crawler import *
    from spider_header import *
except Exception:
    from crawler.spiders.crawler import *
    from crawler.spiders.spider_header import *


class GithubSpider(Crawler):
    name = 'github-spider'
    allowed_domains = ['www.github.com']
    start_urls = ['https://www.github.com/search?p=1&q=crawler&type=Repositories']

    def __init__(self):
        super().__init__(CrawlerTrait.VOICING)
        style_class = 'd-flex flex-column flex-md-row flex-justify-between border-bottom pb-3 position-relative'
        self.add_task(f'//div[@class="{style_class}"]', self._crawl_repository_amount_)

    def _crawl_repository_amount_(self, response, result):
        logger.debug(f'crawl_repository_amount: {result.text}')
        matcher = CrawlerMatcher(result.text, Matcher.IntegerMatcher)
        logger.debug(color_line(f'crawler repositories total {matcher.match()}', offset=4))


class GithubSpiderUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    # @UnitTests.skip
    def crawl_detail_page_test(self):
        process = CrawlerProcess()
        process.crawl(GithubSpider)
        process.start()
        web_driver_service.stop()


GithubSpiderUnitTests().run()
