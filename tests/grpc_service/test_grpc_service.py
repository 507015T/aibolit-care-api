#
# @pytest_asyncio.fixture
# async def grpc_test_channel(get_testing_db: AsyncSession):
#     server = grpc.aio.server()
#     medications_pb2_grpc.add_MedicationServiceServicer_to_server(grpc_main.MedicationService(), server)
#     # users_pb2_grpc.add_UserServiceServicer_to_server(grpc_main.UserService(db_session=get_testing_db), server)
#     port = server.add_insecure_port('[::]:0')
#     await server.start()
#
#     channel = grpc.aio.insecure_channel(f"localhost:{port}")
#     try:
#         yield channel
#     finally:
#         await channel.close()
#         await server.stop(0)
#
#
# @pytest.mark.asyncio
# async def test_post_schedule(grpc_test_channel, get_testing_db: AsyncSession):
#     # user_stub = users_pb2_grpc.UserServiceStub(grpc_test_channel)
#     # request_user = users_pb2.CreateUserRequest()
#     # response = await user_stub.CreateUser(request_user)
#     # print(type(response))
#     # assert 1 == response.id
#     stub = medications_pb2_grpc.MedicationServiceStub(grpc_test_channel)
#     start_date = Timestamp()
#     start_date.FromDatetime(datetime.now())
#     request = medications_pb2.CreateScheduleRequest(
#         user_id=1,
#         medication_name="Test Medication",
#         start_date=start_date,
#         frequency=15,
#         duration_days=10,
#     )
#     response = await stub.CreateSchedule(request)
#     assert 'lol' == response

# if rpc_call == "1":
#     request = medications_pb2.CreateScheduleRequest(  # type: ignore
#         user_id=1, medication_name="Test Medication", start_date=start_date, frequency=15, duration_days=10
#     )
#     reply = await stub.CreateSchedule(request)
#     print("Create Schedule Response Received:")
#     print(reply)
# if rpc_call == "2":
#     request = medications_pb2.GetAllSchedulesRequest(user_id=1)  # type: ignore
#     reply = await stub.GetAllSchedules(request)
#     print("Get All Schedules Response Received:")
#     print(reply)
# if rpc_call == "3":
#     request = medications_pb2.GetUserScheduleRequest(user_id=1, schedule_id=2)  # type:ignore
#     reply = await stub.GetUserSchedule(request)
#     print("Get User Schedule Response Received.")
#     print(reply)
#
# if rpc_call == "4":
#     request = medications_pb2.GetUserNextTakingsRequest(user_id=1)  # type: ignore
#     reply = await stub.GetUserNextTakings(request)
#     print("Get User Next Takings Response Received.")
#     print(reply)
