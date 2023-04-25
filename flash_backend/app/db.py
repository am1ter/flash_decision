from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

meta = MetaData()
engine = create_async_engine(settings.DB_URL, echo=settings.LOG_DB_ACCESS)
AsyncSessionFactory = sessionmaker(  # type: ignore[call-overload]
    bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSessionFactory() as session:
        yield session
