from datetime import date, timedelta
from operator import or_

from fastapi import HTTPException
from sqlalchemy import select

from schedules import models, utils


async def create_schedule(schedule, db):
    end_date = schedule.start_date + timedelta(days=schedule.duration_days) if schedule.duration_days else None
    db_schedule = models.MedicationSchedule(end_date=end_date, **schedule.model_dump())
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule


async def get_schedules(user_id, db):

    db_request = await db.execute(
        select(models.MedicationSchedule)
        .filter(models.MedicationSchedule.user_id == user_id)
        .filter(
            or_(
                models.MedicationSchedule.end_date >= date.today(),
                models.MedicationSchedule.end_date.is_(None),
            ),
        ),
    )
    db_schedules = db_request.scalars().all()
    return db_schedules


async def get_user_schedule(schedule_id, user_id, db):
    result = await db.execute(
        select(models.MedicationSchedule)
        .filter(models.MedicationSchedule.id == schedule_id)
        .filter(models.MedicationSchedule.user_id == user_id)
    )
    schedule = result.scalars().first()
    schedule.daily_plan = utils.generate_daily_plan(schedule.frequency)
    if schedule.end_date and schedule.end_date < date.today():
        raise HTTPException(
            status_code=404, detail=f"The medication '{schedule.medication_name}' intake ended on {schedule.end_date}"
        )
    return schedule


async def get_user_next_takings(user_id, db):
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
    return schedules
