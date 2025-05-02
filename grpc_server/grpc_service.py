from datetime import datetime, time
from functools import wraps
import grpc
from src.database import get_db_ctx
from src.users.service import validate_user_exists
from . import medications_pb2, medications_pb2_grpc
from src.schedules import service, schemas, utils
from google.protobuf.timestamp_pb2 import Timestamp


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
        schedule_data = schemas.MedicationScheduleCreate(
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
        db_schedule = await service.create_schedule(schedule_data, db)
        return medications_pb2.CreateScheduleResponse(schedule_id=db_schedule.id)  # type: ignore

    @db_context_manager
    async def GetAllSchedules(self, request, context, db):
        db_schedules = await service.get_schedules(request.user_id, db)
        schedules = [schemas.MedicationSchedule.model_validate(schedule).id for schedule in db_schedules]
        return medications_pb2.GetAllSchedulesResponse(user_id=request.user_id, schedules=schedules)  # type: ignore

    @db_context_manager
    async def GetUserSchedule(self, request, context, db):
        db_schedule = await service.get_user_schedule(request.schedule_id, user_id=request.user_id, db=db)
        schedule_dict = schemas.MedicationSchedule.model_validate(db_schedule).model_dump(mode='python')
        start_date = schedule_dict.pop("start_date")
        start_ts = Timestamp()
        start_ts.FromDatetime(datetime.combine(start_date, time.min))
        end_date = schedule_dict.pop("end_date")
        end_ts = Timestamp()
        end_ts.FromDatetime(datetime.combine(end_date, time.min))
        return medications_pb2.MedicationSchedule(**schedule_dict, start_date=start_ts, end_date=end_ts)  # type: ignore

    @db_context_manager
    async def GetUserNextTakings(self, request, context, db):
        db_schedules = await service.get_schedules(request.user_id, db=db)
        schedules = [schemas.MedicationSchedule.model_validate(schedule) for schedule in db_schedules]
        next_takings = [
            medications_pb2.NextTakingsMedications(  # type: ignore
                schedule_id=next_taking.id,
                schedule_name=next_taking.medication_name,
                schedule_times=list(filter(utils.is_within_timeframe, next_taking.daily_plan)),  # type: ignore
            )
            for next_taking in schedules
            if any(map(utils.is_within_timeframe, next_taking.daily_plan))  # type: ignore
        ]
        return medications_pb2.GetUserNextTakingsResponse(user_id=request.user_id, next_takings=next_takings)
