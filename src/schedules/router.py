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
    return await service.get_schedules(user_id, db)
