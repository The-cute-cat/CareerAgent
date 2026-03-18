from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# 假设你的配置类在这里
from config import settings

# 动态构建数据库连接 URL
DATABASE_URL = (
    f"mysql+aiomysql://{settings.database.user}:{settings.database.password}"
    f"@{settings.database.host}:{settings.database.port}/{settings.database.database}"
    "?charset=utf8mb4"
)

# 2. 创建异步引擎
async_engine = create_async_engine(
    DATABASE_URL,
    # 改进：将其绑定到环境变量，开发环境为 True，生产环境为 False
    echo=getattr(settings, "debug", False),
    pool_size=10,         # 连接池基础大小，根据并发量调整
    max_overflow=20,      # 突发流量时允许的溢出连接数
    pool_pre_ping=True,   # 改进：MySQL必开，每次借出连接前测试是否存活，防止"MySQL server has gone away"
    pool_recycle=3600,    # 改进：MySQL默认8小时断开空闲连接，设置3600秒主动回收，增强稳定性
)

# 3. 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 异步必设为 False，否则 commit 后访问属性会引发隐式同步查询报错
    autocommit=False,
    autoflush=False,
)

# # 4. 声明性基类
# class Base(DeclarativeBase):
#     pass

# 5. FastAPI 依赖注入函数：获取数据库会话
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    提供数据库会话。
    使用 async with 语法自动管理上下文，无需显式调用 close()。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # 💡 改进：去掉了隐式的 await session.commit()
            # 请在你的路由 (Router) 或服务层 (Service) 中，确定数据修改无误后，显式调用 session.commit()
        except Exception:
            # 发生异常时回滚
            await session.rollback()
            raise
        # async with 结束时会自动安全地关闭/归还 session，无需写 finally: await session.close()

