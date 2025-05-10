from datetime import date, datetime, time
from google.protobuf.timestamp_pb2 import Timestamp
import grpc
from aibolit.transport.grpc.generated.schedule_pb2_grpc import SchedulesServiceServicer
from aibolit.transport.grpc.generated import schedule_pb2
from aibolit.services.users.service import UserService
from aibolit.services.schedules.service import ScheduleService
from aibolit.schemas.schedules.schemas import MedicationScheduleCreateRequest, MedicationSchedule


class GrpcScheduleService(SchedulesServiceServicer):
    def __init__(self, schedules_service: ScheduleService, users_service: UserService) -> None:
        self._schedules_service = schedules_service
        self._users_service = users_service

    async def CreateSchedule(self, request, context: grpc.aio.ServicerContext):
        start_date = request.start_date.ToDatetime().date() if len(str(request.start_date)) else date.today()
        schedule_data = MedicationScheduleCreateRequest(
            medication_name=request.medication_name,
            frequency=request.frequency,
            duration_days=request.duration_days if request.duration_days else None,
            start_date=start_date,
            user_id=request.user_id,
        )
        user_exists = await self._users_service.get_user_by_id(user_id=schedule_data.user_id)
        if not user_exists:
            await context.abort(grpc.StatusCode.NOT_FOUND, f"User with id={schedule_data.user_id} not found")
        schedule_id = await self._schedules_service.create_schedule(schedule_data)
        return schedule_pb2.CreateScheduleResponse(schedule_id=schedule_id.schedule_id)

    async def GetAllSchedules(self, request, context: grpc.aio.ServicerContext):
        schedules = await self._schedules_service.get_all_user_schedules(request.user_id)
        return schedule_pb2.GetAllSchedulesResponse(user_id=schedules.user_id, schedules=schedules.schedules)

    async def GetUserSchedule(self, request, context: grpc.aio.ServicerContext):
        schedule = await self._schedules_service.get_user_schedule(
            schedule_id=request.schedule_id, user_id=request.user_id
        )
        schedule_dict = MedicationSchedule(**schedule.model_dump(mode='python')).model_dump(mode='python')
        start_date = schedule_dict.pop("start_date")
        start_ts = Timestamp()
        start_ts.FromDatetime(datetime.combine(start_date, time.min))
        end_date = schedule_dict.pop("end_date")
        end_ts = Timestamp()
        end_ts.FromDatetime(datetime.combine(end_date, time.min))
        return schedule_pb2.MedicationSchedule(**schedule_dict, start_date=start_ts, end_date=end_ts)

    async def GetUserNextTakings(self, request, context: grpc.aio.ServicerContext):
        schedules = await self._schedules_service.get_user_next_takings(request.user_id)
        next_takings = schedules.next_takings[0]
        next_takings = schedule_pb2.NextTakingsMedications(**next_takings.model_dump(mode='pyton'))
        return schedule_pb2.GetUserNextTakingsResponse(user_id=request.user_id, next_takings=[next_takings])
