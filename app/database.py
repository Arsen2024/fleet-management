import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set")

engine = create_async_engine(DATABASE_URL)

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
