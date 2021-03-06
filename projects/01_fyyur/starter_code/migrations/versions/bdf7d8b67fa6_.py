"""empty message

Revision ID: bdf7d8b67fa6
Revises: ddc21558c0d3
Create Date: 2019-10-27 17:26:37.544674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdf7d8b67fa6'
down_revision = 'ddc21558c0d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('Artist', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_talent')
    op.drop_column('Artist', 'seeking_description')
    # ### end Alembic commands ###
