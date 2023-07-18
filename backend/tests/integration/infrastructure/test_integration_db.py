import pytest
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

# Import 1st party modules after setting env vars
from app.infrastructure.db import get_connection, get_new_engine
from app.infrastructure.orm import Base
from app.system.config import Environment, Settings

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def engine() -> AsyncEngine:
    return get_new_engine()


class TestDb:
    async def test_connection(self, engine: AsyncEngine) -> None:
        """Make sure the database is up and a connection to it can be established"""
        try:
            async with get_connection(engine) as conn:
                await conn.execute(text("SELECT 1"))
        except ConnectionRefusedError:
            pytest.fail("Connection to DB cannot be established")

    async def test_migrations(self, engine: AsyncEngine) -> None:
        """Check that all database migrations are applied to `production` db schema"""

        # Check if environment configurated to run in production mode
        assert Settings().general.ENVIRONMENT == Environment.production, "Wrong env configuration"
        assert Settings().db.DB_SCHEMA == Environment.production.value, "Wrong db schema"

        def include_name(name: str, type_: str, parent_names: dict) -> bool:
            """Filter only current db schema tables"""
            if type_ == "schema":
                return name in [Settings().db.DB_SCHEMA]
            else:
                return True

        def custom_compare_metadata(connection: AsyncConnection) -> list[tuple]:
            """
            Read existed db structure and compare it with models.
            To run sync function in async context used AsyncConnection.run_sync() method.
            This method requires functions, that will receive connection as first arguments.
            """
            mc = MigrationContext.configure(
                connection=connection,  # type: ignore[arg-type]
                opts={
                    "compare_type": True,
                    "include_schemas": True,
                    "include_name": include_name,
                    "version_table_schema": Settings().db.DB_SCHEMA,
                },
            )
            return compare_metadata(mc, Base.metadata)

        async with engine.connect() as conn:
            diff = await conn.run_sync(custom_compare_metadata)

        assert not diff, f"DB and migrations are not synced"
