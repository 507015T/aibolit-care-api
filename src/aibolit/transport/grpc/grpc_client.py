from concurrent import futures
import grpc
from aibolit.core.config import settings
from aibolit.core.database import get_db_grpc
from aibolit.repositories.schedules.repository import ScheduleRepo
from aibolit.repositories.users.repository import UserRepo
from aibolit.services.schedules.service import ScheduleService
from aibolit.services.users.service import UserService
from aibolit.transport.grpc.adapters.schedules.service import GrpcScheduleService
from aibolit.transport.grpc.generated.schedule_pb2_grpc import add_SchedulesServiceServicer_to_server
from aibolit.transport.grpc.generated.user_pb2_grpc import add_UserServiceServicer_to_server
from aibolit.transport.grpc.adapters.users.service import GrpcUserService


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))

    async with get_db_grpc() as session:
        users_repo, schedules_repo = UserRepo(session), ScheduleRepo(session)
        users_service, schedules_service = UserService(users_repo), ScheduleService(schedules_repo)

        server = grpc.aio.server()
        add_UserServiceServicer_to_server(GrpcUserService(users_service), server)
        add_SchedulesServiceServicer_to_server(GrpcScheduleService(schedules_service, users_service), server)

        server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
        await server.start()
        await server.wait_for_termination()


if __name__ == "__main__":
    import asyncio

    asyncio.run(serve())
