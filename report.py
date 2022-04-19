#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os.path

from header import *


class TplNode:
    class Trait(Enum):
        ROOT = 'root'
        LINE_TRUNK = 'line-trunk'
        LOGIC_TRUNK = 'logic_trunk'
        BEGIN = 'begin'
        END = 'end'
        STR = 'str'
        NEWLINE = 'newline'

    def __init__(self, trait, value=''):
        self.trait = trait
        self.value = value
        self.parent = None
        self.children = []

    def add(self, child):
        child.parent = self
        self.children.append(child)

    @property
    def last_child(self):
        if len(self.children) == 0:
            return None
        return self.children[-1]

    @property
    def left_is_begin(self):
        if self.is_root:
            return False
        i = self.parent.children.index(self)
        if i > 0:
            return self.parent.children[i - 1].is_begin
        return False

    @property
    def left_is_str(self):
        if self.is_root:
            return False
        i = self.parent.children.index(self)
        if i > 0:
            return self.parent.children[i - 1].is_str
        return False

    @property
    def begin_ahead(self):
        if self.is_root:
            return False
        i = self.parent.children.index(self)
        i -= 1
        while i >= 0:
            if self.parent.children[i].is_end:
                return False
            if self.parent.children[i].is_begin:
                return True
            i -= 1
        return False

    @property
    def trunk_ahead(self):
        if self.is_root:
            return False
        i = self.parent.children.index(self)
        i -= 1
        while i >= 0:
            if self.parent.children[i].is_end:
                return False
            if self.parent.children[i].is_trunk:
                return True
            i -= 1
        return False

    @property
    def right_is_trunk(self):
        if self.is_root:
            return False
        if self.is_begin:
            i = self.parent.children.index(self)
            return self.parent.children[i + 1].is_trunk

        return False

    @property
    def right_is_logic_trunk(self):
        if self.is_root:
            return False
        if self.is_begin:
            i = self.parent.children.index(self)
            return self.parent.children[i + 1].is_logic_trunk

        return False

    @property
    def is_begin(self):
        return self.trait == TplNode.Trait.BEGIN

    @property
    def is_end(self):
        return self.trait == TplNode.Trait.END

    @property
    def is_str(self):
        return self.trait == TplNode.Trait.STR

    @property
    def is_root(self):
        return self.trait == TplNode.Trait.ROOT

    @property
    def is_logic_trunk(self):
        return self.trait == TplNode.Trait.LOGIC_TRUNK

    @property
    def is_trunk(self):
        return self.trait == TplNode.Trait.LOGIC_TRUNK or self.trait == TplNode.Trait.LINE_TRUNK

    @property
    def is_newline(self):
        return self.trait == TplNode.Trait.NEWLINE

    @property
    def _dict_(self):
        d = {}
        for k, v in self.__dict__.items():
            if k != 'parent':
                d[k] = v
        return d

    def to_json(self):
        return json.dumps(self._dict_, cls=ObjectEncoder, indent=2)

    def __repr__(self):
        return str(self._dict_)

    @staticmethod
    def ROOT():
        return TplNode(TplNode.Trait.ROOT)

    @staticmethod
    def TRUNK():
        return TplNode(TplNode.Trait.LOGIC_TRUNK)

    @staticmethod
    def LINE_TRUNK():
        return TplNode(TplNode.Trait.LINE_TRUNK)

    @staticmethod
    def END():
        return TplNode(TplNode.Trait.END)

    @staticmethod
    def NEWLINE():
        return TplNode(TplNode.Trait.NEWLINE)


