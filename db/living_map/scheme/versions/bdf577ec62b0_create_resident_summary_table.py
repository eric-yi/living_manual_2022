"""create resident summary table

Revision ID: bdf577ec62b0
Revises: f7652f427aee
Create Date: 2022-04-13 14:16:35.880840

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
revision = 'bdf577ec62b0'
down_revision = 'f7652f427aee'
branch_labels = None
depends_on = None


TABLE_NAME = 'resident_summary'


def upgrade():
    table_schema = build_table_schema(TABLE_NAME,
                                      sa.Column('published_at', sa.DateTime(), nullable=True),
                                      sa.Column('origin', sa.String, nullable=True),
                                      sa.Column('diagnosed', sa.Integer, nullable=True),
                                      sa.Column('asymptomatic', sa.Integer, nullable=True),
                                      sa.Column('district_code', sa.String, nullable=True),
                                      )

    op.create_table(*table_schema)


def downgrade():
    drop_table(op, TABLE_NAME)
