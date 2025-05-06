from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from aibolit.database import get_db
from aibolit.schedules import utils, service

# from openapi.generated.schemas.medication_schedule import (
from aibolit.schedules.schemas import (
    MedicationScheduleCreateResponse,
    MedicationScheduleCreate,
    MedicationScheduleIdsResponse,
    MedicationSchedule,
    NextTakingsMedications,
    NextTakingsMedicationsResponse,
)
from aibolit.users.service import validate_user_exists

router = APIRouter()


@router.post("/schedule", status_code=201, response_model=MedicationScheduleCreateResponse)
async def create_schedule(
    schedule: MedicationScheduleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MedicationScheduleCreateResponse:
    user_exists = await validate_user_exists(schedule.user_id, db)
    if not user_exists:
        raise HTTPException(status_code=404, detail=f"User with id={schedule.user_id} not found")
    db_schedule = await service.create_schedule(schedule, db)
    return MedicationScheduleCreateResponse(schedule_id=db_schedule.id)


@router.get("/schedules", response_model=MedicationScheduleIdsResponse)
async def get_all_schedules(
    user_id: int, db: Annotated[AsyncSession, Depends(get_db)]
) -> MedicationScheduleIdsResponse:
    db_schedules = await service.get_schedules(user_id, db)
    schedules = [MedicationSchedule.model_validate(schedule).id for schedule in db_schedules]
    return MedicationScheduleIdsResponse(user_id=user_id, schedules=schedules)


@router.get("/schedule", response_model=MedicationSchedule)
async def get_user_schedule(
    schedule_id: int, user_id: int, db: Annotated[AsyncSession, Depends(get_db)]
) -> MedicationSchedule:
    db_schedule = await service.get_user_schedule(schedule_id, user_id, db)
    schedule = MedicationSchedule.model_validate(db_schedule)
    return schedule


@router.get("/next_takings", response_model=NextTakingsMedicationsResponse)
async def get_user_next_takings(
    user_id: int, db: Annotated[AsyncSession, Depends(get_db)]
) -> NextTakingsMedicationsResponse:
    db_schedules = await service.get_schedules(user_id, db)
    schedules = [MedicationSchedule.model_validate(schedule) for schedule in db_schedules]
    next_takings = [
        NextTakingsMedications(
            schedule_id=next_taking.id, schedule_name=next_taking.medication_name, schedule_times=next_taking.daily_plan
        )
        for next_taking in schedules
        if any(map(utils.is_within_timeframe, next_taking.daily_plan))
    ]
    return NextTakingsMedicationsResponse(user_id=user_id, next_takings=next_takings)
