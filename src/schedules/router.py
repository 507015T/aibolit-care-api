from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

import database
from schedules import schemas, service, utils

router = APIRouter()


@router.post("/schedule", status_code=201, response_model=schemas.MedicationScheduleCreateResponse)
async def create_schedule(
    schedule: schemas.MedicationScheduleCreate,
    db: Annotated[AsyncSession, Depends(database.get_db)],
) -> schemas.MedicationScheduleCreateResponse:
    db_schedule = await service.create_schedule(schedule, db)
    return schemas.MedicationScheduleCreateResponse(schedule_id=db_schedule.id)


@router.get("/schedules", response_model=schemas.MedicationScheduleIdsResponse)
async def get_all_schedules(
    user_id: int, db: Annotated[AsyncSession, Depends(database.get_db)]
) -> schemas.MedicationScheduleIdsResponse:
    db_schedules = await service.get_schedules(user_id, db)
    schedules = [schemas.MedicationSchedule.model_validate(schedule).id for schedule in db_schedules]
    return schemas.MedicationScheduleIdsResponse(user_id=user_id, schedules=schedules)


@router.get("/schedule", response_model=schemas.MedicationSchedule)
async def get_user_schedule(
    schedule_id: int, user_id: int, db: Annotated[AsyncSession, Depends(database.get_db)]
) -> schemas.MedicationSchedule:
    db_schedule = await service.get_user_schedule(schedule_id, user_id, db)
    schedule = schemas.MedicationSchedule.model_validate(db_schedule)
    return schedule


@router.get("/next_takings", response_model=schemas.NextTakingsMedicationsResponse)
async def get_user_next_takings(
    user_id: int, db: Annotated[AsyncSession, Depends(database.get_db)]
) -> schemas.NextTakingsMedicationsResponse:
    db_schedules = await service.get_schedules(user_id, db)
    schedules = [schemas.MedicationSchedule.model_validate(schedule) for schedule in db_schedules]
    next_takings = [
        schemas.NextTakingsMedications(
            schedule_id=next_taking.id, schedule_name=next_taking.medication_name, schedule_times=next_taking.daily_plan
        )
        for next_taking in schedules
        if any(map(utils.is_within_timeframe, next_taking.daily_plan))
    ]
    return schemas.NextTakingsMedicationsResponse(user_id=user_id, next_takings=next_takings)
