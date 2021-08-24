"""empty message

Revision ID: f0e52ac8e062
Revises: e8d289f8d563
Create Date: 2021-08-25 01:21:39.293621

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0e52ac8e062'
down_revision = 'e8d289f8d563'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Session', sa.Column('TradingType', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Session', 'TradingType')
    # ### end Alembic commands ###
