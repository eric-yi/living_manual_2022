#!/usr/bin/env python
# -*- coding:utf-8 -*-

try:
    from crawler import *
    from spider_header import *
except Exception:
    from crawler.spiders.crawler import *
    from crawler.spiders.spider_header import *


class AmapPickerSpider(Crawler):
    name = 'amap-picker-spider'
    allowed_domains = ['lbs.amap.com']
    start_urls = ['https://lbs.amap.com/tools/picker']

    def __init__(self):
        super().__init__(CrawlerTrait.VOICING)
        self.add_task('//input[@id="txtSearch"]', self._query_coordinate_)

    def _query_coordinate_(self, response, documents):
        logger.debug(f'query_coordinate: {documents}')
        documents.send_keys('上海市博山路12弄')
        search_btn = self.driver.query(response, '//a[@title="搜索"]')
        search_btn.click()
        coordinate_input = self.driver.query(response, '//input[@id="txtCoordinate"]')
        coordinate = coordinate_input.get_attribute('value')
        logger.debug(f'上海市博山路12弄: {coordinate}')


class AmapPickerSpiderUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    # @UnitTests.skip
    def crawl_detail_page_test(self):
        process = CrawlerProcess()
        process.crawl(AmapPickerSpider)
        process.start()
        time.sleep(5)
        web_driver_service.stop()


AmapPickerSpiderUnitTests().run()
