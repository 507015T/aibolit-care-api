from datetime import datetime, timedelta
from typing import List
from config import settings


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
