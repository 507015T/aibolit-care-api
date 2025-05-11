import logging
import grpc
import pytest_asyncio
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from aibolit.core.database import Base, get_db
from aibolit.repositories.schedules.repository import ScheduleRepo
from aibolit.repositories.users.repository import UserRepo
from aibolit.main import app
from aibolit.services.users.service import UserService
from aibolit.services.schedules.service import ScheduleService
from aibolit.transport.grpc.adapters.schedules.service import GrpcScheduleService
from aibolit.transport.grpc.adapters.users.service import GrpcUserService
from aibolit.transport.grpc.generated import schedule_pb2_grpc, user_pb2_grpc


SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://test_user:@localhost/test_db"

engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture(scope="function")
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


@pytest_asyncio.fixture
async def grpc_test_channel(get_testing_db: AsyncSession):
    users_repo, schedules_repo = UserRepo(get_testing_db), ScheduleRepo(get_testing_db)
    users_service, schedules_service = UserService(users_repo), ScheduleService(schedules_repo)

    server = grpc.aio.server()
    user_pb2_grpc.add_UserServiceServicer_to_server(GrpcUserService(users_service), server)
    schedule_pb2_grpc.add_SchedulesServiceServicer_to_server(
        GrpcScheduleService(schedules_service, users_service), server
    )
    port = server.add_insecure_port('[::]:0')
    await server.start()

    channel = grpc.aio.insecure_channel(f"localhost:{port}")
    try:
        yield channel
    finally:
        await channel.close()
        await server.stop(0)


@pytest_asyncio.fixture
async def stub_for_schedules(grpc_test_channel):
    return schedule_pb2_grpc.SchedulesServiceStub(grpc_test_channel)


@pytest_asyncio.fixture
async def stub_for_users(grpc_test_channel):
    return user_pb2_grpc.UserServiceStub(grpc_test_channel)


@pytest_asyncio.fixture(autouse=True)
async def suppress_logs():
    """Fixture to suppress logs during tests"""
    logging.disable(logging.CRITICAL)  # Отключаем все логи
    yield
    logging.disable(logging.NOTSET)
