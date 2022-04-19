"""alter vendor add link table

Revision ID: 872e7deeb339
Revises: 0ad5adfdd8c2
Create Date: 2022-04-10 16:34:58.474869

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
revision = '872e7deeb339'
down_revision = '0ad5adfdd8c2'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute('alter table vendor add link char(255);')


def downgrade():
    conn = op.get_bind()
    conn.execute('alter table vendor drop link')
