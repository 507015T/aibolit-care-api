from datetime import date
from typing import List, Optional
from pydantic import BaseModel, computed_field, field_validator, ConfigDict
from schedules import utils


class MedicationScheduleBase(BaseModel):
    medication_name: str
    frequency: int
    duration_days: Optional[int] = None
    start_date: Optional[date] = date.today()
    user_id: int


class MedicationScheduleCreateResponse(BaseModel):
    schedule_id: int


class MedicationScheduleIdsResponse(BaseModel):
    user_id: int
    schedules: List[int]


class MedicationScheduleCreate(MedicationScheduleBase):
    @field_validator("frequency")
    def check_frequency(cls, value):
        if not 1 <= value <= 15:
            raise ValueError("frequency must be between 1 and 15 (inclusive)")
        return value

    @field_validator("duration_days")
    def check_duration_days(cls, value):
        if value is not None and value <= 0:
            raise ValueError("duration_days must be greater than 0 or None")
        return value


class MedicationSchedule(MedicationScheduleBase):
    id: int
    end_date: Optional[date] = None

    @computed_field(return_type=List[str])
    @property
    def daily_plan(self):
        return utils.generate_daily_plan(self.frequency)

    # sql alchemy support
    model_config = ConfigDict(from_attributes=True)


class NextTakingsMedications(BaseModel):
    schedule_id: int
    schedule_name: str
    schedule_times: List[str]

    @field_validator("schedule_times")
    def check_schedule_times(cls, value):
        return list(filter(utils.is_within_timeframe, value))
