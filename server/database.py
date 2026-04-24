import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings


def _ensure_data_dir():
    """确保数据库目录存在"""
    # 解析数据库路径
    db_path = settings.DATABASE_URL.split("///")[-1]
    # 移除可能的协议前缀和查询参数
    db_path = db_path.split("?")[0]

    # 获取目录路径
    db_file = Path(db_path)
    db_dir = db_file.parent

    # 如果不是当前目录，则创建目录
    if str(db_dir) != ".":
        db_dir.mkdir(parents=True, exist_ok=True)


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    # 确保数据库目录存在
    _ensure_data_dir()

    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
