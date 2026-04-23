from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from config import settings

DATABASE_URL = (
    f"mysql+aiomysql://{settings.database.user}:{settings.database.password.get_secret_value()}"
    f"@{settings.database.host}:{settings.database.port}/{settings.database.database}"
    "?charset=utf8mb4"
)

async_engine = create_async_engine(
    DATABASE_URL,
    echo=getattr(settings, "debug", False),
    future=True,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_pre_ping=settings.database.pool_pre_ping,
    pool_recycle=settings.database.pool_recycle,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def get_db_url() -> str:
    return DATABASE_URL


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    提供数据库会话。
    使用 async with 语法自动管理上下文，无需显式调用 close()。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # 需显式调用 session.commit()
        except Exception:
            # 发生异常时回滚
            await session.rollback()
            raise
