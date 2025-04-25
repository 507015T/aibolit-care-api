import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from schedules import models, schemas
from sqlalchemy import select
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_post_schedule(async_client, get_testing_db: AsyncSession):
    await async_client.post("/users", json={})
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

    schedules_table = await get_testing_db.execute(select(models.MedicationSchedule))
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
                "type": "value_error",
                "loc": ["body", "frequency"],
                "msg": "Value error, frequency must be between 1 and 15 (inclusive)",
                "input": 16,
                "ctx": {"error": {}},
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

    schedules_table = await get_testing_db.execute(select(models.MedicationSchedule))
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
                "type": "value_error",
                "loc": ["body", "duration_days"],
                "msg": "Value error, duration_days must be greater than 0 or None",
                "input": 0,
                "ctx": {"error": {}},
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
                "type": "value_error",
                "loc": ["body", "duration_days"],
                "msg": "Value error, duration_days must be greater than 0 or None",
                "input": -13,
                "ctx": {"error": {}},
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

    schedules_table = await get_testing_db.execute(select(models.MedicationSchedule))
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
        select(models.MedicationSchedule).filter(models.MedicationSchedule.user_id == 1)
    )
    user1_schedules = filtered_schedules.scalars().all()
    expected_data = {
        "schedules": [schemas.MedicationSchedule.model_validate(obj).model_dump(mode="json") for obj in user1_schedules]
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
        select(models.MedicationSchedule).filter(models.MedicationSchedule.user_id == 2)
    )
    user2_schedules = filtered_schedules.scalars().all()
    expected_data = {
        "schedules": [schemas.MedicationSchedule.model_validate(obj).model_dump(mode="json") for obj in user2_schedules]
    }
    assert 200 == response.status_code
    assert expected_data == response.json()
    assert "Тренболон" == response.json()["schedules"][0]["medication_name"]


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
    expected_data = {"schedules": []}
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
    response = await async_client.get("/schedules", params={"user_id": 1})
    assert 200 == response.status_code
    expected_data = {"schedules": []}
    assert expected_data == response.json()
