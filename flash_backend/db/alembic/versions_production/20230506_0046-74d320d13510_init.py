"""init

Revision ID: 74d320d13510
Revises:
Create Date: 2023-05-06 00:46:30.367261

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "74d320d13510"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    enum_user_status = postgresql.ENUM(
        "active", "disabled", name="user_status", schema="production"
    )
    op.create_table(
        "User",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column(
            "datetime_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("status", enum_user_status, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="production",
    )
    op.create_index(
        op.f("ix_production_User_email"), "User", ["email"], unique=True, schema="production"
    )


def downgrade() -> None:
    enum_user_status = postgresql.ENUM(
        "active", "disabled", name="user_status", schema="production"
    )
    op.drop_index(op.f("ix_production_User_email"), table_name="User", schema="production")
    op.drop_table("User", schema="production")
    enum_user_status.drop(op.get_bind())
