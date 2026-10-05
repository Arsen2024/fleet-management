from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.base import Base

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def test_connection():
    async with engine.connect():
        pass


async def init_db():
    async with engine.begin() as connection:

        def create_tables(sync_connection):
            Base.metadata.create_all(bind=sync_connection)

        await connection.run_sync(create_tables)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
