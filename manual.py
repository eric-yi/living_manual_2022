#!/usr/bin/env python
# -*- coding:utf-8 -*-
from report import *
import htmlmin


class HtmlBuilder:
    class Tpl:
        def __init__(self, name, report_cls=None, views=None):
            self.name = name
            self.report_cls = report_cls
            self.views = views

        def __repr__(self):
            return str(self.__dict__)

    class Label:
        def __init__(self, name):
            self.prefix = f'<!--{name} {{'
            self.suffix = '}} -->'

        def __repr__(self):
            return str(self.__dict__)

        def find(self, line):
            prefix_position = line.find(self.prefix)
            if prefix_position > -1:
                suffix_position = line.find(self.suffix)
                return (prefix_position, prefix_position + len(self.prefix) + 1, suffix_position,
                        suffix_position + len(self.suffix))
            return False

    JS_LABEL = Label('js')
    CSS_LABEL = Label('css')
    HTML_LABEL = Label('html')
    TPL_LABEL = Label('tpl')

    def __init__(self):
        self.name = 'living_manual'
        self.tpl_layout_filepath = os.path.join(TEMPlATE_DIR, f'{self.name}_layout.tpl')
        self.tpl_layout = read(self.tpl_layout_filepath)
        self.tpl_list = []
        for line in self.tpl_layout.splitlines():
            positions = self.TPL_LABEL.find(line)
            if positions:
                _, position, offset, _ = positions
                self.tpl_list.append(HtmlBuilder.Tpl(line[position:offset]))

        self.tpl_map_filepath = os.path.join(TEMPlATE_DIR, f'{self.name}_map.tpl')
        self.tpl_summary_filepath = os.path.join(TEMPlATE_DIR, f'{self.name}_summary.tpl')
        self.tpl_resident_filepath = os.path.join(TEMPlATE_DIR, f'{self.name}_resident.tpl')
        self.tpl_vendor_filepath = os.path.join(TEMPlATE_DIR, f'{self.name}_vendor.tpl')

    def attach(self, tpl_name, report_cls=None, views=None):
        for tpl in self.tpl_list:
            if tpl.name == tpl_name:
                tpl.report_cls = report_cls
                tpl.views = views
                break

    def build(self):
        return self._build_tpl_(self.tpl_layout)

    def _build_tpl_(self, tpl, ignore_tpl=False):
        htmls = []
        for line in tpl.splitlines():
            positions = self.JS_LABEL.find(line)
            if positions:
                js = self._replace_html_label_(line, positions, 'js', '<script type="text/javascript">',
                                               '</script>')
                htmls.extend(js)
                continue
            positions = self.CSS_LABEL.find(line)
            if positions:
                css = self._replace_html_label_(line, positions, 'css', '<style>', '</style>')
                htmls.extend(css)
                continue
            positions = self.HTML_LABEL.find(line)
            if positions:
                html = self._replace_html_label_(line, positions, 'html')
                htmls.extend(html)
                continue
            if not ignore_tpl:
                positions = self.TPL_LABEL.find(line)
                if positions:
                    _, position, offset, _ = positions
                    tpl_name = line[position:offset]
                    for tpl in self.tpl_list:
                        if tpl.name == tpl_name:
                            tpl_lines = read(os.path.join(TEMPlATE_DIR, f'{tpl_name}.tpl'))
                            tpl_lines = self._build_tpl_(tpl_lines, True)
                            if tpl.report_cls is not None and tpl.views is not None:
                                report = tpl.report_cls(tpl_lines, tpl.views)
                                tpl_lines = report.generate()
                            htmls.append(tpl_lines)
                            break
                    continue
            htmls.append(line)
        return '\n'.join(htmls)

    def _replace_html_label_(self, line, positions, file_suffix, header='', ender=''):
        lines = []
        mark, position, offset, capacity = positions
        js_line = f'{line[:mark]}{header}'
        lines.append(js_line)
        js = read(os.path.join(TEMPlATE_DIR, f'{line[position:offset]}.{file_suffix}'))
        lines.append(js)
        js_line = f'{ender}{line[capacity:]}'
        lines.append(js_line)
        return lines


def generate_manual(html_path, map_info_view, map_view, summary_views, resident_views, vendor_views):
    html_builder = HtmlBuilder()
    html_builder.attach('living_manual_map', MapInfoReport, map_info_view)
    html_builder.attach('living_manual_summary', SummariesReport, summary_views)
    html_builder.attach('living_manual_resident', ResidentsReport, resident_views)
    html_builder.attach('living_manual_vendor', VendorsReport, vendor_views)
    html_builder.attach('living_manual_map_script', MapReport, map_view)
    manual_html = html_builder.build()
    html = htmlmin.minify(manual_html, remove_empty_space=True)
    write(html_path, html)


class ManualUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    def _setup_(self):
        import random

        def generate_value():
            num = random.randint(3, 10)
            value = ''
            for _ in range(num):
                c = chr(random.randint(97, 122))
                value += c
            return value

        self.vendor_views = []
        for _ in range(5):
            view = VendorView(
                district=generate_value(),
                name=generate_value(),
                contact=generate_value(),
                address=generate_value(),
                mobile=generate_value(),
                category=generate_value(),
                desc=generate_value(),
            )
            self.vendor_views.append(view)

        self.resident_views = []
        for _ in range(5):
            view = ResidentView(
                district=generate_value(),
                name=generate_value(),
                contact=generate_value(),

            )
            self.resident_views.append(view)

    @UnitTests.skip
    def generate_and_save_manual_test(self):
        html_path = html_filepath()
        generate_manual(html_path, [], self.resident_views, self.vendor_views)
        assert os.path.exists(html_path)
        logger.debug(html_path)

    @UnitTests.skip
    def html_builder_test(self):
        builder = HtmlBuilder()
        assert len(builder.tpl_list) > 0
        logger.debug(builder.tpl_list)
        html = builder.build()
        assert '<html' in html
        logger.debug(html)


ManualUnitTests().run()
