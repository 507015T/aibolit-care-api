import grpc
from aibolit.config import settings
from aibolit.grpc_service.generated import medications_pb2_grpc, users_pb2_grpc
from aibolit.grpc_service.grpc_service import MedicationService, UserService


async def serve():
    server = grpc.aio.server()
    medications_pb2_grpc.add_MedicationServiceServicer_to_server(MedicationService(), server)
    users_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    await server.start()
    print(f"gRPC server started on port {settings.GRPC_PORT}")
    await server.wait_for_termination()


if __name__ == "__main__":
    import asyncio

    asyncio.run(serve())
