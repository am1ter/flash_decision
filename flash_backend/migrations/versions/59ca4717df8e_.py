"""empty message

Revision ID: 59ca4717df8e
Revises: d16440742b31
Create Date: 2021-10-05 01:31:56.877152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59ca4717df8e'
down_revision = 'd16440742b31'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Iteration', sa.Column('StartBarPrice', sa.Float(), nullable=True))
    op.add_column('Iteration', sa.Column('FinalBarPrice', sa.Float(), nullable=True))
    op.add_column('Iteration', sa.Column('FixingBarPrice', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Iteration', 'FixingBarPrice')
    op.drop_column('Iteration', 'FinalBarPrice')
    op.drop_column('Iteration', 'StartBarPrice')
    # ### end Alembic commands ###
