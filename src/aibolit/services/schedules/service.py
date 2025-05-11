from datetime import date, datetime, timedelta
from typing import List
from aibolit.models.schedules.models import MedicationScheduleOrm
from aibolit.repositories.schedules.repository import ScheduleRepo
from aibolit.schemas.schedules.schemas import (
    MedicationSchedule,
    MedicationScheduleCreateRequest,
    MedicationScheduleCreateResponse,
    MedicationScheduleIdsResponse,
    NextTakingsMedications,
    NextTakingsMedicationsResponse,
)

from aibolit.core.config import settings


class ScheduleExpiredError(Exception):
    pass


class ScheduleNotFound(Exception):
    pass


class ScheduleService:
    def __init__(self, schedules_repo: ScheduleRepo) -> None:
        self._schedules_repo = schedules_repo

    async def create_schedule(self, schedule: MedicationScheduleCreateRequest) -> MedicationScheduleCreateResponse:
        schedule = await self._schedules_repo.create_schedule(schedule)
        return MedicationScheduleCreateResponse(schedule_id=schedule.id)

    async def get_all_user_schedules(self, user_id: int) -> MedicationScheduleIdsResponse:
        db_schedules = await self._schedules_repo.get_all_user_schedules(user_id)
        schedules_with_plan = await self._schedules_with_plan(db_schedules)
        schedules = [schedule.id for schedule in schedules_with_plan]
        return MedicationScheduleIdsResponse(user_id=user_id, schedules=schedules)

    async def get_user_schedule(self, user_id: int, schedule_id: int) -> MedicationSchedule:
        db_schedule = await self._schedules_repo.get_user_schedule(schedule_id, user_id)
        if not db_schedule:
            raise ScheduleNotFound(f"The medication schedule with id={schedule_id} for user={user_id} not found")
        if db_schedule.end_date and db_schedule.end_date < date.today():
            raise ScheduleExpiredError(
                f"The medication '{db_schedule.medication_name}' intake ended on {db_schedule.end_date}"
            )
        schedule = await self._one_schedule_with_plan(db_schedule)
        return schedule

    async def get_user_next_takings(self, user_id: int) -> NextTakingsMedicationsResponse:
        user_db_schedules = await self._schedules_repo.get_all_user_schedules(user_id)
        schedules = await self._schedules_with_plan(user_db_schedules)
        next_takings = [
            NextTakingsMedications(
                schedule_id=next_taking.id,
                schedule_name=next_taking.medication_name,
                schedule_times=list(filter(self._is_within_timeframe, next_taking.daily_plan)),
            )
            for next_taking in schedules
            if any(map(self._is_within_timeframe, next_taking.daily_plan))
        ]

        return NextTakingsMedicationsResponse(user_id=user_id, next_takings=next_takings)

    def _is_within_timeframe(self, time_str) -> bool:
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

    async def _generate_daily_plan(self, frequency) -> List[str]:
        start_day = datetime.strptime("8:00", "%H:%M")
        end_day = datetime.strptime("22:00", "%H:%M")
        if frequency == 1:
            return ["8:00"]
        interval = (end_day - start_day) / (frequency - 1)
        times = []
        for freq in range(frequency):
            estimated_time = start_day + (freq * interval)
            minutes_of_estimated_time = estimated_time.minute
            new_minutes_of_estimated_time = (minutes_of_estimated_time + 14) // 15 * 15
            if new_minutes_of_estimated_time == 60:
                estimated_time = estimated_time.replace(minute=0) + timedelta(hours=1)
            else:
                estimated_time = estimated_time.replace(minute=new_minutes_of_estimated_time)
            times.append(estimated_time.strftime("%H:%M"))

        return times

    async def _one_schedule_with_plan(self, db_schedule) -> MedicationSchedule:
        daily_plan = await self._generate_daily_plan(db_schedule.frequency)
        schedule = MedicationSchedule(**db_schedule.__dict__, daily_plan=daily_plan)
        return MedicationSchedule.model_validate(schedule)

    async def _schedules_with_plan(self, db_schedules: List[MedicationScheduleOrm]) -> List[MedicationSchedule]:
        return [await self._one_schedule_with_plan(db_schedule) for db_schedule in db_schedules]
