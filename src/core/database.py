from sqlalchemy.ext.asyncio import (
    async_sessionmaker, 
    AsyncSession, 
    create_async_engine
)

from src.core.config import settings


async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)