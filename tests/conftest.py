import sys
import os
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
import pytest_asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from database import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    url=SQLALCHEMY_DATABASE_URL,
    echo=False,
)
TestingSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, autoflush=False
)


@pytest_asyncio.fixture(loop_scope="function")
async def get_testing_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(loop_scope="function")
async def async_client(get_testing_db):
    app.dependency_overrides[get_db] = lambda: get_testing_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
