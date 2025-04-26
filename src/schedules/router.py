from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

import database
from schedules import schemas, service

router = APIRouter()


@router.post("/schedule", status_code=201)
async def create_schedule(
    schedule: schemas.MedicationScheduleCreate,
    db: Annotated[AsyncSession, Depends(database.get_db)],
) -> dict[str, int]:
    db_schedule = await service.create_schedule(schedule, db)
    return {"schedule_id": db_schedule.id}


@router.get("/schedules")
async def get_all_schedules(user_id: int, db: Annotated[AsyncSession, Depends(database.get_db)]):
    db_schedules = await service.get_schedules(user_id, db)
    schedules = [schemas.MedicationSchedule.model_validate(schedule).id for schedule in db_schedules]
    return {"user_id": user_id, "schedules": schedules}


@router.get("/schedule")
async def get_user_schedule(schedule_id: int, user_id: int, db: Annotated[AsyncSession, Depends(database.get_db)]):
    db_schedule = await service.get_user_schedule(schedule_id, user_id, db)
    return db_schedule
