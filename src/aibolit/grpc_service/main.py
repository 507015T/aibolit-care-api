import grpc
from aibolit.config import settings
from aibolit.grpc_service.generated.schedule_pb2_grpc import add_SchedulesServiceServicer_to_server
from aibolit.grpc_service.generated.user_pb2_grpc import add_UserServiceServicer_to_server
from aibolit.grpc_service.adapters.grpc_service import ScheduleService, UserService


async def serve():
    server = grpc.aio.server()
    add_SchedulesServiceServicer_to_server(ScheduleService(), server)
    add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    await server.start()
    print(f"gRPC server started on port {settings.GRPC_PORT}")
    await server.wait_for_termination()


if __name__ == "__main__":
    import asyncio

    asyncio.run(serve())
