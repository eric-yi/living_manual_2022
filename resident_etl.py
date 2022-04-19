#!/bin/env python
# -*- coding: utf-8 -*- #

from etl import *
from living_map_db import *


class ResidentMatcher:
    class Summary:
        class ShCity:
            def __init__(self, *args):
                self.year, self.month, self.day, self.diagnosed, self.asymptomatic, self.transfered, self.diagnosed_isolation, self.asymptomatic_isolation = args

            @property
            def date(self):
                return Timer.from_date_string(f'{self.year}-{self.month}-{self.day}')

            def __repr__(self):
                return str(self.__dict__)

        class ShDistrict:
            def __init__(self, *args):
                self.year, self.month, self.day, self.district, self.diagnosed, self.asymptomatic = args

            @property
            def date(self):
                return Timer.from_date_string(f'{self.year}-{self.month}-{self.day}')

            def __repr__(self):
                return str(self.__dict__)

    def __init__(self, matcher):
        self.matcher = matcher

    def match(self, s):
        return self.matcher(s)

    @staticmethod
    def ShCitySummaryMatcher(s):
        pattern = r'.+：(\d{4})年(\d{1,2})月(\d{1,2})日0—24时，\D+(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+'
        group = Matcher.find(s, pattern)
        return ResidentMatcher.Summary.ShCity(*group)

    @staticmethod
    def ShDistrictSummaryMatcher(s):
        pattern = '(\d{4})年(\d{1,2})月(\d{1,2})日，(.+)[无]?新增(\d+|)\D+[无]?新增(\d+)\D+'
        group = Matcher.find(s, pattern)
        return ResidentMatcher.Summary.ShDistrict(*group)


class ResidentJsonETL(JsonETL):
    def __init__(self):
        super().__init__('resident-json-etl', living_map_db)
        for resident_link in ResidentLink().inputs:
            resident_input = ResidentInput()
            resident_input.get_by_link(resident_link.id.val)
            self.filepaths.append(os.path.join(INPUT_DIR, 'shanghai_resident', resident_input.path.val))
        coordinate_filename = 'shanghai_resident_coordinate.json'
        self.coordinate_name = filename_of(coordinate_filename)
        self.filepaths.append(os.path.join(INPUT_DIR, coordinate_filename))
        self.resident_summary_list = []
        self.resident_list = []

    def _transfer_(self):
        for name, data in self.dataset.items():
            if name == self.coordinate_name:
                continue
            if 'mp.weixin.qq.com' in data['link']['link']:
                self._transfer_weixin_(name, data)

    def _transfer_weixin_(self, name, data):
        self._color_print_(f' transfer {name} by weixin')
        published_at = data['link']['published_at']
        self._add_city_summary_(data, name)
        district_summary_matcher = ResidentMatcher(ResidentMatcher.ShDistrictSummaryMatcher)
        coordinate_mapping = self.dataset[self.coordinate_name]
        for district in data['districts']:
            district_summary_data = district['summary']
            resident_summary = self._add_district_summary_(district_summary_data, district_summary_matcher, name)
            district_residents_data = district['residents']
            for resident_data in district_residents_data:
                resident = Resident()
                if resident_data in coordinate_mapping:
                    coordinate = coordinate_mapping[resident_data]
                    longitude, latitude = coordinate.split(',')
                    resident.longitude.set(longitude)
                    resident.latitude.set(latitude)
                resident.address.set(Matcher.AddressMatcher(resident_data))
                resident.published_at.set(published_at)
                if resident_summary is not None:
                    resident.district_code.set(resident_summary.district_code.val)
                self.resident_list.append(resident)

    def _add_city_summary_(self, data, name):
        sh_summary_data = data['summary']
        sh_summary_matcher = ResidentMatcher(ResidentMatcher.ShCitySummaryMatcher)
        sh_summary = sh_summary_matcher.match(sh_summary_data)
        resident_summary = self._matcher_summary_to_resident_summary(name, sh_summary)
        resident_summary.district_code.set('31')
        resident_summary.origin_desc.set(sh_summary_data)
        self.resident_summary_list.append(resident_summary)

    def _add_district_summary_(self, district_summary_data, district_summary_matcher, name):
        try:
            district_summary = district_summary_matcher.matcher(district_summary_data)
            resident_summary = self._matcher_summary_to_resident_summary(name, district_summary)
            resident_summary.origin_desc.set(district_summary_data)
            for district in districts:
                if district.name.val in district_summary.district or district_summary.district in district.name.val:
                    resident_summary.district_code.set(district.code.val)
                    break
            self.resident_summary_list.append(resident_summary)
            return resident_summary
        except Exception as e:
            logger.error(f'{name}: {e} - {district_summary_data}')
        return None

    def _matcher_summary_to_resident_summary(self, name, matcher_summary):
        resident_summary = ResidentSummary()
        resident_summary.published_at.set(matcher_summary.date)
        diagnosed = int(matcher_summary.diagnosed) if len(matcher_summary.diagnosed) > 0 else 0
        asymptomatic = int(matcher_summary.asymptomatic) if len(matcher_summary.asymptomatic) > 0 else 0
        resident_summary.diagnosed.set(diagnosed)
        resident_summary.asymptomatic.set(asymptomatic)
        resident_summary.origin.set(name)
        return resident_summary

    def _load_(self):
        for resident_summary in self.resident_summary_list:
            if not resident_summary.exist:
                resident_summary.save()
        for resident in self.resident_list:
            if not resident.exist:
                resident.save()


class ResidentJsonETLUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    # @UnitTests.skip
    def resident_json_etl_test(self):
        # ResidentSummary().batch_delete()
        # Resident().batch_delete()
        etl = ResidentJsonETL()
        etl.etl()
        assert len(etl.dataset) > 0
        summary_list = ResidentSummary().all
        assert len(summary_list) > 0
        logger.debug(summary_list)
        resident_list = Resident().all
        assert len(resident_list) > 0
        logger.debug(resident_list)

    @UnitTests.skip
    def resident_matcher_test(self):
        s1 = '市卫健委今早（6日）通报：2022年4月5日0—24时，新增本土新冠肺炎确诊病例311例和无症状感染者16766例，其中40例确诊病例为此前无症状感染者转归，4例确诊病例和16256例无症状感染者在隔离管控中发现，其余在相关风险人群排查中发现。新增境外输入性新冠肺炎确诊病例4例和无症状感染者1例，均在闭环管控中发现。'
        s2 = '市卫健委今早（13日）通报：2022年4月12日0—24时，新增本土新冠肺炎确诊病例1189例和无症状感染者25141例，其中23例确诊病例为此前无症状感染者转归，867例确诊病例和24500例无症状感染者在隔离管控中发现，其余在相关风险人群排查中发现。'
        matcher = ResidentMatcher(ResidentMatcher.ShCitySummaryMatcher)
        summary = matcher.match(s1)
        assert summary.day == '5'
        logger.debug(summary)
        summary = matcher.match(s2)
        assert summary.day == '12'
        logger.debug(summary)
        s3 = '2022年4月5日，浦东新区新增162例本土确诊病例，新增7983例本土无症状感染者，分别居住于：'
        s4 = '2022年4月5日，静安区新增12例本土确诊病例，新增290例本土无症状感染者，分别居住于：'
        matcher = ResidentMatcher(ResidentMatcher.ShDistrictSummaryMatcher)
        summary = matcher.match(s3)
        assert summary.district == '浦东新区'
        logger.debug(summary)
        summary = matcher.match(s4)
        assert summary.district == '静安区'
        logger.debug(summary)
        s5 = '2022年4月13日，杨浦区新增54例本土新冠肺炎确诊病例，新增1131例本土无症状感染者，分别居住于：'
        summary = matcher.match(s5)
        assert summary.district == '杨浦区'
        logger.debug(summary)
        s6 = '2022年4月10日，崇明区无新增本土确诊病例，新增55例新冠肺炎无症状感染者，分别居住于：'
        summary = matcher.match(s6)
        assert summary.district == '崇明区'
        logger.debug(summary)


ResidentJsonETLUnitTests().run()
