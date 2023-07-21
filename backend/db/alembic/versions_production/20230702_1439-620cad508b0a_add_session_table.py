"""Add session table

Revision ID: 620cad508b0a
Revises: cfeca6e8aa73
Create Date: 2023-07-02 14:39:00.180402

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "620cad508b0a"
down_revision = "cfeca6e8aa73"
branch_labels = None
depends_on = None

enum_session_mode = sa.Enum(
    "classic", "blitz", "crypto", "custom", name="SessionMode", schema="production"
)
enum_session_timeframe = sa.Enum(
    "minutes1",
    "minutes5",
    "minutes15",
    "minutes30",
    "minutes60",
    "daily",
    name="SessionTimeframe",
    schema="production",
)
enum_session_barsnumber = sa.Enum(
    "bars15",
    "bars30",
    "bars50",
    "bars70",
    name="SessionBarsnumber",
    schema="production",
)
enum_session_timelimit = sa.Enum(
    "seconds5",
    "seconds10",
    "seconds30",
    "seconds60",
    "seconds120",
    name="SessionTimelimit",
    schema="production",
)
enum_session_iterations = sa.Enum(
    "iterations5",
    "iterations10",
    "iterations15",
    "iterations20",
    name="SessionIterations",
    schema="production",
)
enum_session_slippage = sa.Enum(
    "no_slippage",
    "low",
    "average",
    "high",
    name="SessionSlippage",
    schema="production",
)
enum_session_fixingbar = sa.Enum(
    "bar10", "bar20", "bar30", "bar40", name="SessionFixingbar", schema="production"
)
enum_session_status = sa.Enum(
    "created", "active", "closed", name="SessionStatus", schema="production"
)


def upgrade() -> None:
    op.create_table(
        "session",
        sa.Column("_id", sa.UUID(), nullable=False),
        sa.Column(
            "datetime_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("ticker", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "mode",
            enum_session_mode,
            nullable=False,
        ),
        sa.Column(
            "timeframe",
            enum_session_timeframe,
            nullable=False,
        ),
        sa.Column(
            "barsnumber",
            enum_session_barsnumber,
            nullable=False,
        ),
        sa.Column(
            "timelimit",
            enum_session_timelimit,
            nullable=False,
        ),
        sa.Column(
            "iterations",
            enum_session_iterations,
            nullable=False,
        ),
        sa.Column(
            "slippage",
            enum_session_slippage,
            nullable=False,
        ),
        sa.Column(
            "fixingbar",
            enum_session_fixingbar,
            nullable=False,
        ),
        sa.Column(
            "status",
            enum_session_status,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["production.user._id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("_id"),
        schema="production",
    )
    op.create_index(
        op.f("ix_production_session_user_id"),
        "session",
        ["user_id"],
        unique=False,
        schema="production",
    )


def downgrade() -> None:
    enum_session_mode.drop(op.get_bind())
    enum_session_timeframe.drop(op.get_bind())
    enum_session_barsnumber.drop(op.get_bind())
    enum_session_timelimit.drop(op.get_bind())
    enum_session_iterations.drop(op.get_bind())
    enum_session_slippage.drop(op.get_bind())
    enum_session_fixingbar.drop(op.get_bind())
    enum_session_status.drop(op.get_bind())
    op.drop_index(op.f("ix_production_session_user_id"), table_name="session", schema="production")
    op.drop_table("session", schema="production")
