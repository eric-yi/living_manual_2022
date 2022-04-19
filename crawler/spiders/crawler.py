#!/usr/bin/env python
# -*- coding:utf-8 -*-

try:
    from spider_header import *
except Exception:
    from crawler.spiders.spider_header import *

from service import ServiceStatus, Service

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from scrapy import Request
from scrapy.spiders import Spider, Rule
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor

from bs4 import BeautifulSoup
from lxml import etree


class WebDriverService(Service):
    def __init__(self):
        super().__init__('web-crawler',
                         'java -Dwebdriver.chrome.driver="chromedriver" -jar selenium-server-standalone-3.141.59.jar')

    def start(self):
        super().start()
        time.sleep(1)
        url = 'http://localhost:4444/wd/hub'
        logger.info(f'Initializing chromium, {url}')
        chrome_options = DesiredCapabilities.CHROME
        chrome_options['prefs'] = {"credentials_enable_service": False, "profile.password_manager_enabled": False}
        self.driver = webdriver.Remote(command_executor=url,
                                       desired_capabilities=chrome_options)

    def open(self, site):
        if self.driver is not None:
            self.driver.get(site)

    def stop(self):
        if self.driver is not None:
            self.driver.close()
        super().stop()


web_driver_service = WebDriverService()


class CrawlerMatcher:
    def __init__(self, result, matcher):
        self.result = result
        self.matcher = matcher

    def match(self):
        return self.matcher(self.result)


class CrawlerTrait(Enum):
    SILENT = 'silent'
    VOICING = 'voicing'


class SilentDriver:
    def __init__(self):
        pass

    def request(self, url):
        pass

    def query(self, response, xpath, wait_timeout=0):
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        dom = etree.HTML(str(soup))
        return dom.xpath(xpath)


class VoicingDriver:
    def __init__(self):
        if web_driver_service.status == ServiceStatus.IDLE:
            web_driver_service.start()
        self.driver = web_driver_service.driver

    def request(self, url):
        self.driver.get(url)

    def query(self, response, xpath, wait_timeout=3):
        try:
            return WebDriverWait(self.driver, wait_timeout).until(
                ec.presence_of_element_located(
                    (By.XPATH, xpath)
                ))
        except Exception as e:
            logger.error(e)
            return None


class Crawler(Spider):
    class Task:
        def __init__(self, xpath, do, filter=None):
            self.xpath = xpath
            self.do = do
            self.filter = filter

        def __repr__(self):
            return str(self.__dict__)

    def __init__(self, trait=CrawlerTrait.SILENT):
        super().__init__(f'{trait} crawler')
        if trait == CrawlerTrait.SILENT:
            self.driver = SilentDriver()
        else:
            self.driver = VoicingDriver()
        self.tasks = OrderedDict()
        self.tasks = []
        self.html_to_file = False

    def start_requests(self):
        logger.debug('start requests')
        for start_url in self.start_urls:
            yield Request(url=start_url, callback=self.parse)

    def add_task(self, xpath, call, filter=None):
        self.tasks.append(Crawler.Task(xpath, call, filter))

    def parse(self, response, **kwargs):
        self._before_parse_(response, **kwargs)
        url = response.url
        print(color_line(f'parse {url}', offset=4))
        timer = Timer()
        self.driver.request(url)
        for task in self.tasks:
            try:
                if task.filter is not None and task.filter not in url:
                    logger.debug(f'skip {url} to crawl: "{task.xpath}"')
                    continue
                logger.debug(f'{url} to crawl: "{task.xpath}"')
                documents = self._crawl_(response, task.xpath)
                task.do(response, documents)
            except Exception as e:
                logger.error(f'crawl xpath error: {e}')
        print(color_line(f'parse {url} elapse {timer.elapse()}', offset=4))
        return self._next_(response)

    def _before_parse_(self, response, **kwargs):
        if self.html_to_file:
            html_file = os.path.join(ORIGIN_DIR, f'{url_to_filename(response.url)}.html')
            with open(html_file, 'w', encoding='utf8') as fd:
                fd.write(response.text)
                fd.flush()

    def _next_(self, response):
        pass

    def _crawl_(self, response, xpath):
        return self.driver.query(response, xpath)


class SilentSpider(Crawler):
    name = 'silent-spider'
    allowed_domains = ['localhost:18088']
    start_urls = ['http://localhost:18088/example']

    def __init__(self):
        super().__init__(CrawlerTrait.SILENT)
        self.add_task('//p[@id="title"]', self._crawl_xpath_test_)

    def _crawl_xpath_test_(self, result):
        print(color_lines(f'silent spider task: \n{result}', offset=4, border=True))


class VoicingSpider(Crawler):
    name = 'silent-spider'
    allowed_domains = ['localhost:18088']
    start_urls = ['http://localhost:18088/example']

    def __init__(self):
        super().__init__(CrawlerTrait.VOICING)
        self.add_task('//p[@id="title"]', self._crawl_xpath_test_)

    def _crawl_xpath_test_(self, result):
        print(color_lines(f'voice spider task: \n{result}', offset=4, border=True))


RESIDENT_INPUT_DIR = os.path.join(INPUT_DIR, 'shanghai_resident')

RESIDENT_COORDINATE_FILE = os.path.join(INPUT_DIR, 'shanghai_resident_coordinate.json')

from http.server import HTTPServer, BaseHTTPRequestHandler


class CrawlerUnitTests(UnitTests):
    class TestServer(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes('<html><head><title>test server</title></head>', 'utf-8'))
            self.wfile.write(bytes('<p>Request: %s</p>', 'utf-8'))
            self.wfile.write(bytes('<body>', 'utf-8'))
            self.wfile.write(bytes('<p id="title">This is an example web server.</p>', 'utf-8'))
            self.wfile.write(bytes('</body></html>', 'utf-8'))

    def __init__(self):
        super().__init__(__file__)

    def _setup_(self):
        self.host = 'localhost'
        self.port = 18088
        self.test_server = HTTPServer((self.host, self.port), CrawlerUnitTests.TestServer)
        print(color_line(f'Server started http://{self.host}:{self.port}', offset=4, border=True))
        from threading import Thread
        t = Thread(target=(lambda: self.test_server.serve_forever()))
        t.daemon = True
        t.start()

    def _teardown_(self):
        if self.test_server is not None:
            self.test_server.server_close()
            self.test_server = None

    @UnitTests.skip
    def start_web_driver_service_test(self):
        web_driver_service.start()
        assert web_driver_service.driver is not None
        web_driver_service.open('https://www.baidu.com/')
        assert web_driver_service.driver.current_url == 'https://www.baidu.com/'
        logger.debug(web_driver_service.driver)
        web_driver_service.stop()

    # @UnitTests.skip
    def use_slient_crawler_test(self):
        process = CrawlerProcess()
        process.crawl(SilentSpider)
        process.start()
        process.stop()

    @UnitTests.skip
    def use_voicing_crawler_test(self):
        process = CrawlerProcess()
        process.crawl(VoicingSpider)
        process.start()
        process.stop()
        web_driver_service.stop()


CrawlerUnitTests().run()
