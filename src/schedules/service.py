from schedules import models
from sqlalchemy import select
from datetime import date


async def create_schedule(schedule, db):
    db_schedule = models.MedicationSchedule(**schedule.model_dump())
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule


async def get_schedules(user_id, db):

    result = await db.execute(
        select(models.MedicationSchedule)
        .where(models.MedicationSchedule.user_id == user_id)
    )

    schedules = result.scalars().all()
    return {"schedules": schedules}
