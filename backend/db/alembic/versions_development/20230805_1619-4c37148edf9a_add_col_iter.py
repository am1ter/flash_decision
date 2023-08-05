"""Add column iteration_num

Revision ID: 4c37148edf9a
Revises: ea50fe080d40
Create Date: 2023-08-05 16:19:52.660188

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4c37148edf9a"
down_revision = "ea50fe080d40"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "decision", sa.Column("iteration_num", sa.Integer(), nullable=False), schema="development"
    )


def downgrade() -> None:
    op.drop_column("decision", "iteration_num", schema="development")
