from datetime import date, timedelta
from operator import or_
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aibolit.models.schedule import MedicationScheduleOrm
from aibolit.transport.rest.schedules.schemas import MedicationScheduleCreateRequest


class SchedulesRepo:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_schedule(self, schedule: MedicationScheduleCreateRequest) -> MedicationScheduleOrm:
        end_date = schedule.start_date + timedelta(days=schedule.duration_days) if schedule.duration_days else None
        db_schedule = MedicationScheduleOrm(end_date=end_date, **schedule.model_dump())
        self._db.add(db_schedule)
        await self._db.commit()
        await self._db.refresh(db_schedule)
        return db_schedule

    async def get_all_user_schedules(self, user_id: int) -> Optional[Sequence[MedicationScheduleOrm]]:

        db_request = await self._db.execute(
            select(MedicationScheduleOrm)
            .filter(MedicationScheduleOrm.user_id == user_id)
            .filter(
                or_(
                    MedicationScheduleOrm.end_date >= date.today(),
                    MedicationScheduleOrm.end_date.is_(None),
                ),
            ),
        )
        db_schedules = db_request.scalars().all()
        return db_schedules

    async def get_user_schedule(self, schedule_id: int, user_id: int) -> Optional[MedicationScheduleOrm]:
        result = await self._db.execute(
            select(MedicationScheduleOrm)
            .filter(MedicationScheduleOrm.id == schedule_id)
            .filter(MedicationScheduleOrm.user_id == user_id)
        )
        schedule = result.scalars().first()
        # # TODO: ВЫНЕСТИ ЭТО НАХУЙ ОТСЮДА И ПОМЕСТИТЬ В SERVICES
        # if schedule.end_date and schedule.end_date < date.today():
        #     raise HTTPException(
        #         status_code=404,
        #         detail=f"The medication '{schedule.medication_name}' intake ended on {schedule.end_date}",
        #     )
        return schedule

    async def get_user_next_takings(self, user_id: int) -> Optional[Sequence[MedicationScheduleOrm]]:
        result = await self._db.execute(
            select(MedicationScheduleOrm)
            .filter(MedicationScheduleOrm.user_id == user_id)
            .filter(
                or_(
                    MedicationScheduleOrm.end_date >= date.today(),
                    MedicationScheduleOrm.end_date.is_(None),
                ),
            ),
        )
        schedules = result.scalars().all()
        return schedules
