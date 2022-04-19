#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os.path

try:
    from crawler import *
    from spider_header import *
except Exception:
    from crawler.spiders.crawler import *
    from crawler.spiders.spider_header import *


class ResidentCoordinateSpider(Crawler):
    name = 'resident-coordinate-spider'
    allowed_domains = ['lbs.amap.com']
    start_urls = ['https://lbs.amap.com/tools/picker']

    def __init__(self):
        super().__init__(CrawlerTrait.VOICING)
        self._load_resident_address_list_()
        self.add_task('//input[@id="txtSearch"]', self._query_coordinate_)

    def _load_resident_address_list_(self):
        self.addresses = []
        for filepath in list_files(RESIDENT_INPUT_DIR):
            with open(filepath, 'r') as fd:
                resident = json.load(fd)
                for district in resident['districts']:
                    for resident in district['residents']:
                        self.addresses.append(resident)

    def _query_coordinate_(self, response, documents):
        logger.debug(f'query_coordinate: {documents}')
        coordinate_mapping = {}
        if os.path.exists(RESIDENT_COORDINATE_FILE):
            with open(RESIDENT_COORDINATE_FILE, 'r') as fd:
                coordinate_mapping = json.load(fd)
        max_requests = -1
        for i, address in enumerate(self.addresses):
            if max_requests != -1 and i > max_requests:
                break
            if address in coordinate_mapping:
                continue
            try:
                documents.clear()
                documents.send_keys(f'上海市{address}')
                search_btn = self.driver.query(response, '//a[@title="搜索"]')
                search_btn.click()
                coordinate_input = self.driver.query(response, '//input[@id="txtCoordinate"]')
                coordinate = coordinate_input.get_attribute('value')
                logger.debug(f'{address}: {coordinate}')
                coordinate_mapping[address] = coordinate
                # time.sleep(1)
            except Exception as e:
                logger.debug(f'query {address} error: {e}')

        with open(RESIDENT_COORDINATE_FILE, 'w+', encoding='utf8') as fd:
            json.dump(coordinate_mapping, fd, ensure_ascii=False, cls=ObjectEncoder, indent=2)


class ResidentCoordinateSpiderUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    # @UnitTests.skip
    def crawl_detail_page_test(self):
        process = CrawlerProcess()
        process.crawl(ResidentCoordinateSpider)
        process.start()
        web_driver_service.stop()

    @UnitTests.skip
    def load_resident_address_list_test(self):
        class MockResidentCoordinateSpider(ResidentCoordinateSpider):
            def __init__(self):
                pass

        spider = MockResidentCoordinateSpider()
        spider._load_resident_address_list_()
        assert len(spider.addresses) > 0
        logger.debug(spider.addresses)


ResidentCoordinateSpiderUnitTests().run()
