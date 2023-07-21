"""init

Revision ID: 0f3ba2d3f4d0
Revises:
Create Date: 2023-05-06 00:46:41.082681

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0f3ba2d3f4d0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    enum_user_status = postgresql.ENUM(
        "active", "disabled", name="UserStatus", schema="development"
    )
    op.create_table(
        "user",
        sa.Column("_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column(
            "datetime_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("status", enum_user_status, nullable=False),
        sa.PrimaryKeyConstraint("_id"),
        schema="development",
    )
    op.create_index(
        op.f("ix_development_user_email"), "user", ["email"], unique=True, schema="development"
    )


def downgrade() -> None:
    enum_user_status = postgresql.ENUM(
        "active", "disabled", name="UserStatus", schema="development"
    )
    op.drop_index(op.f("ix_development_user_email"), table_name="user", schema="development")
    op.drop_table("user", schema="development")
    enum_user_status.drop(op.get_bind())
