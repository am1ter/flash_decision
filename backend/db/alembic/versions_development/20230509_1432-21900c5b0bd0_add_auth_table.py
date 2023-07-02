"""Add auth table

Revision ID: 21900c5b0bd0
Revises: 0f3ba2d3f4d0
Create Date: 2023-05-09 14:32:47.882239

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "21900c5b0bd0"
down_revision = "0f3ba2d3f4d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    enum_auth_status = postgresql.ENUM(
        "sign_up",
        "sign_in",
        "wrong_password",
        name="AuthStatus",
        schema="development",
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
        sa.ForeignKeyConstraint(["user_id"], ["development.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="development",
    )
    op.create_index(
        op.f("ix_development_auth_user_id"), "auth", ["user_id"], unique=False, schema="development"
    )


def downgrade() -> None:
    enum_auth_status = postgresql.ENUM(
        "sign_up",
        "sign_in",
        "wrong_password",
        name="AuthStatus",
        schema="development",
    )
    op.drop_index(op.f("ix_development_auth_user_id"), table_name="auth", schema="development")
    op.drop_table("auth", schema="development")
    enum_auth_status.drop(op.get_bind())
