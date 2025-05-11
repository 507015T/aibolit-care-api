import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from aibolit.models.schedules import models
from sqlalchemy import select
from datetime import date, datetime, timedelta
from freezegun import freeze_time


@pytest.mark.asyncio
async def test_post_schedule(async_client, get_testing_db: AsyncSession):
    user = await async_client.post("/users", json={})
    assert 201 == user.status_code
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Финастерид",
            "frequency": 1,
            "duration_days": 5,
            "user_id": 1,
        },
    )
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()

    schedules_table = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    created_schedule = schedules_table.scalars().first()
    assert "Финастерид" == created_schedule.medication_name
    end_date = created_schedule.end_date.isoformat()
    expected_end_date = (date.today() + timedelta(days=5)).isoformat()
    assert expected_end_date == end_date


@pytest.mark.asyncio
async def test_post_schedule_with_wrong_frequency(async_client):
    await async_client.post("/users", json={})
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Финастерид",
            "frequency": 16,
            "duration_days": 730,
            "user_id": 1,
        },
    )
    assert 422 == response.status_code
    expected_data = {
        "detail": [
            {
                "type": "less_than",
                "loc": ["body", "frequency"],
                "msg": "Input should be less than 16",
                "input": 16,
                "ctx": {"lt": 16},
            }
        ]
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_post_schedule_without_duration_days(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Фенибут",
            "frequency": 10,
            "user_id": 1,
        },
    )
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()

    schedules_table = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    created_schedule = schedules_table.scalars().first()
    assert None is created_schedule.end_date


@pytest.mark.asyncio
async def test_post_schedule_with_wrong_duration_days(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Фенибут",
            "frequency": 10,
            "user_id": 1,
            "duration_days": 0,
        },
    )
    assert 422 == response.status_code
    expected_data = {
        "detail": [
            {
                "type": "greater_than",
                "loc": ["body", "duration_days"],
                "msg": "Input should be greater than 0",
                "input": 0,
                "ctx": {"gt": 0},
            }
        ]
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_post_schedule_with_negative_duration_days(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Фенибут",
            "frequency": 10,
            "user_id": 1,
            "duration_days": -13,
        },
    )
    assert 422 == response.status_code
    expected_data = {
        "detail": [
            {
                "type": "greater_than",
                "loc": ["body", "duration_days"],
                "msg": "Input should be greater than 0",
                "input": -13,
                "ctx": {"gt": 0},
            }
        ]
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_post_schedule_with_none_duration_days(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Фенибут",
            "frequency": 10,
            "user_id": 1,
            "duration_days": None,
        },
    )
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()

    schedules_table = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    duration_days = schedules_table.scalars().first().duration_days
    assert None is duration_days


