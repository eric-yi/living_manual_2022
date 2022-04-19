"""alter district initialise table

Revision ID: a4835b378b13
Revises: 8cfd220cc448
Create Date: 2022-04-13 14:26:01.876246

"""
import logging
import sys
from alembic import op
import sqlalchemy as sa

FORMAT = '%(levelname)s %(asctime)s [%(filename)s:%(lineno)d]: %(message)s'
logging.basicConfig(format=FORMAT, stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()


def build_table_schema(name, *columns):
    dml_args = [
        name,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True)
    ]

    dml_args.extend(columns)

    dml_args.extend((
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('state', sa.Integer(), nullable=True, default=1)
    ))

    return dml_args


def drop_table(op, name):
    try:
        op.drop_table(name)
    except Exception as e:
        logger.error(f'drop table error: {e}')


# revision identifiers, used by Alembic.
revision = 'a4835b378b13'
down_revision = '8cfd220cc448'
branch_labels = None
depends_on = None


def upgrade():
    from datetime import datetime
    conn = op.get_bind()

    fields = [
        {
            'name': '上海市',
            'code': '31'
        },
        {
            'name': '黄浦区',
            'code': '310101'
        },
        {
            'name': '徐汇区',
            'code': '310104'
        },
        {
            'name': '长宁区',
            'code': '310105'
        },
        {
            'name': '静安区',
            'code': '310106'
        },
        {
            'name': '普陀区',
            'code': '310107'
        },
        {
            'name': '虹口区',
            'code': '310109'
        },
        {
            'name': '杨浦区',
            'code': '310110'
        },
        {
            'name': '闵行区',
            'code': '310112'
        },
        {
            'name': '宝山区',
            'code': '310113'
        },
        {
            'name': '嘉定区',
            'code': '310114'
        },
        {
            'name': '浦东新区',
            'code': '310115'
        },
        {
            'name': '金山区',
            'code': '310116'
        },
        {
            'name': '松江区',
            'code': '310117'
        },
        {
            'name': '青浦区',
            'code': '310118'
        },
        {
            'name': '奉贤区',
            'code': '310120'
        },
        {
            'name': '崇明县',
            'code': '310151'
        },
    ]
    created_at = datetime.now()
    updated_at = created_at
    state = 1
    for field in fields:
        conn.execute('insert into district(name, code, created_at, updated_at, state) values(?, ?, ?, ?, ?)',
                     (field['name'], field['code'], created_at, updated_at, state,))


def downgrade():
    conn = op.get_bind()
    conn.execute('delete from district')
