#!/bin/env python
# -*- coding: utf-8 -*- #

from etl import *
from etl_instance import *


class ETLFactory:
    def __init__(self):
        self.etl_instance_list = [
            input_0000001_csv_etl.Input0000001CsvETL(),
        ]

    def build(self):
        for etl_instance in self.etl_instance_list:
            etl_instance.etl()


class ETLFactoryUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    def _setup_(self):
        self.factory = ETLFactory()

    # @UnitTests.skip
    def build_test(self):
        self.factory.build()


ETLFactoryUnitTests().run()
