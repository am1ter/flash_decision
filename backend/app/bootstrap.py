from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db import DbDep
from app.infrastructure.orm.mapper import init_orm_mappers


class Bootstrap:
    """
    Configure the app during the ititialization.
    Use singleton pattern to avoid multiple instances.
    """

    _instance: Bootstrap | None = None
    db_dep: type[AsyncSession]

    def __new__(
        cls,
        *,
        start_orm: bool = True,
        db_dep: type[AsyncSession] = DbDep,
    ) -> Bootstrap:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if start_orm:
                init_orm_mappers()
            cls._instance.db_dep = db_dep
        return cls._instance


bootstrap = Bootstrap()
