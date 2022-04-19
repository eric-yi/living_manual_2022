#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import logging
import __main__ as main
import time
from enum import Enum
import collections
import inspect
from datetime import datetime
import numpy as np
import pandas as pd
import csv
import re
from functools import reduce
import uuid
from collections import OrderedDict
import json

FORMAT = '%(levelname)s %(asctime)s [%(filename)s:%(lineno)d]: %(message)s'
logging.basicConfig(format=FORMAT, stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

WORKDIR = os.path.dirname(__file__)
ORIGIN_DIR = os.path.join(WORKDIR, 'data', 'origin')
INPUT_DIR = os.path.join(WORKDIR, 'data', 'input')
TEMPlATE_DIR = os.path.join(WORKDIR, 'data', 'template')
MANUAL_DIR = os.path.join(WORKDIR, 'data', 'manual')
DB_DIR = os.path.join(WORKDIR, 'db')

DISTRICTS_COORD_MAPPING = {
    '黄浦区': '121.48442,31.231661',
    '徐汇区': '121.436307,31.188334',
    '长宁区': '121.424751,31.220537',
    '静安区': '121.447348,31.227718',
    '普陀区': '121.39547,31.249618',
    '虹口区': '121.504994,31.264917',
    '杨浦区': '121.525409,31.259588',
    '闵行区': '121.380857,31.112834',
    '宝山区': '121.489431,31.405242',
    '嘉定区': '121.265276,31.375566',
    '浦东新区': '121.544346,31.221461',
    '金山区': '121.341774,30.742769',
    '松江区': '121.227676,31.03257',
    '青浦区': '121.124249,31.15098',
    '奉贤区': '121.473945,30.918406',
    '崇明县': '121.397662,31.623863'}

SLOGAN = f'''   ___      _                                         __    ___  ___  ___  ___          __                  __        _ 
  / (_)  __(_)__  ___ _    __ _  ___ ____  __ _____ _/ /   |_  |/ _ \|_  ||_  |    ___ / /  ___ ____  ___ _/ /  ___ _(_)
 / / / |/ / / _ \/ _ `/   /  ' \/ _ `/ _ \/ // / _ `/ /   / __// // / __// __/    (_-</ _ \/ _ `/ _ \/ _ `/ _ \/ _ `/ / 
/_/_/|___/_/_//_/\_, /   /_/_/_/\_,_/_//_/\_,_/\_,_/_/   /____/\___/____/____/   /___/_//_/\_,_/_//_/\_, /_//_/\_,_/_/  
                /___/                                                                               /___/ '''


class TermStyle:
    RESET = '\33[0m'
    BOLD = '\33[1m'
    ITALIC = '\33[3m'
    URL = '\33[4m'
    BLINK = '\33[5m'
    BLINK2 = '\33[6m'
    SELECTED = '\33[7m'
    BLACK = '\33[30m'
    RED = '\33[31m'
    GREEN = '\33[32m'
    YELLOW = '\33[33m'
    BLUE = '\33[34m'
    VIOLET = '\33[35m'
    BEIGE = '\33[36m'
    WHITE = '\33[37m'
    BLACKBG = '\33[40m'
    REDBG = '\33[41m'
    GREENBG = '\33[42m'
    YELLOWBG = '\33[43m'
    BLUEBG = '\33[44m'
    VIOLETBG = '\33[45m'
    BEIGEBG = '\33[46m'
    WHITEBG = '\33[47m'
    GREY = '\33[90m'
    RED2 = '\33[91m'
    GREEN2 = '\33[92m'
    YELLOW2 = '\33[93m'
    BLUE2 = '\33[94m'
    VIOLET2 = '\33[95m'
    BEIGE2 = '\33[96m'
    WHITE2 = '\33[97m'
    GREYBG = '\33[100m'
    REDBG2 = '\33[101m'
    GREENBG2 = '\33[102m'
    YELLOWBG2 = '\33[103m'
    BLUEBG2 = '\33[104m'
    VIOLETBG2 = '\33[105m'
    BEIGEBG2 = '\33[106m'
    WHITEBG2 = '\33[107m'


def get_screen_width():
    from screeninfo import get_monitors
    monitors = list(filter(lambda monitor: monitor.is_primary, get_monitors()))
    if len(monitors) > 0:
        monitor = monitors[0]
        return monitor.width
    return -1


def pretty_label(width, color=TermStyle.GREEN2):
    return '{color}{label_line}{reset}'.format(
        color=color, label_line=''.join(('*' for _ in range(width))),
        reset=TermStyle.RESET)


def color_line(line, **kwargs):
    border = kwargs['border'] if 'border' in kwargs else False
    offset = kwargs['offset'] if 'offset' in kwargs else 0
    color = kwargs['color'] if 'color' in kwargs else TermStyle.BLUE2
    label_color = kwargs['label_color'] if 'label_color' in kwargs else TermStyle.GREEN2
    width = len(line) + offset * 2
    color_line = color_string(line, width, offset, color, label_color)
    if border:
        label = pretty_label(width, label_color)
        return f'{label}\n{color_line}\n{label}'
    return color_line


def color_lines(lines, **kwargs):
    label_color = kwargs['label_color'] if 'label_color' in kwargs else TermStyle.GREEN2
    line_color = kwargs['line_color'] if 'line_color' in kwargs else TermStyle.BLUE2
    offset = kwargs['offset'] if 'offset' in kwargs else 0
    width = len(reduce(lambda s1, s2: s1 if len(s1) > len(s2) else s2, lines.splitlines())) + offset * 2
    label = pretty_label(width, label_color)
    colors = [label]
    for line in lines.splitlines():
        colors.append(color_string(line, width, offset, line_color, label_color))
    colors.append(label)
    return '\n'.join(colors)


def color_string(s, width, offset, color, label_color):
    prefix = ''
    if offset > 0:
        prefix = f'{label_color}*{TermStyle.RESET}'
        prefix += ' '.join(['' for _ in range(offset)])
    postfix = ''
    if offset > 0:
        postfix = ' '.join(['' for _ in range(width - offset - len(s))])
        postfix += f'{label_color}*{TermStyle.RESET}'
    return f'{prefix}{color}{s}{TermStyle.RESET}{postfix}'


def color_slogan():
    return color_lines(SLOGAN, label_color=TermStyle.BLUE2, line_color=TermStyle.RED2, offset=2)


def shell(statement, **kwargs):
    print(color_line(statement))
    from subprocess import Popen, PIPE, STDOUT
    from threading import Thread
    waiting = kwargs['waiting'] if 'waiting' in kwargs else True
    valued = kwargs['valued'] if 'valued' in kwargs else False
    cwd = kwargs['cwd'] if 'cwd' in kwargs else WORKDIR
    logger.debug(f'run at "{cwd}"')

    class Output():
        pid = None
        stdout = []
        stderr = []

        def __repr__(self):
            return str(self.__dict__)

        def single_value(self):
            return self.stdout[0] if len(self.stdout) > 0 else ''

    def log_subprocess_output(processor, output):
        with processor.stdout:
            for data in iter(processor.stdout.readline, b''):
                line = data.decode('utf-8').rstrip()
                output.stdout.append(line)
                print(line)
        processor.wait()

    try:
        output = Output()
        processor = Popen(statement, cwd=cwd, shell=True,
                          stdout=PIPE, stderr=STDOUT)
        output.pid = processor.pid
        thread = Thread(target=log_subprocess_output,
                        args=(processor, output,))
        thread.setDaemon(not waiting)
        thread.start()
        if waiting:
            thread.join()
        if valued:
            return output.single_value()
        return output
    except KeyboardInterrupt:
        logger.error(f'programming interrupt by ctrl-c, shell:{statement}')
    except Exception as err:
        logger.error(f'execute shell:{statement} exception: {err}')


def now():
    return datetime.now()


def list_files(dir):
    return list(
        map(lambda f: os.path.join(os.path.abspath(dir), f), filter(lambda f: not os.path.isdir(f), os.listdir(dir))))


def filename_of(path):
    return os.path.basename(path).split('.')[0]


def read(filepath):
    with open(filepath, 'r') as fd:
        return fd.read()


def write(filepath, content):
    with open(filepath, 'w') as fd:
        fd.write(content)
        fd.flush()


def url_to_filename(url):
    from urllib.parse import urlparse
    u = urlparse(url)
    site = u.netloc
    path = u.path.replace('/', '_').split('.')[0]
    return f'{site}{path}'


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


class Matcher:
    @staticmethod
    def ChineseMatcher(s):
        return Matcher._match_first_(s, r'[\u4e00-\u9fa5]+')

    @staticmethod
    def ChineseMatcher(s):
        return Matcher._match_first_(s, r'[\u4e00-\u9fa5]+')

    @staticmethod
    def MobileMatcher(s):
        return Matcher._match_first_(s, r'1[358]\d+')

    @staticmethod
    def TelMatcher(s):
        return Matcher._match_first_(s, r'\(?0\d{2,3}[)-]?\d{7,8}')

    @staticmethod
    def IntegerMatcher(s):
        return Matcher._match_first_(s, r'\d+,?\d+')

    @staticmethod
    def AddressMatcher(s):
        return Matcher._match_first_(s, r'[\u4e00-\u9fa5a-zA-Z0-9]+')

    @staticmethod
    def find(s, pattern):
        group = re.findall(pattern, s)
        if len(group) > 0:
            return group[0]
        return []

    @staticmethod
    def _match_first_(s, pattern):
        matches = re.findall(pattern, s)
        if len(matches) > 0:
            return matches[0]
        return ''


class Timer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.now = now()

    def elapse(self):
        class TimeDelta:
            def __init__(self, delta):
                self.delta = delta
                self.s = round(delta.total_seconds(), 3)
                self.ms = self.s * 1000

            def __repr__(self):
                return f'{self.s} seconds'

        delta = now() - self.now
        return TimeDelta(delta)

    @staticmethod
    def code():
        return now().strftime("%Y%d%m%H%M%S")

    @staticmethod
    def timestamp():
        return now().timestamp()

    @staticmethod
    def from_string(s, fmp='%Y-%m-%d %H:%M:%S'):
        return datetime.strptime(s, fmp)

    @staticmethod
    def from_date_string(s):
        return Timer.from_string(s, '%Y-%m-%d')

    @staticmethod
    def to_string(d, fmt):
        return d.strftime(fmt)

    @staticmethod
    def to_date_string(d):
        return Timer.to_string(d, '%Y-%m-%d')


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "_dict_"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj


def html_filepath(district=None):
    filename = f'living_shanghai_2022_{Timer.code()}'
    if district:
        filename += f'_{district}'
    return os.path.join(MANUAL_DIR, f'{filename}.html')


class UnitTests:
    def __init__(self, filepath=__file__):
        self.name = self.__class__.__name__
        self.cls = self.__class__.__mro__[0]
        self.filepath = filepath

    @property
    def _skip_(self):
        return self.filepath != main.__file__

    def _setup_(self):
        pass

    def _teardown_(self):
        pass

    def run(self):
        if self._skip_:
            return
        self._setup_()

        fns = [getattr(self.cls, fn)
               for fn in dir(self.cls) if not fn.startswith('__')]
        for fn in fns:
            if inspect.isfunction(fn):
                fun_name = fn.__name__
                annotations = fn.__annotations__
                if 'test' in annotations or fun_name.endswith('_test'):
                    if 'test' in annotations and annotations['test'] == 'skip':
                        print(color_line(f'== {self.name}:{fn.__name__} skipped ==', color=TermStyle.RED2))
                        continue
                    print(color_line(f'== {self.name}:{fn.__name__} run ==', color=TermStyle.GREEN2))
                    timer = Timer()
                    eval(f'self.{fn.__name__}()')
                    print(color_line(f'{self.name}:{fn.__name__} elapse {timer.elapse()}', offset=4, border=True,
                                     color=TermStyle.GREEN2, label_color=TermStyle.BLUE2))

        self._teardown_()

    @staticmethod
    def test(fn):
        fn.__annotations__['test'] = 'normal'
        return fn

    @staticmethod
    def skip(fn):
        fn.__annotations__['test'] = 'skip'
        return fn


class HeaderUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    @UnitTests.skip
    def shell_test(self):
        output = shell('ls')
        assert output is not None
        logger.debug(f'$ ls \n {output}')
        assert output.pid > 0
        output = shell('ls', waiting=True)
        logger.debug(f'$ ls \n {output}')
        assert output.pid > 0

    @UnitTests.skip
    def list_files_test(self):
        files = list_files(WORKDIR)
        assert len(files) > 0
        print(files)
        files = list_files(os.path.join('data', 'input', '0000001'))
        assert len(files) > 0
        print(files)

    @UnitTests.skip
    def filename_test(self):
        name = filename_of('data/input/0000001/001.csv')
        print(name)
        assert name == '001'

    @UnitTests.skip
    def read_test(self):
        tpl_body = read(os.path.join(TEMPlATE_DIR, 'living_manual_body.tpl'))
        assert tpl_body is not None
        logger.debug(tpl_body)

    @UnitTests.skip
    def timer_test(self):
        timer = Timer()
        time.sleep(1)
        time_delta = timer.elapse()
        assert time_delta.s >= 1
        assert time_delta.ms >= 1000
        logger.debug(time_delta)
        d = Timer.from_date_string('2022-4-1')
        assert Timer.to_date_string(d) == '2022-04-01'

    @UnitTests.skip
    def color_string_test(self):
        s = color_line('one line string')
        print(s)
        s = color_line('one line string with offset', offset=4)
        print(s)
        s = color_line('one line string with offset and border', offset=4, border=True)
        print(s)
        s = color_lines('\n'.join(['multi line string', 'multi line string', 'multi line string']))
        print(s)
        s = color_lines('\n'.join(
            ['multi line string with offset', 'multi line string with offset', 'multi line string with offset']),
            offset=4)
        print(s)

    # @UnitTests.skip
    def matcher_test(self):
        s = '米姑娘13761884893'
        chinese = Matcher.ChineseMatcher(s)
        assert chinese == '米姑娘'
        mobile = Matcher.MobileMatcher(s)
        assert mobile == '13761884893'
        s = '83,843 repository results'
        number = Matcher.IntegerMatcher(s)
        assert number == '83,843'
        s = '德州路420弄，'
        address = Matcher.AddressMatcher(s)
        assert address == '德州路420弄'
        s = '德州路420弄、 '
        address = Matcher.AddressMatcher(s)
        assert address == '德州路420弄'

    @UnitTests.skip
    def url_to_filename_test(self):
        urls = ['https://mp.weixin.qq.com/s/OZGM-pNkefZqWr0IFRJj1g',
                'https://mp.weixin.qq.com/s/vxFiV2HeSvByINUlTmFKZA',
                'https://mp.weixin.qq.com/s/u0XfHF8dgfEp8vGjRtcwXA',
                'https://mp.weixin.qq.com/s/_Je5_5_HqBcs5chvH5SFfA',
                'https://mp.weixin.qq.com/s/79NsKhMHbg09Y0xaybTXjA',
                'https://mp.weixin.qq.com/s/HTM47mUp0GF-tWXkPeZJlg',
                'https://mp.weixin.qq.com/s/8bljTUplPh1q4MXb6wd_gg',
                'https://mp.weixin.qq.com/s/djwW3S9FUYBE2L5Hj94a3A',
                'https://wsjkw.sh.gov.cn/xwfb/20220405/4c6aec72ef47453ba2a5643fad214b2a.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220404/ff41c17c2bec4154b800f22040d3754a.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220402/e4dfcc8e58b14b3e8dab46d60ff6d767.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220401/8c101d231d5644df8ed92d6bdbfab236.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220331/e86a298aecdf4e94b1796089e943054b.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220330/8d4f5179f1ef43da91c2d63cd906bfeb.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220329/b7430a2b3e04483c9d7ac6e4f4d4cf68.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220328/12b074e3958e448ab6bfb52e739d1d1e.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220327/09cfe78deb4041098d0042010fabdfeb.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220326/ff80e7e71f00478abf80a7d057e1683b.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220325/a76fbb6a18f542cda80fa9a9a4b08dd3.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220324/a8643ae53c7644f597cd88b8f2f4d8c4.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220323/dd54a58cdf524a51af5ba113adc6730f.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220322/b5bf11c3ef924f2e9d292ad14b0f3403.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220321/2cda1b24b5304d118352bdfd32af0aa4.html',
                'https://wsjkw.sh.gov.cn/xwfb/20220320/f9f1683cf055471fb1a67b8586e36660.html']
        for url in urls:
            filename = url_to_filename(url)
            assert 'https' not in filename
            logger.debug(filename)


HeaderUnitTests().run()
