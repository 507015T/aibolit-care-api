import grpc
from aibolit.grpc.generated.users_pb2_grpc import UserServiceServicer

from aibolit.grpc.generated import users_pb2
from aibolit.services.users import UserService
from aibolit.schemas.users import UserCreateRequest


class GrpcUserService(UserServiceServicer):
    def __init__(self, users_service: UserService):
        self._users_service = users_service

    async def CreateUser(self, request, context: grpc.aio.ServicerContext):
        db_user = await self._users_service.create_user(UserCreateRequest())
        return users_pb2.CreateUserResponse(id=db_user)
