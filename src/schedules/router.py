from fastapi import APIRouter, Depends
import database
from schedules import service, schemas
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/schedules")
async def index(
    schedule: schemas.MedicationScheduleCreate,
    db: AsyncSession = Depends(database.get_db),
):
    return await service.create_schedule(schedule, db)


@router.get("/schedules")
async def get_all_schedules(db: AsyncSession = Depends(database.get_db)):
    return await service.get_schedules(db)
