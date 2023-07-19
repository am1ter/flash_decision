import asyncio
import logging
import logging.config
from collections.abc import MutableMapping
from typing import Literal

from alembic import context
from sqlalchemy.ext.asyncio import AsyncConnection

from app.infrastructure.orm.base import Base
from app.infrastructure.sql import DbSqlPg
from app.system.config import Settings

# Read logger config with json-formatter from alembic.ini and create logger
logging.config.fileConfig(context.config.config_file_name)  # type: ignore[arg-type]
logger = logging.getLogger("alembic")
logger.info(
    "Db migration started",
    extra={"sql_url": Settings().sql.SQL_URL_WO_PASS, "sql_schema": Settings().sql.SQL_SCHEMA},
)

# Read models
target_metadata = Base.metadata


def do_run_migrations(connection: AsyncConnection) -> None:
    def include_name(
        name: str | None,
        type_: Literal[
            "schema", "table", "column", "index", "unique_constraint", "foreign_key_constraint"
        ],
        parent_names: MutableMapping[
            Literal["schema_name", "table_name", "schema_qualified_table_name"], str | None
        ],
    ) -> bool:
        """Filter tables only in current sql schema"""
        if type_ == "schema":
            return name in [Settings().sql.SQL_SCHEMA]
        else:
            return True

    context.configure(
        connection=connection,  # type: ignore[arg-type]
        dialect_opts={"paramstyle": "named"},
        target_metadata=target_metadata,
        compare_type=True,
        include_schemas=True,
        include_name=include_name,
        version_table_schema=Settings().sql.SQL_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    db_sql = DbSqlPg()
    async with db_sql.get_connection() as conn:
        await conn.run_sync(do_run_migrations)


# Run using asyncio
try:
    asyncio.run(run_migrations_online())
    logger.info(
        "Db migration finished",
        extra={
            "sql_url": Settings().sql.SQL_URL_WO_PASS,
            "sql_schema": Settings().sql.SQL_SCHEMA,
        },
    )
except Exception as e:
    logger.exception(
        "Db migration failed",
        exc_info=e,
        extra={
            "sql_url": Settings().sql.SQL_URL_WO_PASS,
            "sql_schema": Settings().sql.SQL_SCHEMA,
        },
    )
