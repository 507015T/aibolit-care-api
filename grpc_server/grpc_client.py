from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / ".."))
from google.protobuf.timestamp_pb2 import Timestamp
import grpc

from grpc_server import medications_pb2, medications_pb2_grpc, users_pb2, users_pb2_grpc


async def run():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = medications_pb2_grpc.MedicationServiceStub(channel)
        print("1. Create Schedule")
        print("2. Get All Schedules")
        print("3. Get User Schedule")
        print("4. Get User Next Takings")
        print("5. Create User")
        print("6. Get All Users")
        rpc_call = input("Which rpc would you like to make: ")

        if rpc_call == "1":
            start_date = Timestamp()
            start_date.FromDatetime(datetime.now())
            request = medications_pb2.CreateScheduleRequest(  # type: ignore
                user_id=1, medication_name="Test Medication", start_date=start_date, frequency=15, duration_days=10
            )
            reply = await stub.CreateSchedule(request)
            print("Create Schedule Response Received:")
            print(reply)
        if rpc_call == "2":
            request = medications_pb2.GetAllSchedulesRequest(user_id=1)  # type: ignore
            reply = await stub.GetAllSchedules(request)
            print("Get All Schedules Response Received:")
            print(reply)
        if rpc_call == "3":
            request = medications_pb2.GetUserScheduleRequest(user_id=1, schedule_id=2)  # type:ignore
            reply = await stub.GetUserSchedule(request)
            print("Get User Schedule Response Received.")
            print(reply)

        if rpc_call == "4":
            request = medications_pb2.GetUserNextTakingsRequest(user_id=1)  # type: ignore
            reply = await stub.GetUserNextTakings(request)
            print("Get User Next Takings Response Received.")
            print(reply)
        stub = users_pb2_grpc.UserServiceStub(channel)
        if rpc_call == "5":
            request = users_pb2.CreateUserRequest()
            reply = await stub.CreateUser(request)
            print("Create User Response Received.")
            print(reply)
        if rpc_call == "6":
            request = users_pb2.GetAllUsersRequest()
            reply = await stub.GetUsers(request)
            print("Get All Users Response Received.")
            print(reply)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
