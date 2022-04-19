#!/usr/bin/evn python
# -*- coding:utf-8 -*-

from header import *
import sqlite3


class DB:
    class Condition:
        def __init__(self, op, value):
            self.op = op
            self.val = value

        def __repr__(self):
            return str(self.__dict__)

    def __init__(self, db_file):
        self.db_con = sqlite3.connect(db_file)

    def find(self, table_name, **conditions):
        statement = self._statement_(table_name, 'select', **conditions)
        return self._select_(statement)

    def get_last(self, table_name):
        dataset = self._select_(f'select * from {table_name} order by id desc limit 1')
        if len(dataset) == 1:
            return dataset[0]
        return None

    def get(self, table_name, id):
        statement = (f'select * from {table_name} where id = ?', (id,))
        dataset = self._select_(statement)
        if len(dataset) == 1:
            return dataset[0]
        return None

    def query(self, sql):
        return self._select_(sql)

    def create(self, table_name, **scheme):
        sqls = []
        sqls.append(f'DROP TABLE IF EXISTS {table_name}')
        fields = []
        for n, t in scheme.items():
            fields.append(f'{n} {t}')
        fields = ','.join(fields)
        sqls.append(f'create table {table_name}({fields})')
        self._udpate_(sqls)

    def insert(self, table_name, **fields):
        names = []
        values = []
        for k, v in fields.items():
            names.append(k)
            values.append(v)
        names = ','.join(names)
        if len(fields.items()) == 1:
            refs = '?'
        else:
            refs = ','.join('?' for _ in range(len(fields.items())))
        sql = f'insert into {table_name}({names}) values({refs})'
        statement = (sql, values)
        self._udpate_([statement])

    def update(self, table_name, fields, **conditions):
        field_sql = []
        filed_values = []
        for k, v in fields.items():
            field_sql.append(f'{k} = ?')
            filed_values.append(v)
        where_sql, where_values = DB.where_values(**conditions)
        field_sql = ",".join(field_sql)
        sql = f'update {table_name} set {field_sql}{where_sql}'
        values = filed_values + where_values
        statement = (sql, values)
        self._udpate_([statement])

    def update_with_sql(self, sql):
        self._udpate_([sql])

    def delete(self, table_name, **conditions):
        statement = self._statement_(table_name, 'delete', **conditions)
        self._udpate_([statement])

    def drop(self, table_name):
        sql = f'drop table if exists {table_name}'
        self._udpate_([sql])

    def get_scheme(self, table_name):
        class TableScheme:
            def __init__(self, index, name, type):
                self.index = index
                self.name = name
                self.type = type

            def __repr__(self):
                return str(self.__dict__)

        return list(map(lambda info: TableScheme(info[0], info[1], info[2]), self._select_(
            f'PRAGMA table_info = \'{table_name}\'')))

    def clear_data(self):
        for table, op in self.tables.items():
            if op == 'drop':
                continue
            self.delete(table)

    def reset_scheme(self):
        self.drop('alembic_version')
        for table in self.tables:
            self.drop(table)

    def _statement_(self, table_name, action, **conditions):
        if action == 'select':
            action += ' *'
        sql = f'{action} from {table_name}'
        if len(conditions) == 0:
            return sql
        where, values = DB.where_values(**conditions)
        sql += where
        if action == 'select':
            sql += ' order by id desc'
        return (sql, values)

    def _udpate_(self, sqls):
        db_cur = self.db_con.cursor()
        for sql in sqls:
            logger.debug(sql)
            if type(sql) is tuple:
                db_cur.execute(sql[0], sql[1])
            else:
                db_cur.execute(sql)
        self.db_con.commit()
        db_cur.close()

    def _select_(self, sql):
        logger.debug(sql)
        db_cur = self.db_con.cursor()
        if type(sql) is tuple:
            db_cur.execute(sql[0], sql[1])
        else:
            db_cur.execute(sql)
        dataset = db_cur.fetchall()
        db_cur.close()
        return dataset

    @staticmethod
    def where_values(**conditions):
        where = []
        values = []
        where_and = False
        for k, v in conditions.items():
            if where_and:
                where.append(' and ')
            if type(v) == DB.Condition:
                where.append(f'{k} {v.op} ?')
                values.append(v.val)
            else:
                where.append(f'{k} = ?')
                values.append(v)
            if not where_and:
                where_and = True
        if len(where) > 0:
            where = ' where {}'.format(''.join(where))
        else:
            where = ''
        return (where, values)


