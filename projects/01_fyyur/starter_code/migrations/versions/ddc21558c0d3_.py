"""empty message

Revision ID: ddc21558c0d3
Revises: 59ec67c7eedd
Create Date: 2019-10-27 02:19:02.975542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddc21558c0d3'
down_revision = '59ec67c7eedd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'Artist', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Artist', type_='unique')
    # ### end Alembic commands ###