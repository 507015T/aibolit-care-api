import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from schedules import models, schemas
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
    end_date = schemas.MedicationSchedule.model_validate(created_schedule).model_dump(mode="json")["end_date"]
    correct_end_date = (date.today() + timedelta(days=5)).isoformat()
    assert correct_end_date == end_date


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
    end_date = schemas.MedicationSchedule.model_validate(created_schedule).model_dump(mode="json")["end_date"]
    assert None is end_date


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
    created_schedule = schedules_table.scalars().first()
    duration_days = schemas.MedicationSchedule.model_validate(created_schedule).model_dump(mode="json")["duration_days"]
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
async def test_get_schedules(async_client, get_testing_db: AsyncSession):
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
    response = await async_client.get("/schedules", params={"user_id": 1})
    assert 200 == response.status_code
    filtered_schedules = await get_testing_db.execute(
        select(models.MedicationScheduleOrm).filter(models.MedicationScheduleOrm.user_id == 1)
    )
    user1_schedules = filtered_schedules.scalars().all()
    expected_data = {
        "user_id": 1,
        "schedules": [schemas.MedicationSchedule.model_validate(obj).id for obj in user1_schedules],
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_user_schedules(async_client, get_testing_db: AsyncSession):
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
        "schedules": [schemas.MedicationSchedule.model_validate(obj).id for obj in user2_schedules],
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
    expected_data = {'detail': "The medication 'Фенибут' intake ended on 2023-06-04"}
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
        'detail': [{'input': None, 'loc': ['query', 'user_id'], 'msg': 'Field required', 'type': 'missing'}]
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
        'detail': [{'input': None, 'loc': ['query', 'schedule_id'], 'msg': 'Field required', 'type': 'missing'}]
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
        'detail': [
            {'input': None, 'loc': ['query', 'schedule_id'], 'msg': 'Field required', 'type': 'missing'},
            {'input': None, 'loc': ['query', 'user_id'], 'msg': 'Field required', 'type': 'missing'},
        ]
    }
    assert expected_data == response.json()


@freeze_time("2025-01-01 7:59:59")
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
    print(expected_data, response.json(), sep="\n")
    assert expected_data == response.json()
