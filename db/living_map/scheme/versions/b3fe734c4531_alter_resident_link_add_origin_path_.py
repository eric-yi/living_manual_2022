"""alter  resident_link add origin_path table

Revision ID: b3fe734c4531
Revises: a4835b378b13
Create Date: 2022-04-14 14:27:43.247463

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
revision = 'b3fe734c4531'
down_revision = 'a4835b378b13'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute('alter table resident_link add origin_filepath char(255);')


def downgrade():
    conn = op.get_bind()
    conn.execute('alter table resident_link drop origin_filepath')
