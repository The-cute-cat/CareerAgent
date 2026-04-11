from config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

def get_db_url() -> str:
    DB_URL = (
        f"mysql+aiomysql://{settings.database.user}:{settings.database.password}"
        f"@{settings.database.host}:{settings.database.port}/{settings.database.database}"
        f"?charset=utf8mb4"
    )
    return DB_URL

ASYNC_DATABASE_URL = get_db_url()

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)