from concurrent import futures
import grpc
from aibolit.core.logger import configure_logging, get_logger
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

configure_logging()
logger = get_logger(__name__)


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))

    async with get_db_grpc() as session:
        users_repo, schedules_repo = UserRepo(session), ScheduleRepo(session)
        users_service, schedules_service = UserService(users_repo), ScheduleService(schedules_repo)

        server = grpc.aio.server()
        add_UserServiceServicer_to_server(GrpcUserService(users_service), server)
        add_SchedulesServiceServicer_to_server(GrpcScheduleService(schedules_service, users_service), server)

        server.add_insecure_port(f"[::]:{settings.GRPC_PORT}")
        logger.info(f"gRPC server started on port {settings.GRPC_PORT}")
        await server.start()
        try:
            await server.wait_for_termination()
        except asyncio.CancelledError:
            logger.info("Shutting down gRPC server...")
            await server.stop(grace=5)
            raise


if __name__ == "__main__":
    import sys
    import asyncio

    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
