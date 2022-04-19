#!/usr/bin/evn python
# -*- coding:utf-8 -*-

from db import *


class LivingVendorDB(DB):
    def __init__(self):
        super().__init__(os.path.join(DB_DIR, 'living_vendor', 'living_vendor.db'))
        self.tables = {
            'vendor': 'delete',
            'vendor_tag': 'delete',
            'cart': 'delete',
            'cart_goods': 'delete',
            'product': 'delete',
            'vendor_district': 'delete',
            'district': 'drop',
            'tag': 'drop',
            'category': 'drop',
        }


living_vendor_db = LivingVendorDB()


class District(Entity):
    def __init__(self):
        super().__init__(living_vendor_db, 'district')
        self.name = Entity.Column('')
        self.code = Entity.Column('')


districts = District().all


class Vendor(Entity):
    def __init__(self):
        super().__init__(living_vendor_db, 'vendor')
        self.name = Entity.Column('')
        self.contact = Entity.Column('')
        self.address = Entity.Column('')
        self.mobile = Entity.Column('')
        self.tel = Entity.Column('')
        self.desc = Entity.Column('')
        self.wechat = Entity.Column('')
        self.origin = Entity.Column('')
        self.available_desc = Entity.Column('')
        self.available_time = Entity.Column(None)
        self.input_path = Entity.Column('')
        self.input_type = Entity.Column('')
        self.link = Entity.Column('')
        self.districts = []
        self.tags = []


class Tag(Entity):
    def __init__(self):
        super().__init__(living_vendor_db, 'tag')
        self.name = Entity.Column('')


class VendorTag(Entity):
    def __init__(self):
        super().__init__(living_vendor_db, 'vendor_tag')
        self.vendor_id = Entity.Column(-1)
        self.tag_id = Entity.Column(-1)


class Cart(Entity):
    def __init__(self):
        super().__init__(living_vendor_db, 'cart')
        self.vendor_id = Entity.Column(-1)


class CartGoods(Entity):
    def __init__(self):
        super().__init__(living_vendor_db, 'cart_goods')
        self.cart_id = Entity.Column(-1)
        self.goods_id = Entity.Column(-1)


class Goods(Entity):
    def __init__(self):
        super().__init__(living_vendor_db, 'goods')
        self.product_id = Entity.Column(-1)
        self.amount = Entity.Column(-1)


class Product(Entity):
    def __init__(self):
        super().__init__(living_vendor_db, 'product')
        self.name = Entity.Column('')
        self.manufacturer = Entity.Column('')
        self.origin = Entity.Column('')
        self.production_date = Entity.Column(None)
        self.shelf_life = Entity.Column('')
        self.desc = Entity.Column('')
        self.category_id = Entity.Column(-1)


class VendorDistrict(Entity):
    def __init__(self):
        super().__init__(living_vendor_db, 'vendor_district')
        self.vendor_id = Entity.Column(-1)
        self.district_code = Entity.Column('')


def get_vendors(limit=-1):
    if limit == -1:
        vendors = Vendor().all
    else:
        vendors = Vendor().find_by_limit(limit)
    for vendor in vendors:
        vendor_district_list = VendorDistrict().find(vendor_id=vendor.id.val)
        for vendor_district in vendor_district_list:
            vendor.districts.extend(District().find(code=vendor_district.district_code.val))
        vendor_tag_list = VendorTag().find(vendor_id=vendor.id.val)
        for vendor_tag in vendor_tag_list:
            vendor.tags.append(Tag().get(vendor_tag.tag_id))
    return vendors


class LivingVendorDBUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    @UnitTests.skip
    def insert_test(self):
        living_vendor_db.insert('test', id='2')
        dataset = living_vendor_db.query('select * from test')
        assert len(dataset) > 0
        print(dataset)

    @UnitTests.skip
    def query_test(self):
        dataset = living_vendor_db.find('test')
        assert len(dataset) > 0
        print(dataset)
        id = living_vendor_db.get('test', 1)[0]
        assert id == 1
        print(id)

    @UnitTests.skip
    def vendor_save_test(self):
        vendor = Vendor()
        vendor.name.set('vendor')
        vendor.save()
        data = living_vendor_db.get_last('vendor')
        print(vendor)
        assert vendor.id.val == data[0]
        print(data)
        living_vendor_db.delete('vendor')

    # @UnitTests.skip
    def get_scheme_test(self):
        scheme = living_vendor_db.get_scheme('vendor')
        assert len(scheme) > 0
        logger.debug(scheme)
        vendor_scheme = Vendor().scheme
        assert len(scheme) == len(vendor_scheme)

    @UnitTests.skip
    def entity_fields_test(self):
        fields = Vendor().fields
        assert len(fields) > 0
        logger.debug(fields)

    @UnitTests.skip
    def all_entities_test(self):
        vendors = Vendor().all
        assert len(vendors) > 0
        logger.debug(vendors[-1])

    @UnitTests.skip
    def get_all_vendors_test(self):
        vendors = get_vendors()
        if len(vendors) > 0:
            logger.debug(vendors[0])

    @UnitTests.skip
    def districts_test(self):
        assert len(districts) > 0
        logger.debug(districts)


LivingVendorDBUnitTests().run()
