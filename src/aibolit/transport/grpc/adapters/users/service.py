import grpc
from aibolit.transport.grpc.generated.user_pb2_grpc import UserServiceServicer

from aibolit.transport.grpc.generated import user_pb2
from aibolit.services.users.service import UserService
from aibolit.schemas.users.schemas import UserCreateRequest


class GrpcUserService(UserServiceServicer):
    def __init__(self, users_service: UserService):
        self._users_service = users_service

    async def CreateUser(self, request, context: grpc.aio.ServicerContext):
        db_user = await self._users_service.create_user(UserCreateRequest())
        return user_pb2.CreateUserResponse(id=db_user)
