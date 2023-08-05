"""Add column iteration_num

Revision ID: 0569a71f3725
Revises: f6cc97f0e8c1
Create Date: 2023-08-05 16:21:58.017152

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0569a71f3725"
down_revision = "f6cc97f0e8c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "decision", sa.Column("iteration_num", sa.Integer(), nullable=False), schema="production"
    )


def downgrade() -> None:
    op.drop_column("decision", "iteration_num", schema="production")
