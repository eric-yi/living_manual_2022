#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os.path

from header import *
import argparse
import signal
import json


class ServiceStatus(Enum):
    IDLE = 'idle'
    RUNNING = 'running'


def color_print(s):
    print(color_line(s, offset=4, border=True))


class Service:
    def __init__(self, name='service', command=None):
        self.name = name
        self.command = command
        self.pid_path = os.path.join(WORKDIR, f'.living_manual_at_2022_{name}_pid')
        self.info = None
        self.status = ServiceStatus.IDLE
        self.parameters = {}

    def start(self):
        self.status = ServiceStatus.RUNNING
        self._print_action_('start')
        if os.path.isfile(self.pid_path):
            logger.warning(f'{self.name} is running')
            return
        self.info = shell(self.command, waiting=False)
        if self.info is not None:
            pid = str(self.info.pid)
            logger.info(f'start {self.name} at {pid}')
            with open(self.pid_path, 'w') as pid_file:
                pid_file.write(pid)

    def stop(self):
        self._print_action_('stop')
        if os.path.exists(self.pid_path):
            with open(self.pid_path, 'r') as pid_file:
                pid = int(pid_file.read())
            if pid is not None:
                logger.info(f'stop {self.name} at {pid}')
                try:
                    os.kill(pid, signal.SIGTERM)
                    os.remove(self.pid_path)
                except Exception as e:
                    logger.error(e)
        else:
            logger.warning(f'{self.name} is not running')
        self.status = ServiceStatus.IDLE

    def restart(self):
        self.stop()
        self.start()

    def _print_action_(self, action):
        color_print(f'{action} {self.name}')


class JupyterService(Service):
    def __init__(self):
        super().__init__('notebook', 'jupyter lab --ip=0.0.0.0')


class DBSetting:
    def __init__(self):
        db_dir = os.path.join(os.path.dirname(__file__), 'db')
        self.living_vendor_db_dir = os.path.join(db_dir, 'living_vendor')
        self.living_map_db_dir = os.path.join(db_dir, 'living_map')
        self.living_vendor_db_file = os.path.join(self.living_vendor_db_dir, 'living_vendor.db')
        self.living_map_db_file = os.path.join(self.living_vendor_db_dir, 'living_map')

    def update_living_vendor(self):
        color_print('update_living_vendor')
        DBSetting.update_scheme(self.living_vendor_db_dir)

    def update_living_map(self):
        color_print('update_living_map')
        DBSetting.update_scheme(self.living_map_db_dir)

    def alter_living_vendor(self, desc):
        color_print(f'alter_living_vendor: {desc}')
        DBSetting.alter_scheme(self.living_vendor_db_dir, desc)
        DBSetting.after_alter_print(self.living_vendor_db_dir)

    def alter_living_map(self, desc):
        color_print(f'alter_living_map: {desc}')
        DBSetting.alter_scheme(self.living_map_db_dir, desc)
        DBSetting.after_alter_print(self.living_map_db_dir)

    def rm_living_vendor(self):
        if os.path.exists(self.living_vendor_db_file):
            os.remove(self.living_vendor_db_file)

    def rm_living_map(self):
        if os.path.exists(self.living_map_db_file):
            os.remove(self.living_map_db_file)

    @staticmethod
    def after_alter_print(db_dir):
        scheme_dir = os.path.join(db_dir, 'scheme', 'versions')
        color_print(f'generate file under {scheme_dir}, edit it')

    @staticmethod
    def update_scheme(cwd):
        # shell('alembic current', cwd=cwd, waiting=True)
        # shell('alembic history', cwd=cwd, waiting=True)
        shell('alembic upgrade head', cwd=cwd, waiting=True)
        # shell('alembic current', cwd=cwd, waiting=True)

    @staticmethod
    def alter_scheme(cwd, desc):
        shell(f'alembic revision -m "{desc} table"', cwd=cwd, waiting=True)


db_setting = DBSetting()


class SchemeService(Service):
    def __init__(self):
        super().__init__('scheme')
        self.db_list = ['living_vendor', 'living_map']
        self.db = None
        self.build = None

    def update(self):
        if self.db is not None and self.db in self.db_list:
            if self.build is not None:
                op = getattr(db_setting, f'alter_{self.db}')
                op(self.build)
            else:
                op = getattr(db_setting, f'update_{self.db}')
                op()


class DBService(Service):
    def __init__(self):
        super().__init__('db')

    def start(self):
        self._print_action_('start')
        db_setting.update_living_vendor()
        db_setting.update_living_map()

    def stop(self):
        self._print_action_('stop')
        db_setting.rm_living_vendor()
        db_setting.rm_living_map()


class CrawlerService(Service):
    def __init__(self):
        super.__init__('crawler')


def run(args):
    service = None
    if args.name == 'notebook':
        service = JupyterService()
    if args.name == 'crawler':
        service = CrawlerService()
    if args.name == 'db':
        service = DBService()
    if args.name == 'scheme':
        service = SchemeService()
    if service is not None:
        if args.p is not None:
            for k, v in json.loads(args.p).items():
                service.__setattr__(k, v)
        call_of_service = getattr(service, args.action)
        call_of_service()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', choices=['notebook', 'crawler', 'db', 'scheme'], help='service name')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'update'], help='service action')
    parser.add_argument('-p', help='parameters')
    args = parser.parse_args()
    print(args)
    run(args)
