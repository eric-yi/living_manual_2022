#!/bin/env python
# -*- coding: utf-8 -*- #

from etl_factory import ETLFactory
from report import MapView, MapInfoView, MapMarkerView, SummaryView, ResidentView, VendorView
from manual import generate_manual
from header import *
from living_vendor_db import get_vendors, living_vendor_db
from living_map_db import get_summaries, get_residents, districts as map_districts


class Tips:
    def __init__(self, manual_path, timer):
        self.manual_path = manual_path
        self.timer = timer
        self.label_color = TermStyle.YELLOW2
        self.line_color = TermStyle.BLUE2
        self.offset = 4

    @property
    def prefix(self):
        prefix_tips = [
            'Living Manual Gather Start'
        ]
        return color_lines('\n'.join(prefix_tips), label_color=self.label_color, line_color=self.line_color,
                           offset=self.offset)

    @property
    def postfix(self):
        postfix_tips = [
            'Living Manual Gather Start',
            f'elapse {self.timer.elapse()}',
            f'manual in {self.manual_path}'
        ]
        print(color_lines('\n'.join(postfix_tips), label_color=self.label_color, line_color=self.line_color,
                          offset=self.offset))


def clear():
    living_vendor_db.clear_data()


def published_date_from(published_date):
    date_list = published_date.split(' ')
    if len(date_list) > 0:
        return date_list[0]
    return published_date


def generate_map_info_view(summaries):
    city = ''
    districts = []
    if len(summaries) > 0:
        sorted_summaries = sorted(summaries, key=lambda summary: summary.published_at.val, reverse=True)
        published_date = sorted_summaries[0].published_at.val
        last_summaries = list(filter(lambda summary: summary.published_at == published_date, sorted_summaries))
        if len(last_summaries) > 0:
            for summary in last_summaries:
                if summary.district_code.val == '31':
                    city = summary.origin_desc.val
                    continue
                origin_desc = summary.origin_desc.val
                origin_desc_list = origin_desc.split('，')
                if len(origin_desc_list) > 2:
                    origin_desc = f'{origin_desc_list[1]}，{origin_desc_list[2]}'
                districts.append(origin_desc)
    map_info_view = MapInfoView(
        city=city,
        districts=districts
    )
    return map_info_view


def generate_map_marker_views(residents):
    map_marker_views = []
    for resident in residents:
        info = ''
        published_date = published_date_from(resident.published_at.val)
        if len(published_date) > 0:
            info = f'{published_date}上海发布'
        marker_view = MapMarkerView(
            name=resident.address.val,
            coord=f'{resident.longitude.val},{resident.latitude.val}',
            info=info
        )
        map_marker_views.append(marker_view)
    return map_marker_views


def generate_map_view(center, residents):
    markers = generate_map_marker_views(residents)
    map_view = MapView(
        center=center,
        markers=markers
    )
    return map_view


def generate_summary_views(summaries):
    summary_views = []
    for summary in summaries:
        summary_view = SummaryView(
            published_date=published_date_from(summary.published_at.val),
            district=summary.district.name.val,
            diagnosed=summary.diagnosed.val,
            asymptomatic=summary.asymptomatic.val,
        )
        summary_views.append(summary_view)
    return summary_views


def generate_resident_views(residents):
    resident_views = []
    for resident in residents:
        resident_view = ResidentView(
            published_date=published_date_from(resident.published_at.val),
            district=resident.district.name.val,
            address=resident.address.val,
        )
        resident_views.append(resident_view)
    return resident_views


def generate_vendor_views():
    vendors = get_vendors()
    vendor_views = []
    for vendor in vendors:
        district = ''
        if len(vendor.districts) > 0:
            district = ', '.join(list(map(lambda d: d.name.val, vendor.districts)))
        vendor_view = VendorView(
            district=district,
            name=vendor.name.val,
            contact=vendor.contact.val,
            address=vendor.address.val,
            mobile=vendor.mobile.val,
            desc=vendor.desc.val,
            origin=vendor.origin.val,
            available_desc=vendor.available_desc.val,
            available_date=vendor.available_time.val if vendor.available_time.val is not None else '',
            link=vendor.link.val,
            record_date=vendor.created_at.val,
            tag=','.join(list(map(lambda tag: tag.name.val, vendor.tags))),
        )
        vendor_views.append(vendor_view)
    return vendor_views


def generate(**filter):
    conditions = {}
    district = None
    center = '121.473667,31.230525'
    if 'district' in filter:
        district = filter['district']
        for map_district in map_districts:
            if map_district.name == district:
                conditions['district_code'] = map_district.code.val
                center = DISTRICTS_COORD_MAPPING[district]
                break
    manual_path = html_filepath(district)
    tips = Tips(manual_path, Timer())
    print(tips.prefix)
    ETLFactory().build()
    summaries = get_summaries()
    residents = get_residents(**conditions)
    map_info_view = generate_map_info_view(summaries)
    map_view = generate_map_view(center, residents)
    summary_views = generate_summary_views(summaries)
    resident_views = generate_resident_views(residents)
    vendor_views = generate_vendor_views()
    generate_manual(manual_path, map_info_view, map_view, summary_views, resident_views, vendor_views)
    print(tips.postfix)
    # import webbrowser
    # webbrowser.open(f'file://{manual_path}')


def run(districts=[]):
    if districts:
        for district in districts:
            generate(district=district)
    else:
        generate()


if __name__ == '__main__':
    print(color_slogan())
    clear()
    for district in DISTRICTS_COORD_MAPPING:
        run([district])
