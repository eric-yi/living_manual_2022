#!/usr/bin/evn python
# -*- coding:utf-8 -*-

from db import *


class LivingMapDB(DB):
    def __init__(self):
        super().__init__(os.path.join(DB_DIR, 'living_map', 'living_map.db'))
        self.tables = {
            'resident_link': 'delete',
            'resident': 'delete',
            'resident_summary': 'delete',
            'district': 'drop'
        }


living_map_db = LivingMapDB()


class ResidentLink(Entity):
    def __init__(self):
        super().__init__(living_map_db, 'resident_link')
        self.published_at = Entity.Column('')
        self.origin = Entity.Column('')
        self.link = Entity.Column('')
        self.origin_filepath = Entity.Column('')

    @property
    def exist(self):
        return len(self.find(published_at=self.published_at.val)) > 0

    @property
    def jobs(self):
        return self.find(state=DB.Condition('<', 3))

    @property
    def inputs(self):
        return self.find(state=3)

    @property
    def not_save_origin(self):
        return self.state.val < 2

    @property
    def not_save_input(self):
        return self.state.val != 3

    def reset_state(self):
        self.state.set(1)
        self.update()

    def save_origin(self):
        self.state.set(2)
        self.update()

    def save_input(self):
        self.state.set(3)
        self.update()

    def reset_state_all(self):
        living_map_db.update(self.table_name, {'state': 1})


class Resident(Entity):
    def __init__(self):
        super().__init__(living_map_db, 'resident')
        self.published_at = Entity.Column('')
        self.origin = Entity.Column('')
        self.address = Entity.Column('')
        self.longitude = Entity.Column(0.0)
        self.latitude = Entity.Column(0.0)
        self.diagnosed = Entity.Column(0)
        self.asymptomatic = Entity.Column(0)
        self.link_id = Entity.Column(-1)
        self.summary_id = Entity.Column(-1)
        self.district_code = Entity.Column('')
        self.link = None
        self.summary = None
        self.district = District()

    @property
    def exist(self):
        return len(self.find(published_at=self.published_at.val, address=self.address.val)) > 0


class ResidentSummary(Entity):
    def __init__(self):
        super().__init__(living_map_db, 'resident_summary')
        self.published_at = Entity.Column('')
        self.origin = Entity.Column('')
        self.diagnosed = Entity.Column(0)
        self.asymptomatic = Entity.Column(0)
        self.district_code = Entity.Column('')
        self.district = District()
        self.origin_desc = Entity.Column('')

    @property
    def exist(self):
        return len(self.find(published_at=self.published_at.val, district_code=self.district_code.val)) > 0


class ResidentInput(Entity):
    def __init__(self):
        super().__init__(living_map_db, 'resident_input')
        self.path = Entity.Column('')
        self.link_id = Entity.Column(-1)
        self.resident = None

    def get_by_link(self, link_id):
        return self.get_by(link_id=link_id)


class District(Entity):
    def __init__(self):
        super().__init__(living_map_db, 'district')
        self.name = Entity.Column('')
        self.code = Entity.Column('')


districts = District().all


def get_residents(**conditions):
    if len(conditions) == 0:
        residents = Resident().all
    else:
        if 'limit' in conditions:
            residents = Resident().find_by_limit(conditions['limit'])
        else:
            residents = Resident().find(**conditions)
    for resident in residents:
        if len(resident.district_code.val) > 0:
            district = District()
            district.get_by(code=resident.district_code.val)
            resident.district = district
    return residents


def get_summaries(limit=-1):
    if limit == -1:
        summaries = ResidentSummary().all
    else:
        summaries = ResidentSummary().find_by_limit(limit)
    for summary in summaries:
        if len(summary.district_code.val) > 0:
            district = District()
            district.get_by(code=summary.district_code.val)
            summary.district = district
    return summaries


class LivingMapDBUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    @UnitTests.skip
    def districts_test(self):
        assert len(districts) > 0
        logger.debug(districts)

    @UnitTests.skip
    def resident_link_test(self):
        published_at = now()
        link = ResidentLink()
        link.published_at.set(published_at)
        link.link.set('404')
        link.save()
        logger.debug(link)
        assert link.exist is True
        link.delete()
        assert link.exist is False

    @UnitTests.skip
    def resident_jobs_test(self):
        link = ResidentLink()
        link_jobs = link.jobs
        assert type(link_jobs) is list
        logger.debug(len(link_jobs))

    @UnitTests.skip
    def resident_input_test(self):
        logger.debug(ResidentInput().all)
        resident_input = ResidentInput()
        resident_input.resident_id.set(1)
        resident_input.path.set('test')
        resident_input.save()
        resident_input_list = ResidentInput().all
        assert len(resident_input_list) > 0
        logger.debug(resident_input_list)
        resident_input.delete()
        resident_input_list = ResidentInput().all
        assert len(resident_input_list) == 0
        logger.debug(resident_input_list)

    @UnitTests.skip
    def resident_test(self):
        resident = Resident()
        scheme = resident.db.get_scheme(resident.table_name)
        print(scheme)
        resident_list = Resident().find_by_limit(1)
        if resident_list:
            resident = resident_list[0]
            assert resident.exist is True
            logger.debug(resident)
            resident.address.set(' ')
            logger.debug(resident)
            assert resident.exist is False

    # @UnitTests.skip
    def resident_summary_test(self):
        summary_list = ResidentSummary().all
        logger.debug(summary_list)
        if summary_list:
            summary = summary_list[0]
            assert summary.exist is True
            logger.debug(summary)
            summary.district_code.set(-1)
            assert summary.exist is False
        summary = ResidentSummary()
        summary.to_last()
        assert summary.id.val > 0
        sorted_summary_list = sorted(summary_list, key=lambda summary: summary.published_at.val,
                                     reverse=True)
        assert sorted_summary_list[0].id.val > 0


LivingMapDBUnitTests().run()
