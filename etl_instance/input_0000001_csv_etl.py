#!/bin/env python
# -*- coding: utf-8 -*- #

from vendor_etl import *
from vendor_etl import VendorMatcher


class Input0000001CsvETL(VendorCsvETL):
    def __init__(self):
        super().__init__('0000001', 'input_0000001_csv_etl')

    def _transfer_(self):
        self._transfer_001_()
        self._transfer_002_()

    def _transfer_001_(self):
        dataframes = self.dataset['001']
        self._transfer_from_dataframes_(dataframes, 1,
                                        name=1,
                                        origin=2,
                                        available_desc=3,
                                        desc=4,
                                        input_path='0000001/001')

    def _transfer_002_(self):
        dataframes = self.dataset['002']
        self._transfer_from_dataframes_(dataframes, 1,
                                        name=2,
                                        origin=1,
                                        desc=3,
                                        available_desc=4,
                                        contact=VendorMatcher(5, Matcher.ChineseMatcher),
                                        mobile=VendorMatcher(5, Matcher.MobileMatcher),
                                        districts=VendorMatcher([1, 4], VendorMatcher.DistrictMatcher),
                                        input_path='0000001/002')


class Input0000001CsvETLUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    # @UnitTests.skip
    def input_csv_etl_test(self):
        etl = Input0000001CsvETL()
        etl.etl()
        logger.debug(etl.dataset)
        assert len(etl.dataset) == 2


Input0000001CsvETLUnitTests().run()
