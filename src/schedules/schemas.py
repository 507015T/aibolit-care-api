from datetime import date
from pydantic import BaseModel, field_validator, ConfigDict


class MedicationScheduleBase(BaseModel):
    medication_name: str
    frequency: int
    user_id: int
    duration_days: int | None = None


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
    start_date: date

    # sql alchemy support
    model_config = ConfigDict(from_attributes=True)
