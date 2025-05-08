import pytest
import pytest_asyncio
import grpc
from sqlalchemy.ext.asyncio import AsyncSession
from aibolit.integrations.users_repo import UsersRepo
from aibolit.services.users_service import UserService
from aibolit.transport.grpc.generated import user_pb2, user_pb2_grpc
from aibolit.transport.grpc.adapters.grpc_service import GrpcUserService


@pytest_asyncio.fixture
async def grpc_test_channel(get_testing_db: AsyncSession):
    users_repo = UsersRepo(get_testing_db)
    user_service = UserService(users_repo)

    server = grpc.aio.server()
    user_pb2_grpc.add_UserServiceServicer_to_server(GrpcUserService(user_service), server)
    port = server.add_insecure_port('[::]:0')
    await server.start()

    channel = grpc.aio.insecure_channel(f"localhost:{port}")
    try:
        yield channel
    finally:
        await channel.close()
        await server.stop(0)


@pytest.mark.asyncio
async def test_post_schedule(grpc_test_channel):
    stub = user_pb2_grpc.UserServiceStub(grpc_test_channel)
    request = user_pb2.CreateUserRequest()
    reply = await stub.CreateUser(request)
    assert 1 == reply.id