class Report:
    def __init__(self, name, tpl, views):
        self.name = name
        self.views = views
        self.lines = tpl.splitlines()
        self.prefix = '<!-- {{'
        self.suffix = '}} -->'

    def generate(self):
        node = self._parse_tpl_()
        code = self._make_code_(node)
        return self._run_code_(code)

    def _parse_tpl_(self):
        root = TplNode.ROOT()
        node = root
        for i, line in enumerate(self.lines):
            next_is_end = False
            if (i + 1) < len(self.lines):
                next_line = self.lines[i + 1]
                if self.prefix not in next_line and self.suffix in next_line:
                    next_is_end = True
            node = self._parse_tpl_line_(node, line, next_is_end)

        return root

    def _parse_tpl_line_(self, node, line, next_is_end=False):
        if self.prefix in line and self.suffix in line:
            line_trunk_node = TplNode.LINE_TRUNK()
            node.add(line_trunk_node)
            node = line_trunk_node
        elif not node.is_root and self.prefix in line:
            trunk_node = TplNode.TRUNK()
            node.add(trunk_node)
            node = trunk_node
        prefix_position = line.find(self.prefix)
        suffix_position = line.find(self.suffix)
        if prefix_position > -1:
            if prefix_position > 0:
                str_node = TplNode(TplNode.Trait.STR, line[0:prefix_position])
                node.add(str_node)
            prefix_capacity = suffix_position if suffix_position > -1 else len(line)
            prefix_value = line[prefix_position + len(self.prefix):prefix_capacity].strip()
            begin_node = TplNode(TplNode.Trait.BEGIN, prefix_value)
            node.add(begin_node)
        if suffix_position > -1:
            suffix_capacity = suffix_position + len(self.suffix)
            end_node = TplNode.END()
            node.add(end_node)
            if suffix_capacity < len(line):
                str_node = TplNode(TplNode.Trait.STR, line[suffix_capacity:len(line)])
                node.add(str_node)
            node.add(TplNode.NEWLINE())
            if node.is_trunk:
                node = node.parent
        if self.prefix not in line and self.suffix not in line:
            up = False
            if node.last_child is not None and (node.last_child.is_begin or next_is_end):
                up = True
                line_trunk_node = TplNode.LINE_TRUNK()
                node.add(line_trunk_node)
                node = line_trunk_node
            str_node = TplNode(TplNode.Trait.STR, line)
            node.add(str_node)
            node.add(TplNode.NEWLINE())
            if up:
                node = node.parent
        return node

    class CodeLevel:
        def __init__(self, code, level):
            self.code = code
            self.level = level

        @property
        def sentence(self):
            return ''.join(['\t' for _ in range(self.level)]) + self.code

    def _make_code_(self, node):
        codes = [
            Report.CodeLevel(f'def generate_{self.name}_html({self.name}):', 0),
            Report.CodeLevel('html = []', 1),
        ]
        level = 1
        for child in node.children:
            self._make_code_by_node_(child, level, codes)
        codes.append(Report.CodeLevel('return \'\'.join(html)', 1))
        return '\n'.join(code.sentence for code in codes)

    def _make_code_by_node_(self, node, level, codes):
        if node.is_begin:
            code = node.value
            if node.right_is_trunk:
                code += ':'
                code = code.replace('\'', '\\.')
                codes.append(Report.CodeLevel(f'{code}', level))
                level += 1
            else:
                codes.append(Report.CodeLevel(f'html.append({code})', level))
        if node.begin_ahead:
            level += 1
        if node.is_end:
            level -= 1
        if node.is_str:
            code = node.value
            code = code.replace('\'', '\\\'')
            codes.append(Report.CodeLevel(f'html.append(\'{code}\')', level))
        if node.is_newline:
            codes.append(Report.CodeLevel(f'html.append(\'\\n\')', level))
        for child in node.children:
            self._make_code_by_node_(child, level, codes)

    def _run_code_(self, code):
        html = None
        locals = {
            'html': html,
            self.name: self.views
        }
        code += f'\nhtml = generate_{self.name}_html({self.name})'
        exec(code, None, locals)
        return locals['html']


class MapInfoView:
    def __init__(self, **kwargs):
        self.city = kwargs['city'] if 'city' in kwargs else ''
        self.districts = kwargs['districts'] if 'districts' in kwargs else []

    def __repr__(self):
        return str(self.__dict__)


class MapInfoReport(Report):
    def __init__(self, tpl, view):
        super().__init__('map_info', tpl, [view])


class MapMarkerView:
    def __init__(self, **kwargs):
        self.name = kwargs['name'] if 'name' in kwargs else ''
        self.coord = kwargs['coord'] if 'coord' in kwargs else ''
        self.info = kwargs['info'] if 'info' in kwargs else ''

    def __repr__(self):
        return str(self.__dict__)


class MapMarkersReport(Report):
    def __init__(self, tpl, views):
        super().__init__('map_markers', tpl, views)


class MapView:
    def __init__(self, **kwargs):
        self.center = kwargs['center'] if 'center' in kwargs else ''
        self.markers = kwargs['markers'] if 'markers' in kwargs else []

    def __repr__(self):
        return str(self.__dict__)


class MapReport(Report):
    def __init__(self, tpl, view):
        super().__init__('map', tpl, [view])


class SummaryView:
    def __init__(self, **kwargs):
        self.published_date = kwargs['published_date'] if 'published_date' in kwargs else ''
        self.district = kwargs['district'] if 'district' in kwargs else ''
        self.diagnosed = kwargs['diagnosed'] if 'diagnosed' in kwargs else 0
        self.asymptomatic = kwargs['asymptomatic'] if 'asymptomatic' in kwargs else 0

    def __repr__(self):
        return str(self.__dict__)


class SummariesReport(Report):
    def __init__(self, tpl, views):
        super().__init__('summaries', tpl, views)


