"""Add decision table

Revision ID: ea50fe080d40
Revises: 254f53f7bfde
Create Date: 2023-08-03 22:27:05.973402

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ea50fe080d40"
down_revision = "254f53f7bfde"
branch_labels = None
depends_on = None


enum_decision_action = sa.Enum("buy", "skip", "sell", name="DecisionAction", schema="development")


def upgrade() -> None:
    op.create_table(
        "decision",
        sa.Column("_id", sa.UUID(), nullable=False),
        sa.Column(
            "datetime_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("time_spent", sa.Numeric(), nullable=False),
        sa.Column("result_raw", sa.Numeric(), nullable=False),
        sa.Column("result_final", sa.Numeric(), nullable=False),
        sa.Column("action", enum_decision_action, nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["development.session._id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("_id"),
        schema="development",
    )
    op.create_index(
        op.f("ix_development_decision_session_id"),
        "decision",
        ["session_id"],
        unique=False,
        schema="development",
    )


def downgrade() -> None:
    enum_decision_action.drop(op.get_bind())
    op.drop_index(
        op.f("ix_development_decision_session_id"), table_name="decision", schema="development"
    )
    op.drop_table("decision", schema="development")
