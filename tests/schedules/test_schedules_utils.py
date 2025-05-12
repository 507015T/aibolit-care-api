from datetime import datetime
from freezegun import freeze_time
import pytest
from aibolit.services.schedules.service import ScheduleService


@pytest.mark.parametrize(
    "frequency, expected_result",
    [
        (1, ["08:00"]),
        (2, ["08:00", "22:00"]),
        (3, ["08:00", "15:00", "22:00"]),
        (4, ["08:00", "12:45", "17:30", "22:00"]),
        (5, ["08:00", "11:30", "15:00", "18:30", "22:00"]),
        (6, ["08:00", "11:00", "13:45", "16:30", "19:15", "22:00"]),
        (7, ["08:00", "10:30", "12:45", "15:00", "17:30", "19:45", "22:00"]),
        (8, ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00"]),
        (9, ["08:00", "09:45", "11:30", "13:15", "15:00", "16:45", "18:30", "20:15", "22:00"]),
        (10, ["08:00", "09:45", "11:15", "12:45", "14:15", "16:00", "17:30", "19:00", "20:30", "22:00"]),
        (11, ["08:00", "09:30", "11:00", "12:15", "13:45", "15:00", "16:30", "18:00", "19:15", "20:45", "22:00"]),
        (
            12,
            [
                "08:00",
                "09:30",
                "10:45",
                "12:00",
                "13:15",
                "14:30",
                "15:45",
                "17:00",
                "18:15",
                "19:30",
                "20:45",
                "22:00",
            ],
        ),
        (
            13,
            [
                "08:00",
                "09:15",
                "10:30",
                "11:30",
                "12:45",
                "14:00",
                "15:00",
                "16:15",
                "17:30",
                "18:30",
                "19:45",
                "21:00",
                "22:00",
            ],
        ),
        (
            14,
            [
                "08:00",
                "09:15",
                "10:15",
                "11:15",
                "12:30",
                "13:30",
                "14:30",
                "15:45",
                "16:45",
                "17:45",
                "19:00",
                "20:00",
                "21:00",
                "22:00",
            ],
        ),
        (
            15,
            [
                "08:00",
                "09:00",
                "10:00",
                "11:00",
                "12:00",
                "13:00",
                "14:00",
                "15:00",
                "16:00",
                "17:00",
                "18:00",
                "19:00",
                "20:00",
                "21:00",
                "22:00",
            ],
        ),
    ],
)
def test_generate_daily_plan(frequency, expected_result):
    service = ScheduleService(schedules_repo=None)
    result = service._generate_daily_plan(frequency)
    assert expected_result == result


@pytest.mark.parametrize(
    "input_dt, expected_dt",
    [
        (datetime(2025, 5, 12, 8, 0), datetime(2025, 5, 12, 8, 0)),
        (datetime(2025, 5, 12, 8, 1), datetime(2025, 5, 12, 8, 15)),
        (datetime(2025, 5, 12, 8, 7), datetime(2025, 5, 12, 8, 15)),
        (datetime(2025, 5, 12, 8, 14), datetime(2025, 5, 12, 8, 15)),
        (datetime(2025, 5, 12, 8, 15), datetime(2025, 5, 12, 8, 15)),
        (datetime(2025, 5, 12, 8, 16), datetime(2025, 5, 12, 8, 30)),
        (datetime(2025, 5, 12, 8, 29), datetime(2025, 5, 12, 8, 30)),
        (datetime(2025, 5, 12, 8, 30), datetime(2025, 5, 12, 8, 30)),
        (datetime(2025, 5, 12, 8, 31), datetime(2025, 5, 12, 8, 45)),
        (datetime(2025, 5, 12, 8, 44), datetime(2025, 5, 12, 8, 45)),
        (datetime(2025, 5, 12, 8, 45), datetime(2025, 5, 12, 8, 45)),
        (datetime(2025, 5, 12, 8, 46), datetime(2025, 5, 12, 9, 0)),
        (datetime(2025, 5, 12, 8, 59), datetime(2025, 5, 12, 9, 0)),
        (datetime(2025, 5, 12, 9, 0), datetime(2025, 5, 12, 9, 0)),
        (datetime(2025, 5, 12, 9, 1), datetime(2025, 5, 12, 9, 15)),
        (datetime(2025, 5, 12, 9, 14), datetime(2025, 5, 12, 9, 15)),
        (datetime(2025, 5, 12, 9, 45), datetime(2025, 5, 12, 9, 45)),
        (datetime(2025, 5, 12, 10, 59), datetime(2025, 5, 12, 11, 0)),
        (datetime(2025, 5, 12, 21, 59), datetime(2025, 5, 12, 22, 0)),
        (datetime(2025, 5, 12, 22, 0), datetime(2025, 5, 12, 22, 0)),
        (datetime(2025, 5, 12, 22, 1), datetime(2025, 5, 12, 22, 15)),
    ],
)
def test_round_to_next_interval(input_dt: datetime, expected_dt: datetime):
    assert ScheduleService._round_to_next_interval(input_dt) == expected_dt


@pytest.mark.parametrize(
    "now_time, dose_time, expected",
    [
        ("08:00", "08:15", True),
        ("08:30", "08:15", True),
        ("08:50", "08:15", False),
        ("07:00", "07:30", False),
        ("07:00", "07:59", False),
        ("22:30", "22:15", False),
        ("07:59", "08:00", True),
        ("21:59", "22:00", True),
        ("22:30", "22:00", True),
        ("22:01", "22:00", True),
        ("22:31", "22:00", False),
        ("23:00", "22:30", False),
        ("00:30", "22:00", False),
        ("22:00", "23:30", False),
        ("21:30", "22:30", False),
    ],
)
def test_is_within_timeframe(now_time: str, dose_time: str, expected: bool):
    frozen_dt = datetime.strptime(f"2025-05-12 {now_time}", "%Y-%m-%d %H:%M")
    with freeze_time(frozen_dt):
        assert ScheduleService._is_within_timeframe(dose_time) == expected
