#!/bin/env python
# -*- coding: utf-8 -*- #

from etl import *
from living_vendor_db import *


class VendorMatcher:
    def __init__(self, index, matcher):
        self.index = index
        self.matcher = matcher

    def match(self, data):
        if type(self.index) == list:
            s = ' '.join([data[i] for i in self.index])
        else:
            s = data[self.index]
        return self.matcher(s)

    @staticmethod
    def DistrictMatcher(s):
        return list(filter(lambda d: d.name.val[:2] in s, districts))


class VendorCsvETL(CsvETL):
    def __init__(self, num, name='vendor_csv_etl'):
        super().__init__(name, living_vendor_db)
        self.vendor_list = []
        self.filepaths = list_files(os.path.join(INPUT_DIR, num))

    def _load_(self):
        for vendor in self.vendor_list:
            vendor.save()
            for district in vendor.districts:
                if district.code == '31' and len(vendor.districts) > 1:
                    continue
                vendor_district = VendorDistrict()
                vendor_district.vendor_id.set(vendor.id.val)
                vendor_district.district_code.set(district.code.val)
                vendor_district.save()

    def _transfer_from_dataframes_(self, dataframe, start_index, **mappings):
        rows, cols = dataframe.T.shape
        for i in range(start_index, rows):
            data = dataframe[i]
            vendor = Vendor()
            for name, val in mappings.items():
                value = ''
                if type(val) == int:
                    value = data[val]
                elif type(val) == str:
                    value = val
                elif type(val) == VendorMatcher:
                    value = val.match(data)
                if type(value) == list:
                    if len(value) > 0:
                        vendor.__setattr__(name, value)
                else:
                    vendor.__getattribute__(name).set(value)
            vendor.input_type.set('csv')
            self.vendor_list.append(vendor)


class VendorCsvETLUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    # @UnitTests.skip
    def vendor_csv_etl_test(self):
        etl = VendorCsvETL('0000001')
        etl.etl()
        logger.debug(etl.dataset)
        assert len(etl.dataset) == 2

    # @UnitTests.skip
    def matcher_test(self):
        data = ['米姑娘13761884893', '浦东发布', '浦东发布, 宝山区']
        matcher = VendorMatcher(0, Matcher.ChineseMatcher)
        chinese = matcher.match(data)
        assert chinese == '米姑娘'
        matcher = VendorMatcher(0, Matcher.MobileMatcher)
        mobile = matcher.match(data)
        assert mobile == '13761884893'
        matcher = VendorMatcher(1, VendorMatcher.DistrictMatcher)
        match_districts = matcher.match(data)
        assert len(match_districts) == 1 and match_districts[0].name == '浦东新区'
        matcher = VendorMatcher(2, VendorMatcher.DistrictMatcher)
        match_districts = matcher.match(data)
        assert len(match_districts) == 2 and match_districts[0].name == '宝山区' and match_districts[1].name == '浦东新区'


VendorCsvETLUnitTests().run()
