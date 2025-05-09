import grpc
from aibolit.transport.grpc.generated.user_pb2_grpc import UserServiceServicer

from aibolit.transport.grpc.generated.user_pb2 import GetAllUsersResponse, CreateUserResponse, User
from aibolit.services.users_service import UserService
from aibolit.transport.rest.users.schemas import UserCreateRequest


class GrpcUserService(UserServiceServicer):
    def __init__(self, users_service: UserService):
        self._users_service = users_service

    async def CreateUser(self, request, context: grpc.aio.ServicerContext):
        db_user = await self._users_service.create_user(UserCreateRequest())
        return CreateUserResponse(id=db_user)

    async def GetUsers(self, request, context: grpc.aio.ServicerContext):
        users = await self._users_service.list_users()
        users = [User(id=user.id) for user in users.users if user]
        return GetAllUsersResponse(users=users)
