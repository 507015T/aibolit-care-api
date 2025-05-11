from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, PositiveInt, ConfigDict


class MedicationScheduleBase(BaseModel):
    medication_name: str = Field(max_length=255)
    frequency: PositiveInt = Field(lt=16, examples=[7])
    duration_days: Optional[PositiveInt] = Field(
        None, description="Duration in days, must be > 0, if set", examples=[7]
    )
    start_date: Optional[date] = Field(None, description="today date by default", examples=["2025-12-31"])
    user_id: PositiveInt


class MedicationScheduleCreateResponse(BaseModel):
    schedule_id: PositiveInt


class MedicationScheduleIdsResponse(BaseModel):
    user_id: PositiveInt
    schedules: List[PositiveInt]


class MedicationScheduleCreateRequest(MedicationScheduleBase): ...


class MedicationSchedule(MedicationScheduleBase):
    id: PositiveInt
    end_date: Optional[date] = Field(
        None,
        examples=["2026-01-06"],
        description="Read Only!",
        json_schema_extra={"readOnly": True},
    )
    daily_plan: List[str] = Field(
        ...,
        description="Each reception time is a multiple of 15(Read Only)!",
        examples=[["08:00", "10:30", "12:45", "15:00", "17:30", "19:45", "22:00"]],
        title="Daily Plan",
        json_schema_extra={"readOnly": True},
    )

    # sql alchemy support
    model_config = ConfigDict(from_attributes=True)


class NextTakingsMedications(BaseModel):
    schedule_id: PositiveInt
    schedule_name: str
    schedule_times: List[str] = Field(..., json_schema_extra={"readOnly": True})


class NextTakingsMedicationsResponse(BaseModel):
    user_id: PositiveInt
    next_takings: List[NextTakingsMedications]
