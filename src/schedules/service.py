from datetime import date, timedelta
from operator import or_

from sqlalchemy import select

from schedules import models


async def create_schedule(schedule, db):
    end_date = schedule.start_date + timedelta(days=schedule.duration_days) if schedule.duration_days else None
    db_schedule = models.MedicationSchedule(end_date=end_date, **schedule.model_dump())
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return {"schedule_id": db_schedule.id}


async def get_schedules(user_id, db):

    result = await db.execute(
        select(models.MedicationSchedule)
        .filter(models.MedicationSchedule.user_id == user_id)
        .filter(
            or_(
                models.MedicationSchedule.end_date >= date.today(),
                models.MedicationSchedule.end_date.is_(None),
            ),
        ),
    )

    schedules = result.scalars().all()
    return {"schedules": schedules}
