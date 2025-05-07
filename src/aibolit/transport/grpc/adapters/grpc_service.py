from datetime import datetime, time
from functools import wraps
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from aibolit.transport.rest.schedules.schemas import MedicationSchedule, MedicationScheduleCreate
from aibolit.schedules.service import create_schedule, get_schedules, get_user_schedule
from aibolit.schedules.utils import is_within_timeframe
from aibolit.grpc_service.generated import schedule_pb2_grpc, user_pb2, user_pb2_grpc, schedule_pb2
from aibolit.database import get_db_ctx
from aibolit.users.service import get_users, validate_user_exists, create_user


def db_context_manager(func):
    @wraps(func)
    async def wrapper(self, request, context):
        async with get_db_ctx() as db:
            return await func(self, request, context, db)

    return wrapper


class ScheduleService(schedule_pb2_grpc.SchedulesServiceServicer):
    @db_context_manager
    async def CreateSchedule(self, request, context: grpc.aio.ServicerContext, db):
        start_date = request.start_date.ToDatetime().date()
        schedule_data = MedicationScheduleCreate(
            medication_name=request.medication_name,
            frequency=request.frequency,
            duration_days=request.duration_days,
            start_date=start_date,
            user_id=request.user_id,
        )
        user_exists = await validate_user_exists(schedule_data.user_id, db=db)
        if not user_exists:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User with id={schedule_data.user_id} not found")
        db_schedule = await create_schedule(schedule_data, db)
        return schedule_pb2.CreateScheduleResponse(schedule_id=db_schedule.id)  # type: ignore

    @db_context_manager
    async def GetAllSchedules(self, request, context: grpc.aio.ServicerContext, db):
        db_schedules = await get_schedules(request.user_id, db)
        schedules = [MedicationSchedule.model_validate(schedule).id for schedule in db_schedules]
        return schedule_pb2.GetAllSchedulesResponse(user_id=request.user_id, schedules=schedules)  # type: ignore

    @db_context_manager
    async def GetUserSchedule(self, request, context: grpc.aio.ServicerContext, db):
        db_schedule = await get_user_schedule(request.schedule_id, user_id=request.user_id, db=db)
        schedule_dict = MedicationSchedule.model_validate(db_schedule).model_dump(mode='python')
        start_date = schedule_dict.pop("start_date")
        start_ts = Timestamp()
        start_ts.FromDatetime(datetime.combine(start_date, time.min))
        end_date = schedule_dict.pop("end_date")
        end_ts = Timestamp()
        end_ts.FromDatetime(datetime.combine(end_date, time.min))
        return schedule_pb2.MedicationSchedule(**schedule_dict, start_date=start_ts, end_date=end_ts)  # type: ignore

    @db_context_manager
    async def GetUserNextTakings(self, request, context: grpc.aio.ServicerContext, db):
        db_schedules = await get_schedules(request.user_id, db=db)
        schedules = [MedicationSchedule.model_validate(schedule) for schedule in db_schedules]
        next_takings = [
            schedule_pb2.NextTakingsMedications(  # type: ignore
                schedule_id=next_taking.id,
                schedule_name=next_taking.medication_name,
                schedule_times=list(filter(is_within_timeframe, next_taking.daily_plan)),  # type: ignore
            )
            for next_taking in schedules
            if any(map(is_within_timeframe, next_taking.daily_plan))  # type: ignore
        ]
        return schedule_pb2.GetUserNextTakingsResponse(user_id=request.user_id, next_takings=next_takings)


class UserService(user_pb2_grpc.UserServiceServicer):
    @db_context_manager
    async def CreateUser(self, request, context: grpc.aio.ServicerContext, db):
        user_data = user_pb2.CreateUserRequest()
        db_user = await create_user(user_data, db)
        return user_pb2.CreateUserResponse(id=db_user.id)

    @db_context_manager
    async def GetUsers(self, request, context: grpc.aio.ServicerContext, db):
        db_users = await get_users(db)
        users = [user_pb2.User(id=user.id) for user in db_users]
        return user_pb2.GetAllUsersResponse(users=users)
