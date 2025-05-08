import grpc
from aibolit.transport.grpc.generated import user_pb2, user_pb2_grpc

# from aibolit.users.service import get_users, validate_user_exists, create_user
from aibolit.services.users_service import UserService
from aibolit.transport.rest.users.schemas import UserCreateRequest


# def db_context_manager(func):
#     @wraps(func)
#     async def wrapper(self, request, context):
#         async with get_db_ctx() as db:
#             return await func(self, request, context, db)
#
#     return wrapper


# class GrpcScheduleService(schedule_pb2_grpc.SchedulesServiceServicer):
#     def __init__(
#         self,
#
#         schedules_service: ScheduleService,
#         users_service: UserService
#     ) -> None:
#         self._schedules_service = schedules_service
#         self._users_service = users_service
#
#     async def CreateSchedule(self, request, context: grpc.aio.ServicerContext):
#         start_date = request.start_date.ToDatetime().date()
#         schedule_data = MedicationScheduleCreateRequest(
#             medication_name=request.medication_name,
#             frequency=request.frequency,
#             duration_days=request.duration_days,
#             start_date=start_date,
#             user_id=request.user_id,
#         )
#         user_exists = await self._users_service.get_user_by_id(user_id=schedule_data.user_id)
#         if not user_exists:
#             context.set_code(grpc.StatusCode.NOT_FOUND)
#             context.set_details(f"User with id={schedule_data.user_id} not found")
#         db_schedule = await self._schedules_service.create_schedule(schedule_data)
#         return schedule_pb2.CreateScheduleResponse(schedule_id=db_schedule.id)  # type: ignore
#
#     @db_context_manager
#     async def GetAllSchedules(self, request, context: grpc.aio.ServicerContext, db):
#         db_schedules = await get_schedules(request.user_id, db)
#         schedules = [MedicationSchedule.model_validate(schedule).id for schedule in db_schedules]
#         return schedule_pb2.GetAllSchedulesResponse(user_id=request.user_id, schedules=schedules)  # type: ignore
#
#     @db_context_manager
#     async def GetUserSchedule(self, request, context: grpc.aio.ServicerContext, db):
#         db_schedule = await get_user_schedule(request.schedule_id, user_id=request.user_id, db=db)
#         schedule_dict = MedicationSchedule.model_validate(db_schedule).model_dump(mode='python')
#         start_date = schedule_dict.pop("start_date")
#         start_ts = Timestamp()
#         start_ts.FromDatetime(datetime.combine(start_date, time.min))
#         end_date = schedule_dict.pop("end_date")
#         end_ts = Timestamp()
#         end_ts.FromDatetime(datetime.combine(end_date, time.min))
#         return schedule_pb2.MedicationSchedule(**schedule_dict, start_date=start_ts, end_date=end_ts)  # type: ignore
#
#     @db_context_manager
#     async def GetUserNextTakings(self, request, context: grpc.aio.ServicerContext, db):
#         db_schedules = await get_schedules(request.user_id, db=db)
#         schedules = [MedicationSchedule.model_validate(schedule) for schedule in db_schedules]
#         next_takings = [
#             schedule_pb2.NextTakingsMedications(  # type: ignore
#                 schedule_id=next_taking.id,
#                 schedule_name=next_taking.medication_name,
#                 schedule_times=list(filter(is_within_timeframe, next_taking.daily_plan)),  # type: ignore
#             )
#             for next_taking in schedules
#             if any(map(is_within_timeframe, next_taking.daily_plan))  # type: ignore
#         ]
#         return schedule_pb2.GetUserNextTakingsResponse(user_id=request.user_id, next_takings=next_takings)
#
#
class GrpcUserService(user_pb2_grpc.UserServiceServicer):
    def __init__(self, user_service: UserService):
        self._user_service = user_service

    async def CreateUser(self, request, context: grpc.aio.ServicerContext):
        user_pb2.CreateUserRequest()
        db_user = await self._user_service.create_user(UserCreateRequest())
        return user_pb2.CreateUserResponse(id=db_user)

    # async def GetUsers(self, request, context: grpc.aio.ServicerContext, db):
    #     db_users = await get_users(db)
    #     users = [user_pb2.User(id=user.id) for user in db_users]
    #     return user_pb2.GetAllUsersResponse(users=users)
