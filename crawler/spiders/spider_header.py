#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys

root_header_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.append(root_header_dir)

from header import *

logging.getLogger('scrapy').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


class SpiderHeaderUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    # @UnitTests.skip
    def smoke_test(self):
        assert True
        logger.info('Spider Header')


SpiderHeaderUnitTests().run()
