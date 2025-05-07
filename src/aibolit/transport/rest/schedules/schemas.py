from datetime import date, datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field, PositiveInt, computed_field, field_validator, ConfigDict
from aibolit.config import settings


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


class MedicationScheduleCreateRequest(MedicationScheduleBase): ...


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
        return generate_daily_plan(self.frequency)

    # sql alchemy support
    model_config = ConfigDict(from_attributes=True)


class NextTakingsMedications(BaseModel):
    schedule_id: PositiveInt
    schedule_name: str
    schedule_times: List[str] = Field(..., json_schema_extra={"readOnly": True})

    @field_validator("schedule_times")
    def check_schedule_times(cls, value):
        return list(filter(is_within_timeframe, value))


class NextTakingsMedicationsResponse(BaseModel):
    user_id: PositiveInt
    next_takings: List[NextTakingsMedications]


def generate_daily_plan(frequency) -> List[str]:
    start_day = datetime.strptime("8:00", "%H:%M")
    end_day = datetime.strptime("22:00", "%H:%M")
    if frequency == 1:
        return ["8:00"]
    interval = (end_day - start_day) / (frequency - 1)
    times = []
    for freq in range(frequency):
        estimated_time = start_day + (freq * interval)
        minutes_of_estimated_time = estimated_time.minute
        new_minutes_of_estimated_time = (minutes_of_estimated_time + 14) // 15 * 15
        if new_minutes_of_estimated_time == 60:
            estimated_time = estimated_time.replace(minute=0) + timedelta(hours=1)
        else:
            estimated_time = estimated_time.replace(minute=new_minutes_of_estimated_time)
        times.append(estimated_time.strftime("%H:%M"))

    return times


def is_within_timeframe(time_str):
    current_time = datetime.now()
    time_limit = current_time + timedelta(minutes=settings.NEXT_TAKINGS_PERIOD)
    time_obj = datetime.strptime(time_str, "%H:%M").time()
    return (
        settings.TIME_DAY_START <= time_obj <= settings.TIME_DAY_END
        and current_time.time() < time_obj < time_limit.time()
    )
