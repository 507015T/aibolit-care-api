from concurrent import futures
import grpc
from aibolit.config import settings
from aibolit.database import get_db_grpc
from aibolit.integrations.users_repo import UsersRepo
from aibolit.services.users_service import UserService
from aibolit.transport.grpc.generated.user_pb2_grpc import add_UserServiceServicer_to_server
from aibolit.transport.grpc.adapters.grpc_service import GrpcUserService


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))

    # schedules_repo = SchedulesRepo(get_schedules_repo(session))
    # users_repo = UsersRepo(get_users_repo(session))
    #
    # schedules_service = ScheduleService(schedules_repo=schedules_repo)
    # users_service = UserService(users_repo=users_repo)
    #
    # grpc_service = GrpcScheduleService(
    #     schedules_service=schedules_service,
    #     users_service=users_service,
    # )
    # add_SchedulesServiceServicer_to_server(grpc_service, server)

    async with get_db_grpc() as session:
        users_repo = UsersRepo(session)
        user_service = UserService(users_repo)

        add_UserServiceServicer_to_server(GrpcUserService(user_service=user_service), server)

        server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
        await server.start()
        print(f"gRPC server started on port {settings.GRPC_PORT}")
        await server.wait_for_termination()


if __name__ == "__main__":
    import asyncio

    asyncio.run(serve())
