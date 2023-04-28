import asyncio
import logging
import logging.config

from alembic import context
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from app.config import settings_db
from app.models.base import Base

# Read logger config with json-formatter from alembic.ini and create logger
logging.config.fileConfig(context.config.config_file_name)  # type: ignore[arg-type]
logger = logging.getLogger("alembic")
logger.info(
    "Db migration started",
    extra={"db_url": settings_db.DB_URL, "db_schema": settings_db.DB_SCHEMA},
)

# Read models
target_metadata = Base.metadata


def do_run_migrations(connection: AsyncConnection) -> None:
    def include_name(name: str, type_: str, parent_names: dict) -> bool:  # noqa: ARG001
        """Filter tables only in current db schema"""
        if type_ == "schema":
            return name in [settings_db.DB_SCHEMA]
        else:
            return True

    context.configure(
        connection=connection,  # type: ignore[arg-type]
        dialect_opts={"paramstyle": "named"},
        target_metadata=target_metadata,
        compare_type=True,
        include_schemas=True,
        include_name=include_name,
        version_table_schema=settings_db.DB_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_async_engine(settings_db.DB_URL, future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


# Run using asyncio
try:
    asyncio.run(run_migrations_online())
    logger.info(
        "Db migration finished",
        extra={"db_url": settings_db.DB_URL, "db_schema": settings_db.DB_SCHEMA},
    )
except Exception as e:
    logger.exception(
        "Db migration failed",
        exc_info=e,
        extra={"db_url": settings_db.DB_URL, "db_schema": settings_db.DB_SCHEMA},
    )
