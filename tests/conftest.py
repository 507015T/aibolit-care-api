import sys
from pathlib import Path
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

src_path = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(src_path))
from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    url=SQLALCHEMY_DATABASE_URL,
    echo=False,
)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