class ResidentView:
    def __init__(self, **kwargs):
        self.published_date = kwargs['published_date'] if 'published_date' in kwargs else ''
        self.district = kwargs['district'] if 'district' in kwargs else ''
        self.address = kwargs['address'] if 'address' in kwargs else ''

    def __repr__(self):
        return str(self.__dict__)


class ResidentsReport(Report):
    def __init__(self, tpl, views):
        super().__init__('residents', tpl, views)


class VendorView:
    def __init__(self, **kwargs):
        self.district = kwargs['district'] if 'district' in kwargs else ''
        self.name = kwargs['name'] if 'name' in kwargs else ''
        self.contact = kwargs['contact'] if 'contact' in kwargs else ''
        self.address = kwargs['address'] if 'address' in kwargs else ''
        self.mobile = kwargs['mobile'] if 'mobile' in kwargs else ''
        self.category = kwargs['category'] if 'category' in kwargs else ''
        self.desc = kwargs['desc'] if 'desc' in kwargs else ''
        self.origin = kwargs['origin'] if 'origin' in kwargs else ''
        self.order_type = kwargs['order_type'] if 'order_type' in kwargs else ''
        self.link = kwargs['link'] if 'link' in kwargs else ''
        self.available_desc = kwargs['available_desc'] if 'available_desc' in kwargs else ''
        self.available_date = kwargs['available_date'] if 'available_date' in kwargs else ''
        self.record_date = kwargs['record_date'] if 'record_date' in kwargs else ''
        self.tag = kwargs['tag'] if 'tag' in kwargs else ''

    def __repr__(self):
        return str(self.__dict__)


class VendorsReport(Report):
    def __init__(self, tpl, views):
        super().__init__('vendors', tpl, views)


class ReportUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    def _setup_(self):
        vendors_tpl = '''
        <button id="export" onclick="export_excel('residentlist', 'residents')">导出</button>
        <table>
        <!-- {{ for i, vendor in enumerate(vendors) 
        <tr>
            <td align="left" valign="bottom" class="heading"><!-- {{ '{}'.format(i+1) }} --></td>
            <td align="right" valign="bottom" class="district"><b><!-- {{ '{}'.format(vendor.district) }} --></b></td>
            <td align="right" valign="bottom" class="vendor"><b><!-- {{ '{}'.format(vendor.name) }} --></b></td>
            <td align="right" valign="bottom" class="contact"><b><!-- {{ '{}'.format(vendor.contact) }} --></b></td>
            <td align="right" valign="bottom" class="address"><b><!-- {{ '{}'.format(vendor.address) }} --></b></td>
            <td align="right" valign="bottom" class="mobile"><b><!-- {{ '{}'.format(vendor.mobile) }} --></b></td>
            <td align="right" valign="bottom" class="category"><b><!-- {{ '{}'.format(vendor.category) }} --></b></td>
            <td align="right" valign="bottom" class="desc"><b><!-- {{ '{}'.format(vendor.desc) }} --></b></td>
            <td align="right" valign="bottom" class="origin"><b><!-- {{ '{}'.format(vendor.origin) }} --></b></td>
            <td align="right" valign="bottom" class="order_type"><b><!-- {{ '{}'.format(vendor.order_type) }} --></b></td>
            <td align="right" valign="bottom" class="link"><b><!-- {{ '{}'.format(vendor.link) }} --></b></td>
            <td align="right" valign="bottom" class="available_date"><b><!-- {{ '{}'.format(vendor.available_date) }} --></b></td>
            <td align="right" valign="bottom" class="record_date"><b><!-- {{ '{}'.format(vendor.record_date) }} --></b></td>
            <td align="right" valign="bottom" class="tag"><b><!-- {{ '{}'.format(vendor.tag) }} --></b></td>
        </tr>
        }} -->
        </table>
        '''
        import random

        def generate_value():
            num = random.randint(3, 10)
            value = ''
            for _ in range(num):
                c = chr(random.randint(97, 122))
                value += c
            return value

        self.vendors = []
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
            self.vendors.append(view)
        self.vendors_report = VendorsReport(vendors_tpl, self.vendors)

        residents_tpl = '''
          <table>
          <!-- {{ for i, vendor in enumerate(vendors) 
          <tr>
            <td align="left" valign="bottom" class="heading"><!-- {{ '{}'.format(i+1) }} --></td>
            <td align="right" valign="bottom" class="district"><!-- {{ '{}'.format(resident.district) }} --></td>
            <td align="right" valign="bottom" class="address"><!-- {{ '{}'.format(resident.address) }} --></td>
            <td align="right" valign="bottom" class="published_date"><!-- {{ '{}'.format(resident.published_date) }} --></td>
          </tr>
          }} -->
          </table>
          '''
        self.residents = []
        for _ in range(5):
            view = ResidentView(
                district=generate_value(),
                name=generate_value(),
                contact=generate_value(),

            )
            self.residents.append(view)
        self.residents_report = ResidentsReport(residents_tpl, self.residents)

        markers_tpl = '''
<script>
    var LabelsData = [
    <!-- {{ for i, marker in enumerate(markers)
        {
            name: '<!-- {{ '{}'.format(marker.name) }} -->',
            position: [<!-- {{ '{}'.format(marker.coord) }} -->],
            zooms: [10, 20],
            opacity: 1,
            zIndex: 10,
            icon: {
                type: 'image',
                image: 'https://a.amap.com/jsapi_demos/static/images/poi-marker.png',
                clipOrigin: [14, 270],
                clipSize: [50, 68],
                size: [25, 34],
                anchor: 'bottom-center',
                angel: 0,
                retina: true
            },
            text: {
                content: 'test',
                direction: 'left',
                offset: [0, -5],
                style: {
                    fontSize: 11,
                    fontWeight: 'normal',
                    fillColor: 'red',
                    strokeColor: '#fff',
                    strokeWidth: 2,
                }
            }
        },
    }} -->
    ]

    var marker, map = new AMap.Map('container', {
        resizeEnable: true,
        zoom:13,
        center: [121.473667,31.230525]
    });

    var layer = new AMap.LabelsLayer({
        zooms: [3, 20],
        zIndex: 1000,
        // 开启标注避让，默认为开启，v1.4.15 新增属性
        collision: true,
        // 开启标注淡入动画，默认为开启，v1.4.15 新增属性
        animation: true,
    });

    map.add(layer);
    var markers = [];
    for (var i = 0; i < LabelsData.length; i++) {
        var curData = LabelsData[i];
        curData.extData = {
            index: i
        };
        var labelMarker = new AMap.LabelMarker(curData);
        labelMarker.on('mouseover', function(e){
            var position = e.data.data && e.data.data.position;
            if(position){
                normalMarker.setContent(
                    '<div class="amap-info-window">'
                        + '<!-- {{ '{}'.format(marker.info) }} -->' +
                        '<div class="amap-info-sharp"></div>' +
                    '</div>');
                normalMarker.setPosition(position);
                map.add(normalMarker);
            }
        });

        labelMarker.on('mouseout', function(){
            map.remove(normalMarker);
        });
        markers.push(labelMarker);
    }
    layer.add(markers);
    var normalMarker = new AMap.Marker({
        offset: new AMap.Pixel(-75, -80),
    });
    map.setFitView();
</script>
                  '''
        self.markers = []
        for _ in range(5):
            view = MapMarkerView(
                name=generate_value(),
                coord=generate_value(),
                info=generate_value()
            )
            self.markers.append(view)
        self.markers_report = MapMarkersReport(markers_tpl, self.markers)

    @UnitTests.skip
    def parse_vendors_tpl_line_test(self):
        root = TplNode.ROOT()

        def parse_tpl_line(line):
            node = self.vendors_report._parse_tpl_line_(root, line)
            assert node is not None
            logger.debug(node)
            logger.debug(node.to_json())

        parse_tpl_line('<!-- {{ for i, vendor in enumerate(vendors)')
        parse_tpl_line('<td align="left" valign="bottom" class="heading"><!-- {{ i }} --></td>')
        parse_tpl_line('}} -->')

    @UnitTests.skip
    def parse_vendors_tpl_test(self):
        root = self.vendors_report._parse_tpl_()
        assert root is not None
        logger.debug(root)
        logger.debug(root.to_json())

    @UnitTests.skip
    def make_vendors_code_test(self):
        node = self.vendors_report._parse_tpl_()
        code = self.vendors_report._make_code_(node)
        assert code is not ''
        logger.debug(code)

    @UnitTests.skip
    def make_residents_code_test(self):
        node = self.residents_report._parse_tpl_()
        code = self.residents_report._make_code_(node)
        assert code is not ''
        logger.debug(code)

    @UnitTests.skip
    def generate_vendor_html_report_test(self):
        html = self.vendors_report.generate()
        assert html is not None
        logger.debug(html)

    @UnitTests.skip
    def make_map_markers_code_test(self):
        node = self.markers_report._parse_tpl_()
        logger.debug(node.to_json())
        code = self.markers_report._make_code_(node)
        assert code is not ''
        logger.debug(code)

    # @UnitTests.skip
    def generate_map_markers_html_report_test(self):
        html = self.markers_report.generate()
        assert html is not None
        logger.debug(html)


ReportUnitTests().run()
