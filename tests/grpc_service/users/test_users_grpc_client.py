import pytest
from google.protobuf.json_format import MessageToDict
from aibolit.transport.grpc.generated import user_pb2


@pytest.mark.asyncio
async def test_create_user(stub_for_users):
    request = user_pb2.CreateUserRequest()
    response = await stub_for_users.CreateUser(request)
    assert 1 == response.id


@pytest.mark.asyncio
async def test_get_all_users(stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())
    request = user_pb2.GetAllUsersRequest()
    response = await stub_for_users.GetUsers(request)
    json_response = [MessageToDict(user) for user in response.users]
    expected_data = [{"id": 1}, {"id": 2}]
    assert expected_data == json_response
