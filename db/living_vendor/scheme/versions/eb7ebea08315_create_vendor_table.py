"""create vendor table

Revision ID: eb7ebea08315
Revises: 63d8bc6266c9
Create Date: 2022-04-06 22:28:33.991302

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
revision = 'eb7ebea08315'
down_revision = '63d8bc6266c9'
branch_labels = None
depends_on = None

TABLE_NAME = 'vendor'


def upgrade():
    table_schema = build_table_schema(TABLE_NAME,
                                      sa.Column('name', sa.String(), nullable=True),
                                      sa.Column('contact', sa.String(), nullable=True),
                                      sa.Column('address', sa.String(), nullable=True),
                                      sa.Column('mobile', sa.String(), nullable=True),
                                      sa.Column('tel', sa.String(), nullable=True),
                                      sa.Column('desc', sa.String(), nullable=True),
                                      sa.Column('wechat', sa.String(), nullable=True),
                                      )

    op.create_table(*table_schema)


def downgrade():
    drop_table(op, TABLE_NAME)