@pytest.mark.asyncio
async def test_post_schedule_without_user_id(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    data = {
        "medication_name": "Фурацелин",
        "frequency": 15,
        "duration_days": 4,
    }
    response = await async_client.post("/schedule", json=data)
    assert 422 == response.status_code
    expected_data = {
        "detail": [
            {
                "input": {
                    "duration_days": 4,
                    "frequency": 15,
                    "medication_name": "Фурацелин",
                },
                "loc": ["body", "user_id"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_post_schedule_without_required_fields(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    data = {"duration_days": 1, "start_date": "2025-08-23"}
    response = await async_client.post("/schedule", json=data)
    assert 422 == response.status_code
    expected_data = {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "medication_name"],
                "msg": "Field required",
                "input": {"duration_days": 1, "start_date": "2025-08-23"},
            },
            {
                "type": "missing",
                "loc": ["body", "frequency"],
                "msg": "Field required",
                "input": {"duration_days": 1, "start_date": "2025-08-23"},
            },
            {
                "type": "missing",
                "loc": ["body", "user_id"],
                "msg": "Field required",
                "input": {"duration_days": 1, "start_date": "2025-08-23"},
            },
        ]
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_user_schedules_1(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Финастерид",
            "frequency": 1,
            "duration_days": 5,
            "user_id": 1,
        },
    )
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Миноксидил",
            "frequency": 2,
            "user_id": 1,
        },
    )
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Тренболон",
            "frequency": 3,
            "user_id": 2,
        },
    )
    response = await async_client.get("/schedules", params={"user_id": 2})
    filtered_schedules = await get_testing_db.execute(
        select(models.MedicationScheduleOrm).filter(models.MedicationScheduleOrm.user_id == 2)
    )
    user2_schedules = filtered_schedules.scalars().all()
    expected_data = {
        "user_id": 2,
        "schedules": [obj.id for obj in user2_schedules],
    }
    assert 200 == response.status_code
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_user_schedules_2(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Тренболон",
            "frequency": 3,
            "user_id": 2,
        },
    )
    response = await async_client.get("/schedules", params={"user_id": 1})
    assert 200 == response.status_code
    expected_data = {"user_id": 1, "schedules": []}
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_expired_user_schedules(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Тренболон",
            "frequency": 3,
            "user_id": 1,
            "start_date": "2000-05-04",
            "duration_days": 30,
        },
    )
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "ТренболонV0.0.0.0.0.1",
            "frequency": 100,
            "user_id": 1,
            "start_date": "1000-05-04",
            "duration_days": 1,
        },
    )
    response = await async_client.get("/schedules", params={"user_id": 1})
    assert 200 == response.status_code
    expected_data = {"schedules": [], "user_id": 1}
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_expired_schedule_for_user(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Фенибут",
            "frequency": 3,
            "user_id": 1,
            "start_date": "2023-05-04",
            "duration_days": 31,
        },
    )
    response = await async_client.get("/schedule", params={"schedule_id": 1, "user_id": 1})
    assert 404 == response.status_code
    expected_data = {"detail": "The medication 'Фенибут' intake ended on 2023-06-04"}
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_daily_plan(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Вайбкодинг",
            "frequency": 3,
            "user_id": 1,
        },
    )
    response = await async_client.get("/schedule", params={"schedule_id": 1, "user_id": 1})
    assert 200 == response.status_code
    expected_data = {
        "id": 1,
        "medication_name": "Вайбкодинг",
        "frequency": 3,
        "user_id": 1,
        "daily_plan": ["08:00", "15:00", "22:00"],
        "duration_days": None,
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": None,
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_daily_plan_without_user_id(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Вайбкодинг",
            "frequency": 3,
            "user_id": 1,
        },
    )
    response = await async_client.get("/schedule", params={"schedule_id": 1})
    assert 422 == response.status_code
    expected_data = {
        "detail": [{"input": None, "loc": ["query", "user_id"], "msg": "Field required", "type": "missing"}]
    }

    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_daily_plan_without_schedule_id(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Вайбкодинг",
            "frequency": 3,
            "user_id": 1,
        },
    )
    response = await async_client.get("/schedule", params={"user_id": 1})
    assert 422 == response.status_code
    expected_data = {
        "detail": [{"input": None, "loc": ["query", "schedule_id"], "msg": "Field required", "type": "missing"}]
    }

    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_daily_plan_without_params(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Вайбкодинг",
            "frequency": 3,
            "user_id": 1,
        },
    )
    response = await async_client.get("/schedule")
    assert 422 == response.status_code
    expected_data = {
        "detail": [
            {"input": None, "loc": ["query", "schedule_id"], "msg": "Field required", "type": "missing"},
            {"input": None, "loc": ["query", "user_id"], "msg": "Field required", "type": "missing"},
        ]
    }
    assert expected_data == response.json()


@freeze_time("2025-01-01 7:00")
@pytest.mark.asyncio
async def test_get_next_takings(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Вайбкодинг",
            "frequency": 3,
            "user_id": 1,
        },
    )
    await async_client.post(
        "/schedule",
        json={"medication_name": "Кокаколаколастик", "frequency": 7, "user_id": 1, "duration_days": 8},
    )
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "NZT",
            "frequency": 15,
            "user_id": 1,
        },
    )
    response = await async_client.get("/next_takings", params={"user_id": 1})

    expected_data = {
        "user_id": 1,
        "next_takings": [
            {
                "schedule_id": 1,
                "schedule_name": "Вайбкодинг",
                "schedule_times": ["08:00"],
            },
            {
                "schedule_id": 2,
                "schedule_name": "Кокаколаколастик",
                "schedule_times": ["08:00"],
            },
            {
                "schedule_id": 3,
                "schedule_name": "NZT",
                "schedule_times": ["08:00", "09:00"],
            },
        ],
    }

    assert 200 == response.status_code
    assert expected_data == response.json()


