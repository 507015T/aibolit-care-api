import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / ".."))
import grpc
from src.config import settings

from grpc_server import medications_pb2_grpc
from grpc_server.grpc_service import MedicationService


async def serve():
    server = grpc.aio.server()
    medications_pb2_grpc.add_MedicationServiceServicer_to_server(MedicationService(), server)
    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    await server.start()
    print(f"gRPC server started on port {settings.GRPC_PORT}")
    await server.wait_for_termination()


if __name__ == "__main__":
    import asyncio

    asyncio.run(serve())
