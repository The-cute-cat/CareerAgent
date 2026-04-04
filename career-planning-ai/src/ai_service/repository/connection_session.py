from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


def get_db_url() -> str:
    DB_URL = (
        f"mysql+aiomysql://{settings.database.user}:{settings.database.password}"
        f"@{settings.database.host}:{settings.database.port}/{settings.database.database}"
        f"?charset=utf8mb4"
    )
    return DB_URL