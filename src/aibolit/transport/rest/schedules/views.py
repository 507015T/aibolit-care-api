from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated


# from aibolit.schedules import utils, service

# from openapi.generated.schemas.medication_schedule import (
from aibolit.services.users_service import UserService
from aibolit.transport.rest.schedules.schemas import (
    MedicationScheduleCreateResponse,
    MedicationScheduleCreateRequest,
    MedicationScheduleIdsResponse,
    MedicationSchedule,
    NextTakingsMedicationsResponse,
)
from aibolit.services.schedules_service import ScheduleExpiredError, ScheduleService

router = APIRouter()


# TODO: переместить все в services(это бизнес логика )
@router.post("/schedule", status_code=201, response_model=MedicationScheduleCreateResponse)
async def create_schedule(
    schedule: MedicationScheduleCreateRequest,
    schedules_service: Annotated[ScheduleService, Depends(ScheduleService)],
    users_service: Annotated[UserService, Depends(UserService)],
) -> MedicationScheduleCreateResponse:
    user_exists = await users_service.get_user_by_id(schedule.user_id)
    if not user_exists:
        raise HTTPException(status_code=404, detail=f"User with id={schedule.user_id} not found")
    schedule = await schedules_service.create_schedule(schedule)
    return schedule


@router.get("/schedules", response_model=MedicationScheduleIdsResponse)
async def get_all_schedules(
    user_id: int,
    schedules_service: Annotated[ScheduleService, Depends(ScheduleService)],
) -> MedicationScheduleIdsResponse:
    return await schedules_service.get_all_user_schedules(user_id)


@router.get("/schedule", response_model=MedicationSchedule)
async def get_user_schedule(
    schedule_id: int,
    user_id: int,
    schedules_service: Annotated[ScheduleService, Depends(ScheduleService)],
) -> MedicationSchedule:
    try:
        user_schedule = await schedules_service.get_user_schedule(user_id=user_id, schedule_id=schedule_id)
        return user_schedule
    except ScheduleExpiredError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/next_takings", response_model=NextTakingsMedicationsResponse)
async def get_user_next_takings(
    user_id: int,
    schedules_service: Annotated[ScheduleService, Depends(ScheduleService)],
) -> NextTakingsMedicationsResponse:
    return await schedules_service.get_user_next_takings(user_id)