@freeze_time("2025-01-01 7:59:59")
@pytest.mark.asyncio
async def test_get_next_takings_one_minute_before_first_intake(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Вайбкодинг",
            "frequency": 15,
            "user_id": 1,
        },
    )

    response = await async_client.get("/next_takings", params={"user_id": 1})
    expected_data = {
        "user_id": 1,
        "next_takings": [
            {
                "schedule_id": 1,
                "schedule_name": "Вайбкодинг",
                "schedule_times": ["08:00", "09:00"],
            }
        ],
    }
    assert expected_data == response.json()


@freeze_time("2025-01-01 8:01:00")
@pytest.mark.asyncio
async def test_get_next_takings_one_minute_after_first_intake(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Вайбкодинг",
            "frequency": 15,
            "user_id": 1,
        },
    )

    response = await async_client.get("/next_takings", params={"user_id": 1})
    expected_data = {
        "user_id": 1,
        "next_takings": [
            {
                "schedule_id": 1,
                "schedule_name": "Вайбкодинг",
                "schedule_times": ["08:00", "09:00", "10:00"],
            }
        ],
    }
    assert expected_data == response.json()


@freeze_time("2025-01-01 8:30:01")
@pytest.mark.asyncio
async def test_get_next_takings_30_min_after_intake_hides_it(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Вайбкодинг",
            "frequency": 15,
            "user_id": 1,
        },
    )

    response = await async_client.get("/next_takings", params={"user_id": 1})

    expected_data = {
        "user_id": 1,
        "next_takings": [
            {
                "schedule_id": 1,
                "schedule_name": "Вайбкодинг",
                "schedule_times": ["09:00", "10:00"],
            }
        ],
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_next_takings_with_expired_schedule(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    await async_client.post(
        "/schedule",
        json={
            "medication_name": "Вайбкодинг",
            "frequency": 3,
            "user_id": 1,
            "start_date": "2000-01-01",
            "duration_days": 2,
        },
    )
    response = await async_client.get("/next_takings", params={"user_id": 1})

    expected_data = {
        "user_id": 1,
        "next_takings": [],
    }

    assert 200 == response.status_code
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_non_existent_schedule_for_user(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.get("/schedule", params={"user_id": 1, "schedule_id": 1})
    assert 404 == response.status_code
    expected_data = {"detail": "The medication schedule with id=1 for user=1 not found"}

    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_non_existent_user_for_schedule(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    created_schedule = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Финастерид",
            "frequency": 1,
            "duration_days": 5,
            "user_id": 1,
        },
    )
    assert 201 == created_schedule.status_code
    response = await async_client.get("/schedule", params={"user_id": 2, "schedule_id": 1})
    assert 404 == response.status_code
    expected_data = {"detail": "The medication schedule with id=1 for user=2 not found"}

    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_non_existent_user_and_schedule(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    created_schedule = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Финастерид",
            "frequency": 1,
            "duration_days": 5,
            "user_id": 1,
        },
    )
    assert 201 == created_schedule.status_code
    response = await async_client.get("/schedule", params={"user_id": 66, "schedule_id": 66})
    assert 404 == response.status_code
    expected_data = {"detail": "The medication schedule with id=66 for user=66 not found"}

    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_non_existent_schedules_for_user(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.get("/schedules", params={"user_id": 2})
    assert 200 == response.status_code

    assert {"schedules": [], "user_id": 2} == response.json()


@pytest.mark.asyncio
async def test_get_non_existent_next_takings_for_user(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.get("/next_takings", params={"user_id": 1})
    assert 200 == response.status_code
    assert {"next_takings": [], "user_id": 1} == response.json()


@pytest.mark.asyncio
async def test_get_next_takings_for_user_id_not_int(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.get("/next_takings", params={"user_id": "abc"})
    assert 422 == response.status_code
    expected_data = {
        "detail": [
            {
                "type": "int_parsing",
                "loc": ["query", "user_id"],
                "msg": "Input should be a valid integer, unable to parse string as an integer",
                "input": "abc",
            }
        ]
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_user_schedules_with_user_id_not_int(async_client, get_testing_db: AsyncSession):
    response = await async_client.get("/schedules", params={"user_id": "abc"})
    assert 422 == response.status_code
    expected_data = {
        "detail": [
            {
                "type": "int_parsing",
                "loc": ["query", "user_id"],
                "msg": "Input should be a valid integer, unable to parse string as an integer",
                "input": "abc",
            }
        ]
    }

    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_schedule_with_user_and_schedules_ids_not_int(async_client, get_testing_db: AsyncSession):
    response = await async_client.get("/schedule", params={"user_id": "abc", "schedule_id": "lol"})
    assert 422 == response.status_code
    expected_data = {
        "detail": [
            {
                "type": "int_parsing",
                "loc": ["query", "schedule_id"],
                "msg": "Input should be a valid integer, unable to parse string as an integer",
                "input": "lol",
            },
            {
                "type": "int_parsing",
                "loc": ["query", "user_id"],
                "msg": "Input should be a valid integer, unable to parse string as an integer",
                "input": "abc",
            },
        ]
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_post_schedule_with_start_date(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Финастерид",
            "frequency": 15,
            "duration_days": 4,
            "user_id": 1,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
        },
    )
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()
    schedules_table = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    created_schedule = schedules_table.scalars().first()
    assert (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d") == created_schedule.end_date.strftime("%Y-%m-%d")


@pytest.mark.asyncio
async def test_post_schedule_with_old_start_date(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Финастерид",
            "frequency": 15,
            "duration_days": 4,
            "user_id": 1,
            "start_date": date(year=2000, month=1, day=1).strftime("%Y-%m-%d"),
        },
    )
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()
    schedules_table = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    created_schedule = schedules_table.scalars().first()
    assert "2000-01-05" == created_schedule.end_date.strftime("%Y-%m-%d")


@pytest.mark.asyncio
async def test_post_schedule_with_end_date(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Финастерид",
            "frequency": 15,
            "duration_days": 4,
            "user_id": 1,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": "2025-00-00",
        },
    )
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()
    schedules_table = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    created_schedule = schedules_table.scalars().first()
    assert (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d") == created_schedule.end_date.strftime("%Y-%m-%d")


@pytest.mark.asyncio
async def test_post_schedule_with_daily_plan(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Финастерид",
            "frequency": 4,
            "duration_days": 4,
            "user_id": 1,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "daily_plan": ["8:00", "19:43"],
        },
    )
    assert 201 == response.status_code
    response = await async_client.get("/schedule", params={"user_id": 1, "schedule_id": 1})
    assert ["08:00", "12:45", "17:30", "22:00"] == response.json()["daily_plan"]


@pytest.mark.asyncio
async def test_post_schedule_with_wrong_start_date(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "Финастерид",
            "frequency": 4,
            "duration_days": 4,
            "user_id": 1,
            "start_date": "2000-00-00",
        },
    )
    assert 422 == response.status_code
    expected_data = {
        "detail": [
            {
                "type": "date_from_datetime_parsing",
                "loc": ["body", "start_date"],
                "msg": "Input should be a valid date or datetime, month value is outside expected range of 1-12",
                "input": "2000-00-00",
                "ctx": {"error": "month value is outside expected range of 1-12"},
            }
        ]
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_post_schedule_with_large_med_name(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    response = await async_client.post(
        "/schedule",
        json={
            "medication_name": "л" * 256,
            "frequency": 4,
            "duration_days": 4,
            "user_id": 1,
        },
    )
    assert 422 == response.status_code
    assert "String should have at most 255 characters" == response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_post_schedule_with_special_symbols_in_med_name(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
    med_names = [
        "Аспирин®",
        "Paracetamol™",
        "℞ Ибупрофен",
        "C#-ингибитор",
        "<script>alert('XSS')</script>",
        "薬",
        "😷Antibiotic",
        "œ∑´®†¥¨ˆøπ“‘åß∂ƒ©…æΩ≈ç√∫˜µ≤≥÷",
    ]
    for i in med_names:
        response = await async_client.post(
            "/schedule",
            json={
                "medication_name": i,
                "frequency": 4,
                "duration_days": 4,
                "user_id": 1,
            },
        )
        assert 201 == response.status_code
        schedule_id = response.json()["schedule_id"]
        db_schedule = await get_testing_db.execute(
            select(models.MedicationScheduleOrm).where(models.MedicationScheduleOrm.id == schedule_id)
        )
        db_schedule = db_schedule.scalars().first()
        assert db_schedule.medication_name == i
        get_response = await async_client.get("/schedule", params={"schedule_id": schedule_id, "user_id": 1})
        assert get_response.status_code == 200
        assert get_response.json()["medication_name"] == i
