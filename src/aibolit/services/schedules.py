from datetime import date, datetime, timedelta
from typing import List
from aibolit.core.logger import get_logger
from aibolit.models.schedules import MedicationScheduleOrm
from aibolit.repositories.schedules import ScheduleRepo

from aibolit.schemas.openapi_generated import (
    # from aibolit.schemas.schedules import (
    MedicationSchedule,
    MedicationScheduleCreateRequest,
    MedicationScheduleCreateResponse,
    MedicationScheduleIdsResponse,
    NextTakingsMedications,
    NextTakingsMedicationsResponse,
)
from aibolit.core.config import settings
from aibolit.core.exceptions import ScheduleExpiredError, ScheduleNotFoundError, ScheduleNotStartedError

logger = get_logger(__name__)


class ScheduleService:
    def __init__(self, schedules_repo: ScheduleRepo) -> None:
        self._schedules_repo = schedules_repo

    async def create_schedule(self, schedule: MedicationScheduleCreateRequest) -> MedicationScheduleCreateResponse:
        logger.info("Creating schedule", user_id=schedule.user_id)
        schedule = await self._schedules_repo.create_schedule(schedule)
        logger.info(f"Schedule created with id={schedule.id}, for user={schedule.user_id}")
        return MedicationScheduleCreateResponse(schedule_id=schedule.id)

    async def get_all_user_schedules(self, user_id: int) -> MedicationScheduleIdsResponse:
        logger.info("Fetching all schedules for user", user_id=user_id)
        db_schedules = await self._schedules_repo.get_all_user_schedules(user_id)
        schedules_with_plan = self._schedules_with_plan(db_schedules)
        schedules = [schedule.id for schedule in schedules_with_plan]
        logger.info("Fetched user schedules", user_id=user_id, schedule_count=len(schedules))
        return MedicationScheduleIdsResponse(user_id=user_id, schedules=schedules)

    async def get_user_schedule(self, user_id: int, schedule_id: int) -> MedicationSchedule:
        logger.info("Fetching schedule", user_id=user_id, schedule_id=schedule_id)
        db_schedule = await self._schedules_repo.get_user_schedule(schedule_id, user_id)
        if not db_schedule:
            logger.warning("Schedule not found", user_id=user_id, schedule_id=schedule_id)
            raise ScheduleNotFoundError(schedule_id, user_id)
        if db_schedule.end_date and db_schedule.end_date < date.today():
            logger.warning("Schedule is expired", schedule_id=schedule_id, end_date=str(db_schedule.end_date))
            raise ScheduleExpiredError(db_schedule.medication_name, db_schedule.end_date)
        if db_schedule.start_date > date.today():
            raise ScheduleNotStartedError(db_schedule.medication_name, db_schedule.start_date)
        schedule = self._one_schedule_with_plan(db_schedule)
        return schedule

    async def get_user_next_takings(self, user_id: int) -> NextTakingsMedicationsResponse:
        logger.info("Fetching next takings", user_id=user_id)
        user_db_schedules = await self._schedules_repo.get_all_user_schedules(user_id)
        schedules = self._schedules_with_plan(user_db_schedules)
        next_takings = [
            NextTakingsMedications(
                schedule_id=next_taking.id,
                schedule_name=next_taking.medication_name,
                schedule_times=list(filter(self._is_within_timeframe, next_taking.daily_plan)),
            )
            for next_taking in schedules
            if any(map(self._is_within_timeframe, next_taking.daily_plan))
        ]
        logger.info("Next takings determined", user_id=user_id, count=len(next_takings))
        return NextTakingsMedicationsResponse(user_id=user_id, next_takings=next_takings)

    def _schedules_with_plan(self, db_schedules: List[MedicationScheduleOrm]) -> List[MedicationSchedule]:
        return [self._one_schedule_with_plan(db_schedule) for db_schedule in db_schedules]

    def _one_schedule_with_plan(self, db_schedule) -> MedicationSchedule:
        daily_plan = self._generate_daily_plan(db_schedule.frequency)
        schedule = MedicationSchedule(**db_schedule.__dict__, daily_plan=daily_plan)
        return MedicationSchedule.model_validate(schedule)

    def _generate_daily_plan(self, frequency: int) -> List[str]:
        """
        Generate a list of time strings ("HH:MM") representing medication intake times.
        Times are evenly distributed between TIME_DAY_START and TIME_DAY_END (from settings),
        each rounded up to the nearest TIME_ROUNDING_INTERVAL.
        """
        start_day = datetime.combine(date.today(), settings.TIME_DAY_START)
        end_day = datetime.combine(date.today(), settings.TIME_DAY_END)
        if frequency == 1:
            return [start_day.strftime("%H:%M")]
        interval = (end_day - start_day) / (frequency - 1)
        times = [self._round_to_next_interval(start_day + i * interval).strftime("%H:%M") for i in range(frequency)]
        return times

    @staticmethod
    def _round_to_next_interval(dt: datetime) -> datetime:
        interval = settings.TIME_ROUNDING_INTERVAL
        minutes = dt.minute
        rounded_minutes = (minutes + (interval - 1)) // interval * interval
        if rounded_minutes == 60:
            return dt.replace(minute=0, second=0) + timedelta(hours=1)
        return dt.replace(minute=rounded_minutes, second=0)

    @staticmethod
    def _is_within_timeframe(time_str: str) -> bool:
        """Check if medication intake time is within allowed timeframe considering:
        - Daily time limits (TIME_DAY_START/END)
        - Active intake grace period (INTAKE_WINDOW)
        - Upcoming intake window (NEXT_TAKINGS_PERIOD)
        """
        current_datetime = datetime.now()
        current_time = current_datetime.time()
        target_datetime = datetime.strptime(time_str, "%H:%M")
        window_end_time = (target_datetime + timedelta(minutes=settings.INTAKE_WINDOW)).time()
        time_upper_limit = (current_datetime + timedelta(minutes=settings.NEXT_TAKINGS_PERIOD)).time()
        target_time = target_datetime.time()

        is_within_day_limits = settings.TIME_DAY_START <= target_time <= settings.TIME_DAY_END
        is_upcoming = current_time <= target_time <= time_upper_limit
        is_active = target_time <= current_time <= window_end_time
        return is_within_day_limits and (is_upcoming or is_active)
