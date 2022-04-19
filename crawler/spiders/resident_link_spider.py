#!/usr/bin/env python
# -*- coding:utf-8 -*-

from living_map_db import *

try:
    from crawler import *
    from spider_header import *
except Exception:
    from crawler.spiders.crawler import *
    from crawler.spiders.spider_header import *


class ResidentLinkSpider(Crawler):
    name = 'resident-link-spider'
    allowed_domains = ['wsjkw.sh.gov.cn']
    root_url = 'https://wsjkw.sh.gov.cn'
    home_url = f'{root_url}/yqtb'
    start_urls = [f'{home_url}/index.html']

    def __init__(self, trait=CrawlerTrait.SILENT):
        super().__init__(trait)
        self.page = 1
        self.stopped = False
        self.add_task('//ul[@class="uli16 nowrapli list-date"]/li', self._crawl_resident_link_)

    def _crawl_resident_link_(self, response, documents):
        resident_links = []
        for document in documents:
            try:
                resident_link = self._create_resident_link_(response, document)
                if resident_link == -1:
                    self.stopped = True
                    break
                if resident_link == 0:
                    continue
                resident_links.append(resident_link)
            except Exception as e:
                logger.debug(e)
        if not resident_links:
            self.stopped = True
            return
        for resident_link in resident_links:
            if not resident_link.exist:
                resident_link.save()

    def _create_resident_link_(self, response, document):
        href = document.xpath('.//@href')[0]
        if not href.startswith('https'):
            href = f'{self.root_url}{href}'
        title = document.xpath('.//@title')[0]
        pattern = r'\D*(\d+)月(\d+)日\S+'
        groups = Matcher.find(title, pattern)
        if groups:
            # month, day = groups[0]
            month, day = groups
            if int(month) < 3:
                return -1
            link_date = Timer.from_date_string(f'2022-{month}-{day}')
            resident_link = ResidentLink()
            resident_link.published_at.set(link_date)
            resident_link.origin.set(response.url)
            resident_link.link.set(href)
            return resident_link
        return 0

    def _next_(self, response):
        if not self.stopped:
            self.page += 1
            url = f'{self.home_url}/index_{self.page}.html'
            print(color_line(f'next page: {url}', offset=4, border=True))
            return Request(url=url, callback=self.parse, dont_filter=True, )


class ResidentLinkSpiderUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    # @UnitTests.skip
    def crawl_resident_link_page_test(self):
        process = CrawlerProcess()
        process.crawl(ResidentLinkSpider)
        process.start()
        resident_links = ResidentLink().all
        assert len(resident_links) > 0
        logger.debug(resident_links)

    @UnitTests.skip
    def crawl_resident_link_page_with_voicing_test(self):
        class ResidentLinkVoicingSpider(ResidentLinkSpider):
            def __init__(self):
                super().__init__(CrawlerTrait.VOICING)

        process = CrawlerProcess()
        process.crawl(ResidentLinkVoicingSpider)
        process.start()
        web_driver_service.stop()


ResidentLinkSpiderUnitTests().run()
