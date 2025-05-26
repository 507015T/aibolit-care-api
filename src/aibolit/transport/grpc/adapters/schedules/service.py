from datetime import date, datetime, time
from google.protobuf.timestamp_pb2 import Timestamp
import grpc
from aibolit.transport.grpc.generated.schedule_pb2_grpc import SchedulesServiceServicer
from aibolit.transport.grpc.generated import schedule_pb2
from aibolit.services.users.service import UserService
from aibolit.services.schedules.service import ScheduleService
from aibolit.core.exceptions import ScheduleExpiredError, ScheduleNotFoundError, ScheduleNotStartedError
from aibolit.schemas.schedules.schemas import MedicationScheduleCreateRequest, MedicationSchedule
from aibolit.core.logger import get_logger

logger = get_logger(__name__)


class GrpcScheduleService(SchedulesServiceServicer):
    def __init__(self, schedules_service: ScheduleService, users_service: UserService) -> None:
        self._schedules_service = schedules_service
        self._users_service = users_service

    async def CreateSchedule(self, request, context: grpc.aio.ServicerContext):
        logger.info("gRPC CreateSchedule called", user_id=request.user_id, medication_name=request.medication_name)
        start_date = request.start_date.ToDatetime().date() if len(str(request.start_date)) else date.today()
        schedule_data = MedicationScheduleCreateRequest(
            medication_name=request.medication_name,
            frequency=request.frequency,
            duration_days=request.duration_days or None,
            start_date=start_date,
            user_id=request.user_id,
        )
        user_exists = await self._users_service.get_user_by_id(user_id=schedule_data.user_id)
        if not user_exists:
            logger.warning("User not found", user_id=schedule_data.user_id)
            await context.abort(grpc.StatusCode.NOT_FOUND, f"User with id={schedule_data.user_id} not found")
        schedule_id = await self._schedules_service.create_schedule(schedule_data)
        return schedule_pb2.CreateScheduleResponse(schedule_id=schedule_id.schedule_id)

    async def GetAllSchedules(self, request, context: grpc.aio.ServicerContext):
        logger.info("gRPC GetAllSchedules called", user_id=request.user_id)
        schedules = await self._schedules_service.get_all_user_schedules(request.user_id)
        return schedule_pb2.GetAllSchedulesResponse(user_id=schedules.user_id, schedules=schedules.schedules)

    async def GetUserSchedule(self, request, context: grpc.aio.ServicerContext):
        logger.info("gRPC GetUserSchedule called", user_id=request.user_id, schedule_id=request.schedule_id)

        try:
            schedule = await self._schedules_service.get_user_schedule(
                schedule_id=request.schedule_id, user_id=request.user_id
            )
        except ScheduleNotFoundError as e:
            logger.warning("Schedule not found", user_id=request.user_id, schedule_id=request.schedule_id)
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))

        except ScheduleExpiredError as e:
            logger.info("Schedule expired", user_id=request.user_id, schedule_id=request.schedule_id)
            await context.abort(grpc.StatusCode.FAILED_PRECONDITION, str(e))

        except ScheduleNotStartedError as e:
            logger.info("Schedule hasn't started yet", user_id=request.user_id, schedule_ind=request.schedule_id)
            await context.abort(grpc.StatusCode.FAILED_PRECONDITION, str(e))

        schedule_dict = MedicationSchedule(**schedule.model_dump(mode="python")).model_dump(mode="python")
        start_date, end_date = schedule_dict.pop("start_date"), schedule_dict.pop("end_date")
        return schedule_pb2.MedicationSchedule(
            **schedule_dict, start_date=self._to_timestamp(start_date), end_date=self._to_timestamp(end_date)
        )

    async def GetUserNextTakings(self, request, context: grpc.aio.ServicerContext):
        logger.info("gRPC GetUserNextTakings called", user_id=request.user_id)
        schedules = await self._schedules_service.get_user_next_takings(request.user_id)
        next_takings = [
            schedule_pb2.NextTakingsMedications(**next_taking.model_dump(mode='python'))
            for next_taking in schedules.next_takings
        ]
        return schedule_pb2.GetUserNextTakingsResponse(user_id=request.user_id, next_takings=next_takings)

    @staticmethod
    def _to_timestamp(dt: date) -> Timestamp:
        ts = Timestamp()
        ts.FromDatetime(datetime.combine(dt, time.min))
        return ts
