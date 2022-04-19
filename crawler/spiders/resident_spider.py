#!/usr/bin/env python
# -*- coding:utf-8 -*-

from living_map_db import *

try:
    from crawler import *
    from spider_header import *
except Exception:
    from crawler.spiders.crawler import *
    from crawler.spiders.spider_header import *


class ResidentSpider(Crawler):
    name = 'resident-spider'
    allowed_domains = ['wsjkw.sh.gov.cn', 'mp.weixin.qq.com']

    class DistrictResident:
        def __init__(self, summary, residents):
            self.summary = summary
            self.residents = residents

        def __repr__(self):
            return str(self.__dict__)

    class CityResident:
        def __init__(self, link, summary, districts):
            self.link = link
            self.summary = summary
            self.districts = districts

        def __repr__(self):
            return str(self.__dict__)

        @property
        def _json_dict_(self):
            return {'summary': self.summary,
                    'districts': self.districts,
                    'link': self.link.fields
                    }

        def write(self):
            create_folder(RESIDENT_INPUT_DIR)
            filename = f'shanghai_resident_{self.link.published_at.val}.json'
            json_file = os.path.join(RESIDENT_INPUT_DIR, filename)
            with open(json_file, 'w', encoding='utf8') as fd:
                json.dump(self._json_dict_, fd, ensure_ascii=False, cls=ObjectEncoder, indent=2)
            resident_input = ResidentInput()
            resident_input.link_id.set(self.link.id.val)
            resident_input.path.set(filename)
            resident_input.save()
            self.link.save_input()

    def __init__(self, trait=CrawlerTrait.SILENT):
        super().__init__(trait)
        self.page = 1
        self.stopped = False
        self.html_to_file = True
        self.start_urls = []
        self.link_mapping = {}
        link_jobs = ResidentLink().jobs
        for link_job in link_jobs:
            self.start_urls.append(link_job.link.val)
            self.link_mapping[link_job.link.val] = link_job
        self.add_task('//div[@id="js_content"]/section[@data-id and not(@data-role)]', self._crawl_resident_on_weixin_,
                      'mp.weixin.qq.com')

    def _before_parse_(self, response, **kwargs):
        resident_link = self.link_mapping[response.url]
        self.html_to_file = self.html_to_file and resident_link.not_save_origin
        super()._before_parse_(response, **kwargs)
        if self.html_to_file:
            link = self.link_mapping[response.url]
            link.origin_filepath.set(f'{url_to_filename(response.url)}.html')
            link.save_origin()

    def _crawl_resident_on_weixin_(self, response, documents):
        summary, districts = self._parse_resident_on_weixin_(documents)
        self._save_resident_on_weixin_(response, summary, districts)

    def _save_resident_on_weixin_(self, response, summary, districts):
        resident_link = self.link_mapping[response.url]
        sh_resident = ResidentSpider.CityResident(resident_link, summary, districts)
        if resident_link.not_save_input:
            sh_resident.write()
        logger.debug(sh_resident)

    def _parse_resident_on_weixin_(self, documents):
        sh_document, pd_document = documents[0].xpath('.//section[@data-id and not(@data-role)]')
        district_documents = [pd_document] + documents[1:]
        districts = self._crawl_district_resident_on_weixin_(district_documents)
        summary_elements = sh_document.xpath('.//p/span')
        summary = ''.join([summary_element.text for summary_element in summary_elements])
        logger.debug(f'==summary: {summary}')
        return (summary, districts)

    def _crawl_district_resident_on_weixin_(self, documents):
        district_resident_list = []
        for document in documents:
            try:
                p_elements = document.xpath('.//p')
                summary = ''.join(list(map(lambda span: span.text, p_elements[0].xpath('.//span'))))
                residents = []
                for p in p_elements[1:]:
                    span = p.xpath('.//span')
                    if span and span[0].text is not None:
                        residents.append(span[0].text)
                district_resident_list.append(ResidentSpider.DistrictResident(summary, residents))
            except Exception as e:
                logger.debug(e)
        return district_resident_list

    @staticmethod
    def reset_status():
        ResidentInput().batch_delete()
        ResidentLink().reset_state_all()


class ResidentSpiderUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    # @UnitTests.skip
    def crawl_resident_page_test(self):
        self._crawl_resident_page_()
        logger.debug(ResidentLink().all)
        resident_input_list = ResidentInput().all
        assert len(resident_input_list) > 0
        logger.debug(resident_input_list)

    @UnitTests.skip
    def crawl_resident_page_with_voicing_test(self):
        class ResidentVoicingSpider(ResidentSpider):
            def __init__(self):
                super().__init__(CrawlerTrait.VOICING)

        process = CrawlerProcess()
        process.crawl(ResidentVoicingSpider)
        process.start()
        web_driver_service.stop()

    @UnitTests.skip
    def given_reset_then_crawl_resident_page_test(self):
        ResidentSpider.reset_status()
        self._crawl_resident_page_()
        logger.debug(ResidentLink().all)
        resident_input_list = ResidentInput().all
        assert len(resident_input_list) > 0

    @UnitTests.skip
    def reset_resident_test(self):
        ResidentSpider.reset_status()
        assert len(ResidentInput().find()) == 0
        for link in ResidentLink().find():
            assert link.state.val == 1

    @UnitTests.skip
    def crawl_resident_on_weixin_from_html_test(self):
        class MockResponse:
            def __init__(self, url, text):
                self.url = url
                self.text = text

        ResidentSpider.reset_status()
        with open(os.path.join(ORIGIN_DIR, 'mp.weixin.qq.com_s_OZGM-pNkefZqWr0IFRJj1g.html'), 'r',
                  encoding='utf8') as fd:
            html = fd.read()
        response = MockResponse('https://mp.weixin.qq.com/s/OZGM-pNkefZqWr0IFRJj1g', html)
        spider = ResidentSpider()
        documents = spider.driver.query(response, spider.tasks[0].xpath)
        assert documents is not None
        spider._crawl_resident_on_weixin_(response, documents)

    def _crawl_resident_page_(self):
        process = CrawlerProcess()
        process.crawl(ResidentSpider)
        process.start()


ResidentSpiderUnitTests().run()
