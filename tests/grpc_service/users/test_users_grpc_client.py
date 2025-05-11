import pytest
from aibolit.transport.grpc.generated import user_pb2


@pytest.mark.asyncio
async def test_create_user(stub_for_users):
    request = user_pb2.CreateUserRequest()
    response = await stub_for_users.CreateUser(request)
    assert 1 == response.id
