"""create vendor_tag table

Revision ID: 10ef925b9a32
Revises: a0b4495ce7fb
Create Date: 2022-04-06 22:57:28.619978

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
revision = '10ef925b9a32'
down_revision = 'a0b4495ce7fb'
branch_labels = None
depends_on = None


TABLE_NAME = 'vendor_tag'


def upgrade():
    table_schema = build_table_schema(TABLE_NAME,
                                      sa.Column('vendor_id', sa.Integer(), nullable=True),
                                      sa.Column('tag_id', sa.Integer(), nullable=True),
                                      )

    op.create_table(*table_schema)


def downgrade():
    drop_table(op, TABLE_NAME)
