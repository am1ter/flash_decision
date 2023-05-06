"""init

Revision ID: f6d2e72d94cd
Revises:
Create Date: 2023-04-27 23:28:22.067682

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f6d2e72d94cd"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Manually edited
    enum_user_status = postgresql.ENUM(
        "active", "disabled", name="user_status", schema="development"
    )
    op.create_table(
        "User",
        sa.Column("Id", sa.Integer(), nullable=False),
        sa.Column("Name", sa.String(), nullable=False),
        sa.Column("Email", sa.String(), nullable=False),
        sa.Column("Password", sa.String(), nullable=False),
        sa.Column("DatetimeCreate", sa.DateTime(), nullable=False),
        sa.Column("Status", enum_user_status, nullable=False),
        sa.PrimaryKeyConstraint("Id"),
        schema="development",
    )
    op.create_index(
        op.f("ix_development_User_Email"), "User", ["Email"], unique=True, schema="development"
    )


def downgrade() -> None:
    enum_user_status = postgresql.ENUM(
        "active", "disabled", name="user_status", schema="development"
    )
    op.drop_index(op.f("ix_development_User_Email"), table_name="User", schema="development")
    op.drop_table("User", schema="development")
    enum_user_status.drop(op.get_bind())
