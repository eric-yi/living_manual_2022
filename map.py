#!/bin/env python
# -*- coding: utf-8 -*- #

from header import *
import requests
import json


class MapSetting:
    def __init__(self):
        self.url = 'http://restapi.amap.com/v3/geocode/geo?parameters'
        self.key = 'c952f87f6dbed3ba259a6807d379370f'

    def __repr__(self):
        return str(self.__dict__)


map_setting = MapSetting()


class Map:
    def __init__(self):
        pass

    def query_address(self, address):
        return self._query_(address=address)

    def _query_(self, **kwargs):
        params = {
            'city': '上海市',
            'key': map_setting.key,
            'output': 'json'}
        for k, v in kwargs.items():
            params[k] = v
        response = requests.get(map_setting.url, params)
        return json.loads(response.content)


map = Map()


class MapUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    # @UnitTests.skip
    def query_address_test(self):
        result = map.query_address('莲花路')
        assert result is not None
        logger.debug(result)


MapUnitTests().run()
