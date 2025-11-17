from functools import wraps
from typing import Awaitable, Callable
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import DATABASE_URL


engine = create_async_engine(DATABASE_URL, pool_size=20,
    max_overflow=30,
    # Уменьшение времени ожидания recycle
    pool_recycle=3600,
    # Включить пул соединений
    pool_pre_ping=True,
    # Использовать WAL режим для SQLite (улучшает параллельный доступ)
    connect_args={
        "timeout": 30,
        "check_same_thread": False,
        "uri": True
    },
    echo=False) # на проде поставить echo=False

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def with_db_session(func: Callable[..., Awaitable]):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with AsyncSessionLocal() as session:
            kwargs["session"] = session
            return await func(*args, **kwargs)
    return wrapper