from __future__ import annotations

from collections.abc import Callable
from contextlib import _AsyncGeneratorContextManager

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.orm import sessionmaker

from app.infrastructure.db import AsyncSessionFactory, get_connection
from app.infrastructure.orm.mapper import init_orm_mappers

AsyncDbConnFactory = Callable[..., _AsyncGeneratorContextManager[AsyncConnection]]


class Bootstrap:
    """Configure the app during the ititialization"""

    orm_mapped = False

    def __init__(
        self,
        *,
        start_orm: bool = True,
        db_conn_factory: AsyncDbConnFactory = get_connection,
        db_session_factory: sessionmaker = AsyncSessionFactory,
    ) -> None:
        # Mapping Domain <-> ORM must be executed only once
        if start_orm and not self.__class__.orm_mapped:
            init_orm_mappers()
            self.__class__.orm_mapped = True
        self.db_conn_factory = db_conn_factory
        self.db_session_factory = db_session_factory


bootstrap = Bootstrap()
