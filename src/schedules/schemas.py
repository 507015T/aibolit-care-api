from datetime import date, datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field, PositiveInt, computed_field, field_validator, ConfigDict
from schedules import utils


class MedicationScheduleBase(BaseModel):
    medication_name: str
    frequency: PositiveInt = Field(lt=16, examples=[7])
    duration_days: Optional[PositiveInt] = Field(
        None, description="Duration in days, must be > 0, if set", examples=[7]
    )
    start_date: Optional[date] = Field(default_factory=date.today)
    user_id: PositiveInt


class MedicationScheduleCreateResponse(BaseModel):
    schedule_id: PositiveInt


class MedicationScheduleIdsResponse(BaseModel):
    user_id: PositiveInt
    schedules: List[PositiveInt]


class MedicationScheduleCreate(MedicationScheduleBase): ...


class MedicationSchedule(MedicationScheduleBase):
    id: PositiveInt
    end_date: Optional[date] = Field(
        None, examples=[(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")], json_schema_extra={"readOnly": True}
    )

    @computed_field(
        return_type=List[str],
        description="Each reception time is a multiple of 15!",
        examples=[['08:00', '10:30', '12:45', '15:00', '17:30', '19:45', '22:00']],
        json_schema_extra={"readOnly": True},
    )
    def daily_plan(self):
        return utils.generate_daily_plan(self.frequency)

    # sql alchemy support
    model_config = ConfigDict(from_attributes=True)


class NextTakingsMedications(BaseModel):
    schedule_id: PositiveInt
    schedule_name: str
    schedule_times: List[str] = Field(..., json_schema_extra={"readOnly": True})

    @field_validator("schedule_times")
    def check_schedule_times(cls, value):
        return list(filter(utils.is_within_timeframe, value))


class NextTakingsMedicationsResponse(BaseModel):
    user_id: PositiveInt
    next_takings: List[NextTakingsMedications]
