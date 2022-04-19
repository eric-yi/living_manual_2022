#!/bin/env python
# -*- coding: utf-8 -*- #

from db import *


class ETL:
    def __init__(self, name, db):
        self.name = name
        self.db = db

    def etl(self):
        self._color_print_('ETL start')
        etl_timer = Timer()
        logger.debug(f'---- {self.name} extract start ----')
        extract_timer = Timer()
        self._extract_()
        logger.debug(f'---- {self.name} extract end elapse {extract_timer.elapse()} ----')
        logger.debug(f'---- {self.name} transfer start ----')
        transfer_timer = Timer()
        self._transfer_()
        logger.debug(f'---- {self.name} transfer end elapse {transfer_timer.elapse()} ----')
        logger.debug(f'---- {self.name} load start ----')
        load_timer = Timer()
        self._load_()
        logger.debug(f'---- {self.name} load end elapse {load_timer.elapse()} ----')
        self._color_print_(f'ETL end elapse {etl_timer.elapse()}')

    def _extract_(self):
        pass

    def _transfer_(self):
        pass

    def _load_(self):
        pass

    def _color_print_(self, msg):
        print(color_line(f'{self.name} {msg}', offset=4, border=True))


class FileETL(ETL):
    def __init__(self, name, db):
        super().__init__(name, db)
        self.filepaths = []
        self.dataset = {}

    def _extract_(self):
        for filepath in self.filepaths:
            with open(filepath, 'r') as fd:
                data = self._extract_file_(fd)
                self.dataset[filename_of(filepath)] = data

    def _extract_file_(self, fd):
        pass


class CsvETL(FileETL):
    def __init__(self, name, db):
        super().__init__(name, db)

    def _extract_file_(self, fd):
        reader = csv.reader(fd)
        data = list(map(lambda row: row, reader))
        dataframe = {}
        for i, r in enumerate(data):
            dataframe[i] = {}
            row = data[i]
            for j, c in enumerate(row):
                dataframe[i][j] = c
        return pd.DataFrame(dataframe)


class JsonETL(FileETL):
    def __init__(self, name, db):
        super().__init__(name, db)
        self.csv_dataframes = {}

    def _extract_file_(self, fd):
        return json.load(fd)


class ETLUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    @UnitTests.skip
    def csv_etl_test(self):
        etl = CsvETL('csv-etl', None)
        etl.filepaths = [
            os.path.join(INPUT_DIR, '0000001', '002.csv')
        ]
        etl.etl()
        assert len(etl.dataset) is not None
        print(etl.dataset)

    # @UnitTests.skip
    def json_etl_test(self):
        etl = JsonETL('json-etl', None)
        etl.filepaths = [
            os.path.join(INPUT_DIR, 'shanghai_resident', 'shanghai_resident_2022-04-05 00:00:00.json')
        ]
        etl.etl()
        assert len(etl.dataset) is not None
        print(etl.dataset)


ETLUnitTests().run()
