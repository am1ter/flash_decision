"""Add auth table

Revision ID: cfeca6e8aa73
Revises: 74d320d13510
Create Date: 2023-05-09 14:30:29.413383

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "cfeca6e8aa73"
down_revision = "74d320d13510"
branch_labels = None
depends_on = None


def upgrade() -> None:
    enum_auth_status = postgresql.ENUM(
        "sign_up",
        "sign_in",
        "wrong_password",
        name="AuthStatus",
        schema="production",
    )
    op.create_table(
        "auth",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ip_address", sa.String(), nullable=False),
        sa.Column("http_user_agent", sa.String(), nullable=False),
        sa.Column(
            "status",
            enum_auth_status,
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "datetime_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["production.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="production",
    )
    op.create_index(
        op.f("ix_production_auth_user_id"), "auth", ["user_id"], unique=False, schema="production"
    )


def downgrade() -> None:
    enum_auth_status = postgresql.ENUM(
        "sign_up",
        "sign_in",
        "wrong_password",
        name="AuthStatus",
        schema="production",
    )
    op.drop_index(op.f("ix_production_auth_user_id"), table_name="auth", schema="production")
    op.drop_table("auth", schema="production")
    enum_auth_status.drop(op.get_bind())
