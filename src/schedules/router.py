from fastapi import APIRouter, Depends
import database
from schedules import service, schemas
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/schedule")
async def create_schedule(
    schedule: schemas.MedicationScheduleCreate,
    db: AsyncSession = Depends(database.get_db),
):
    return await service.create_schedule(schedule, db)


@router.get("/schedules")
async def get_all_schedules(user_id: int, db: AsyncSession = Depends(database.get_db)):
    return await service.get_schedules(user_id, db)
