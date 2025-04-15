from datetime import date
from pydantic import BaseModel


class MedicationScheduleBase(BaseModel):
    medication_name: str
    frequency: int
    user_id: int
    duration_days: int | None


class MedicationScheduleCreate(MedicationScheduleBase):
    pass


class MedicationSchedule(MedicationScheduleBase):
    id: int
    start_date: date
    end_date: date

    class Config:
        from_attributes = True
