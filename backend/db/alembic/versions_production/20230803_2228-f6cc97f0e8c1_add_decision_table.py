"""Add decision table

Revision ID: f6cc97f0e8c1
Revises: 620cad508b0a
Create Date: 2023-08-03 22:28:26.000277

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f6cc97f0e8c1"
down_revision = "620cad508b0a"
branch_labels = None
depends_on = None


enum_decision_action = sa.Enum("buy", "skip", "sell", name="DecisionAction", schema="production")


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
        sa.ForeignKeyConstraint(["session_id"], ["production.session._id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("_id"),
        schema="production",
    )
    op.create_index(
        op.f("ix_production_decision_session_id"),
        "decision",
        ["session_id"],
        unique=False,
        schema="production",
    )


def downgrade() -> None:
    enum_decision_action.drop(op.get_bind())
    op.drop_index(
        op.f("ix_production_decision_session_id"), table_name="decision", schema="production"
    )
    op.drop_table("decision", schema="production")
