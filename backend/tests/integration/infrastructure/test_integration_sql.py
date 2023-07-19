import pytest
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.infrastructure.orm import Base

# Import 1st party modules after setting env vars
from app.infrastructure.sql import DbSql, DbSqlPg
from app.system.config import Environment, Settings

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def db_sql() -> DbSql:
    return DbSqlPg()


class TestSql:
    async def test_connection(self, db_sql: DbSql) -> None:
        """Make sure the database is up and a connection to it can be established"""
        try:
            async with db_sql.get_connection() as conn:
                await conn.execute(text("SELECT 1"))
        except ConnectionRefusedError:
            pytest.fail("Connection to SQL cannot be established")

    async def test_migrations(self, db_sql: DbSql) -> None:
        """Check that all database migrations are applied to `production` sql schema"""

        # Check if environment configurated to run in production mode
        assert Settings().general.ENVIRONMENT == Environment.production, "Wrong env configuration"
        assert Settings().sql.SQL_SCHEMA == Environment.production.value, "Wrong SQL schema"

        def include_name(name: str, type_: str, parent_names: dict) -> bool:
            """Filter only current sql schema tables"""
            if type_ == "schema":
                return name in [Settings().sql.SQL_SCHEMA]
            else:
                return True

        def custom_compare_metadata(connection: AsyncConnection) -> list[tuple]:
            """
            Read existed SQL structure and compare it with models.
            To run sync function in async context used AsyncConnection.run_sync() method.
            This method requires functions, that will receive connection as first arguments.
            """
            mc = MigrationContext.configure(
                connection=connection,  # type: ignore[arg-type]
                opts={
                    "compare_type": True,
                    "include_schemas": True,
                    "include_name": include_name,
                    "version_table_schema": Settings().sql.SQL_SCHEMA,
                },
            )
            return compare_metadata(mc, Base.metadata)

        async with db_sql.engine.connect() as conn:
            diff = await conn.run_sync(custom_compare_metadata)

        assert not diff, f"SQL and local migrations are not synced"
