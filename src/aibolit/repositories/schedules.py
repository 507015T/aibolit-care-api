from datetime import date, timedelta
from operator import or_
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aibolit.models.schedules import MedicationScheduleOrm

# from aibolit.schemas.schedules import MedicationScheduleCreateRequest
from aibolit.schemas.openapi_generated import MedicationScheduleCreateRequest


class ScheduleRepo:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_schedule(self, schedule: MedicationScheduleCreateRequest) -> MedicationScheduleOrm:
        schedule.start_date = date.today() if not schedule.start_date else schedule.start_date
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
            .filter(MedicationScheduleOrm.start_date <= date.today())
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
        return schedule
