from schedules import models
from sqlalchemy import select


async def create_schedule(schedule, db):
    db_schedule = models.MedicationSchedule(**schedule.model_dump())
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule


async def get_schedules(db):

    result = await db.execute(select(models.MedicationSchedule))
    schedules = result.scalars().all()
    return {"schedules": schedules}
