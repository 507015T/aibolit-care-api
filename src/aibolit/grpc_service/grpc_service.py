from datetime import datetime, time
from functools import wraps
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from aibolit.schedules.schemas import MedicationSchedule, MedicationScheduleCreate
from aibolit.schedules.service import create_schedule, get_schedules, get_user_schedule
from aibolit.schedules.utils import is_within_timeframe
from aibolit.grpc_service.generated import users_pb2, users_pb2_grpc
from aibolit.database import get_db_ctx
from aibolit.users.service import get_users, validate_user_exists, create_user
from aibolit.users.schemas import UserCreate
from aibolit.grpc_service.generated import medications_pb2, medications_pb2_grpc


def db_context_manager(func):
    @wraps(func)
    async def wrapper(self, request, context):
        async with get_db_ctx() as db:
            return await func(self, request, context, db)

    return wrapper


class MedicationService(medications_pb2_grpc.MedicationServiceServicer):
    @db_context_manager
    async def CreateSchedule(self, request, context, db):
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
        return medications_pb2.CreateScheduleResponse(schedule_id=db_schedule.id)  # type: ignore

    @db_context_manager
    async def GetAllSchedules(self, request, context, db):
        db_schedules = await get_schedules(request.user_id, db)
        schedules = [MedicationSchedule.model_validate(schedule).id for schedule in db_schedules]
        return medications_pb2.GetAllSchedulesResponse(user_id=request.user_id, schedules=schedules)  # type: ignore

    @db_context_manager
    async def GetUserSchedule(self, request, context, db):
        db_schedule = await get_user_schedule(request.schedule_id, user_id=request.user_id, db=db)
        schedule_dict = MedicationSchedule.model_validate(db_schedule).model_dump(mode='python')
        start_date = schedule_dict.pop("start_date")
        start_ts = Timestamp()
        start_ts.FromDatetime(datetime.combine(start_date, time.min))
        end_date = schedule_dict.pop("end_date")
        end_ts = Timestamp()
        end_ts.FromDatetime(datetime.combine(end_date, time.min))
        return medications_pb2.MedicationSchedule(**schedule_dict, start_date=start_ts, end_date=end_ts)  # type: ignore

    @db_context_manager
    async def GetUserNextTakings(self, request, context, db):
        db_schedules = await get_schedules(request.user_id, db=db)
        schedules = [MedicationSchedule.model_validate(schedule) for schedule in db_schedules]
        next_takings = [
            medications_pb2.NextTakingsMedications(  # type: ignore
                schedule_id=next_taking.id,
                schedule_name=next_taking.medication_name,
                schedule_times=list(filter(is_within_timeframe, next_taking.daily_plan)),  # type: ignore
            )
            for next_taking in schedules
            if any(map(is_within_timeframe, next_taking.daily_plan))  # type: ignore
        ]
        return medications_pb2.GetUserNextTakingsResponse(user_id=request.user_id, next_takings=next_takings)


class UserService(users_pb2_grpc.UserServiceServicer):
    @db_context_manager
    async def CreateUser(self, request, context, db):
        user_data = UserCreate()
        db_user = await create_user(user_data, db)
        return users_pb2.CreateUserResponse(id=db_user.id)

    @db_context_manager
    async def GetUsers(self, request, context, db):
        db_users = await get_users(db)
        users = [users_pb2.User(id=user.id) for user in db_users]
        return users_pb2.GetAllUsersResponse(users=users)
