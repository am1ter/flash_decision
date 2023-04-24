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
    context.configure(
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
        connection=connection,  # type: ignore[arg-type]
        target_metadata=target_metadata,
        include_schemas=True,
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
