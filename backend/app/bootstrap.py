from __future__ import annotations

from sqlalchemy.orm import sessionmaker

from app.infrastructure.db import AsyncSessionFactory
from app.infrastructure.orm.mapper import init_orm_mappers


class Bootstrap:
    """
    Configure the app during the ititialization.
    Use singleton pattern to avoid multiple instances.
    """

    _instance: Bootstrap | None = None
    db_session_factory: sessionmaker

    def __new__(
        cls,
        *,
        start_orm: bool = True,
        db_session_factory: sessionmaker = AsyncSessionFactory,
    ) -> Bootstrap:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if start_orm:
                init_orm_mappers()
            cls._instance.db_session_factory = db_session_factory
        return cls._instance


bootstrap = Bootstrap()