class Entity:
    class Column:
        def __init__(self, val, **kwargs):
            self.val = val
            for k, v in kwargs.items():
                self.__dict__[k] = v

        def set(self, val):
            self.val = val

        @property
        def name_defined(self):
            return 'name' in self.__dict__

        def __repr__(self):
            return str(self.__dict__)

        def __eq__(self, val):
            return self.val == val

    class Id(Column):
        def __init__(self, value):
            super().__init__(value, name='id')

    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name
        self.id = Entity.Id(-1)
        self.created_at = Entity.Column(None)
        self.updated_at = Entity.Column(None)
        self.state = Entity.Column(1)
        self.cls = self.__class__
        self.scheme = db.get_scheme(table_name)

    @property
    def instance(self):
        return self.cls()

    def save(self):
        self.created_at.set(now())
        self.updated_at.set(self.created_at.val)
        self.state.set(1)
        fields = self.fields.copy()
        del fields['id']
        self.db.insert(self.table_name, **fields)
        data = self.db.get_last(self.table_name)
        if data is not None:
            self.id.set(int(data[0]))

    def update(self):
        fields = self.fields.copy()
        del fields['id']
        self.db.update(self.table_name, fields, id=self.id.val)

    def from_db(self, **conditions):
        dataset = self.db.find(self.table_name, **conditions)
        if len(dataset) > 0:
            self._from_data_(dataset[0])

    def get(self, id):
        data = self.db.get(self.table_name, id)
        if data is not None:
            self._from_data_(data)

    def get_by(self, **conditions):
        dataset = self.db.find(self.table_name, **conditions)
        if len(dataset) == 1:
            self._from_data_(dataset[0])

    def find(self, **conditions):
        dataset = self.db.find(self.table_name, **conditions)
        return self._dataset_to_entities_(dataset)

    def find_by_limit(self, limit, offset=0):
        dataset = self.db.query((f'select * from {self.table_name} limit ? offset ?', (limit, offset)))
        return self._dataset_to_entities_(dataset)

    def delete(self):
        self.db.delete(self.table_name, id=self.id.val)

    def batch_delete(self, **conditions):
        self.db.delete(self.table_name, **conditions)

    @staticmethod
    def batch_save(entities):
        for entity in entities:
            entity.save()

    @property
    def all(self):
        dataset = self.db.find(self.table_name)
        return self._dataset_to_entities_(dataset)

    def to_last(self):
        data = self.db.get_last(self.table_name)
        if data is not None:
            self._from_data_(data)

    def _dataset_to_entities_(self, dataset):
        entities = []
        for data in dataset:
            entity = self.instance
            entity._from_data_(data)
            entities.append(entity)
        return entities

    def _from_data_(self, data):
        for name in self.fields:
            field_scheme = list(filter(lambda c: c.name == name, self.scheme))
            if len(field_scheme) == 0:
                continue
            field_scheme = field_scheme[0]
            self.__dict__[name].set(data[field_scheme.index])

    @property
    def fields(self):
        fields = {}
        for k, v in self.__dict__.items():
            if type(v) is Entity.Column or type(v) is Entity.Id:
                if v.name_defined:
                    fields[v.name] = v.val
                else:
                    fields[k] = v.val
        return fields

    def __repr__(self):
        return f'table:{self.table_name} fields:[ {self.fields} ]'


class DBUnitTests(UnitTests):
    def __init__(self):
        super().__init__(__file__)

    def _setup_(self):
        self.db_file = os.path.join(DB_DIR, 'test.db')
        with open(self.db_file, 'a'):
            os.utime(self.db_file, None)
        self.db = DB(self.db_file)
        self.db.create('test', id='integer primary key autoincrement', name='char(50)', created_at='date',
                       updated_at='date', state='int')

    def _teardown_(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    @UnitTests.skip
    def get_all_tables_test(self):
        r = self.db.find('sqlite_master', type='table')
        assert r[0][0] == 'table'
        logger.debug(r)

    @UnitTests.skip
    def insert_test(self):
        self.db.insert('test', id=1, name='name', created_at=now())
        r = self.db.find('test')
        assert r[0][0] == 1 and r[0][1] == 'name'
        logger.debug(r)

    @UnitTests.skip
    def delete_test(self):
        self.db.delete('test')
        r = self.db.find('test')
        assert len(r) == 0

    @UnitTests.skip
    def update_test(self):
        self.db.insert('test', id=1, name='name', created_at=now())
        self.db.update('test', {'name': 'update name'}, id=1)
        r = self.db.find('test')
        assert r[0][0] == 1 and r[0][1] == 'update name'
        logger.debug(r)

    # @UnitTests.skip
    def entity_test(self):
        db = self.db

        class TestEntity(Entity):
            def __init__(self):
                super().__init__(db, 'test')
                self.name = Entity.Column('')

        entity = TestEntity()
        entity.name.set('name')
        entity.save()
        assert entity.id.val > 0 and entity.name.val == 'name'
        logger.debug(entity)
        entity.name.set('update name')
        entity.update()
        assert entity.id.val == 1 and entity.name.val == 'update name'
        logger.debug(entity)
        entity = TestEntity()
        entity.name.set('name 2')
        entity.save()
        assert entity.id.val == 2 and entity.name.val == 'name 2'
        logger.debug(entity)
        entity.get(1)
        assert entity.id.val == 1 and entity.name.val == 'update name'
        logger.debug(entity)
        logger.debug(json.dumps(entity.fields))


DBUnitTests().run()
