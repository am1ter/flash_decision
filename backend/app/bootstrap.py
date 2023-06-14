from __future__ import annotations

from collections.abc import Callable
from contextlib import _AsyncGeneratorContextManager

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.orm import sessionmaker

from app.infrastructure.db import AsyncSessionFactory, get_connection
from app.infrastructure.orm.mapper import init_orm_mappers

AsyncDbConnFactory = Callable[..., _AsyncGeneratorContextManager[AsyncConnection]]


class Bootstrap:
    """
    Configure the app during the ititialization.
    Singleton is used, because only one instance of bootstrap is allowed.
    """

    _instance: Bootstrap | None = None
    db_conn_factory: AsyncDbConnFactory
    db_session_factory: sessionmaker

    def __new__(
        cls,
        *,
        start_orm: bool = True,
        db_conn_factory: AsyncDbConnFactory = get_connection,
        db_session_factory: sessionmaker = AsyncSessionFactory,
    ) -> Bootstrap:
        if not cls._instance:
            # Mapping Domain <-> ORM must be executed only once
            instance = super().__new__(cls)
            if start_orm:
                init_orm_mappers()
            instance.db_conn_factory = db_conn_factory
            instance.db_session_factory = db_session_factory
            cls._instance = instance
        return cls._instance
