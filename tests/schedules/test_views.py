from httpx import AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from aibolit.models import schedules as models
from sqlalchemy import select
from datetime import date, datetime, timedelta


@pytest_asyncio.fixture
async def created_user(async_client: AsyncClient):
    return await async_client.post("/users", json={})


@pytest_asyncio.fixture
async def created_schedule(async_client: AsyncClient, created_user):
    data = {
        "medication_name": "Вайбкодинг",
        "frequency": 8,
        "duration_days": 5,
        "user_id": 1,
    }
    return await async_client.post("/schedule", json=data)


@pytest.mark.asyncio
async def test_post_schedule(async_client: AsyncClient, get_testing_db: AsyncSession, created_user):
    data = {
        "medication_name": "Финастерид",
        "frequency": 1,
        "duration_days": 5,
        "user_id": 1,
    }
    response = await async_client.post("/schedule", json=data)
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()

    db_schedules = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    db_created_schedule = db_schedules.scalars().first()
    assert "Финастерид" == db_created_schedule.medication_name
    end_date = db_created_schedule.end_date.isoformat()
    expected_end_date = (date.today() + timedelta(days=5)).isoformat()
    assert expected_end_date == end_date


@pytest.mark.asyncio
async def test_post_schedule_without_duration_days(
    async_client: AsyncClient, get_testing_db: AsyncSession, created_user
):
    data = {
        "medication_name": "Фенибут",
        "frequency": 10,
        "user_id": 1,
    }
    response = await async_client.post("/schedule", json=data)
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()

    db_schedules = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    db_created_schedule = db_schedules.scalars().first()
    assert None is db_created_schedule.end_date


@pytest.mark.asyncio
async def test_post_schedule_with_wrong_frequency(async_client: AsyncClient, created_user):
    data = {
        "medication_name": "Финастерид",
        "frequency": 16,
        "duration_days": 730,
        "user_id": 1,
    }
    response = await async_client.post("/schedule", json=data)
    assert 422 == response.status_code
    expected_data = "Input should be less than 16"
    assert expected_data == response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_post_schedule_with_wrong_duration_days(async_client: AsyncClient, created_user):
    data = {
        "medication_name": "Фенибут",
        "frequency": 10,
        "user_id": 1,
        "duration_days": 0,
    }
    response = await async_client.post("/schedule", json=data)
    assert 422 == response.status_code
    assert "Input should be greater than 0" == response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_post_schedule_with_negative_duration_days(async_client: AsyncClient, created_user):
    data = {
        "medication_name": "Фенибут",
        "frequency": 10,
        "user_id": 1,
        "duration_days": -13,
    }
    response = await async_client.post("/schedule", json=data)
    assert 422 == response.status_code
    assert "Input should be greater than 0" == response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_post_schedule_with_none_duration_days(
    async_client: AsyncClient, get_testing_db: AsyncSession, created_user
):
    data = {
        "medication_name": "Фенибут",
        "frequency": 10,
        "user_id": 1,
        "duration_days": None,
    }
    response = await async_client.post("/schedule", json=data)
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()

    db_schedules = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    duration_days = db_schedules.scalars().first().duration_days
    assert None is duration_days


@pytest.mark.asyncio
async def test_post_schedule_without_user_id(async_client: AsyncClient, created_user):
    data = {
        "medication_name": "Фурацелин",
        "frequency": 15,
        "duration_days": 4,
    }
    response = await async_client.post("/schedule", json=data)
    assert 422 == response.status_code
    assert ["body", "user_id"] == response.json()["detail"][0]["loc"]
    assert "Field required" == response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_post_schedule_without_required_fields(async_client: AsyncClient, created_user):
    data = {"duration_days": 1, "start_date": "2025-08-23"}
    response = await async_client.post("/schedule", json=data)
    assert 422 == response.status_code
    expected_data = [
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
    assert expected_data == response.json()["detail"]


@pytest.mark.asyncio
async def test_post_schedule_with_start_date(async_client: AsyncClient, get_testing_db: AsyncSession, created_user):
    data = {
        "medication_name": "Финастерид",
        "frequency": 15,
        "duration_days": 4,
        "user_id": 1,
        "start_date": datetime.now().strftime("%Y-%m-%d"),
    }
    response = await async_client.post("/schedule", json=data)
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()
    db_schedules = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    db_created_schedule = db_schedules.scalars().first()
    expected_end_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
    assert expected_end_date == db_created_schedule.end_date.strftime("%Y-%m-%d")


@pytest.mark.asyncio
async def test_post_schedule_with_old_start_date(async_client: AsyncClient, get_testing_db: AsyncSession, created_user):
    data = {
        "medication_name": "Финастерид",
        "frequency": 15,
        "duration_days": 4,
        "user_id": 1,
        "start_date": date(year=2000, month=1, day=1).strftime("%Y-%m-%d"),
    }
    response = await async_client.post("/schedule", json=data)
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()
    db_schedules = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    db_created_schedule = db_schedules.scalars().first()
    assert "2000-01-05" == db_created_schedule.end_date.strftime("%Y-%m-%d")


@pytest.mark.asyncio
async def test_post_schedule_with_read_only_end_date(
    async_client: AsyncClient, get_testing_db: AsyncSession, created_user
):
    data = {
        "medication_name": "Финастерид",
        "frequency": 15,
        "duration_days": 4,
        "user_id": 1,
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": "2025-00-00",
    }
    response = await async_client.post("/schedule", json=data)
    assert 201 == response.status_code
    expected_data = {"schedule_id": 1}
    assert expected_data == response.json()
    db_schedules = await get_testing_db.execute(select(models.MedicationScheduleOrm))
    db_created_schedule = db_schedules.scalars().first()
    assert (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d") == db_created_schedule.end_date.strftime(
        "%Y-%m-%d"
    )


@pytest.mark.asyncio
async def test_post_schedule_with_read_only_daily_plan(async_client: AsyncClient, created_user):
    data = {
        "medication_name": "Финастерид",
        "frequency": 4,
        "user_id": 1,
        "daily_plan": ["8:00", "19:43"],
    }
    response = await async_client.post("/schedule", json=data)
    assert 201 == response.status_code
    response = await async_client.get("/schedule", params={"user_id": 1, "schedule_id": 1})
    assert ["08:00", "12:45", "17:30", "22:00"] == response.json()["daily_plan"]


@pytest.mark.asyncio
async def test_post_schedule_with_wrong_start_date(async_client: AsyncClient, created_user):
    data = {
        "medication_name": "Финастерид",
        "frequency": 4,
        "duration_days": 4,
        "user_id": 1,
        "start_date": "2000-00-00",
    }
    response = await async_client.post("/schedule", json=data)
    assert 422 == response.status_code
    expected_data = [
        {
            "type": "date_from_datetime_parsing",
            "loc": ["body", "start_date"],
            "msg": "Input should be a valid date or datetime, month value is outside expected range of 1-12",
            "input": "2000-00-00",
            "ctx": {"error": "month value is outside expected range of 1-12"},
        }
    ]
    assert expected_data == response.json()["detail"]


@pytest.mark.asyncio
async def test_post_schedule_with_large_med_name(async_client: AsyncClient, created_user):
    data = {
        "medication_name": "л" * 256,
        "frequency": 4,
        "duration_days": 4,
        "user_id": 1,
    }
    response = await async_client.post("/schedule", json=data)
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


@pytest.mark.asyncio
async def test_get_future_schedule(async_client: AsyncClient, created_user):
    data = {
        "medication_name": "Финастерид",
        "frequency": 4,
        "duration_days": 4,
        "user_id": 1,
        "start_date": (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d"),
    }
    await async_client.post("/schedule", json=data)
    response = await async_client.get("/schedule", params={"schedule_id": 1, "user_id": 1})
    assert 409 == response.status_code
    expected_data = {
        "detail": f"The medication 'Финастерид' intake will begin {(datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')}"
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_schedule_with_user_and_schedules_ids_not_int(async_client: AsyncClient):
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
async def test_get_expired_user_schedules(async_client: AsyncClient, created_user):
    data1 = {
        "medication_name": "Тренболон",
        "frequency": 3,
        "user_id": 1,
        "start_date": "2000-05-04",
        "duration_days": 30,
    }
    data2 = {
        "medication_name": "ТренболонV0.0.0.0.0.1",
        "frequency": 100,
        "user_id": 1,
        "start_date": "1000-05-04",
        "duration_days": 1,
    }
    await async_client.post("/schedule", json=data1)
    await async_client.post("/schedule", json=data2)
    response = await async_client.get("/schedules", params={"user_id": 1})
    assert 200 == response.status_code
    expected_data = {"schedules": [], "user_id": 1}
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_expired_one_schedule_for_user(async_client: AsyncClient, created_user):
    data = {
        "medication_name": "Фенибут",
        "frequency": 3,
        "user_id": 1,
        "start_date": "2023-05-04",
        "duration_days": 31,
    }
    await async_client.post("/schedule", json=data)
    response = await async_client.get("/schedule", params={"schedule_id": 1, "user_id": 1})
    assert 410 == response.status_code
    expected_data = {"detail": "The medication 'Фенибут' intake ended on 2023-06-04"}
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_non_existent_schedule_for_user(async_client: AsyncClient, created_user):
    response = await async_client.get("/schedule", params={"user_id": 1, "schedule_id": 1})
    assert 404 == response.status_code
    expected_data = {"detail": "The medication schedule with id=1 for user=1 not found"}
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_non_existent_user_for_schedule(async_client: AsyncClient, created_schedule):
    response = await async_client.get("/schedule", params={"user_id": 2, "schedule_id": 1})
    assert 404 == response.status_code
    expected_data = {"detail": "The medication schedule with id=1 for user=2 not found"}
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_non_existent_user_and_schedule(async_client: AsyncClient, created_schedule):
    response = await async_client.get("/schedule", params={"user_id": 66, "schedule_id": 66})
    assert 404 == response.status_code
    expected_data = {"detail": "The medication schedule with id=66 for user=66 not found"}
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_daily_plan(async_client: AsyncClient, created_schedule):
    response = await async_client.get("/schedule", params={"schedule_id": 1, "user_id": 1})
    assert 200 == response.status_code
    expected_data = {
        "id": 1,
        "medication_name": "Вайбкодинг",
        "frequency": 8,
        "user_id": 1,
        "daily_plan": ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00"],
        "duration_days": 5,
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_daily_plan_without_user_id(async_client: AsyncClient, created_schedule):
    response = await async_client.get("/schedule", params={"schedule_id": 1})
    assert 422 == response.status_code
    expected_data = {
        "detail": [{"input": None, "loc": ["query", "user_id"], "msg": "Field required", "type": "missing"}]
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_daily_plan_without_schedule_id(async_client: AsyncClient, created_schedule):
    response = await async_client.get("/schedule", params={"user_id": 1})
    assert 422 == response.status_code
    expected_data = {
        "detail": [{"input": None, "loc": ["query", "schedule_id"], "msg": "Field required", "type": "missing"}]
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_daily_plan_without_params(async_client: AsyncClient, created_schedule):
    response = await async_client.get("/schedule")
    assert 422 == response.status_code
    expected_data = {
        "detail": [
            {"input": None, "loc": ["query", "schedule_id"], "msg": "Field required", "type": "missing"},
            {"input": None, "loc": ["query", "user_id"], "msg": "Field required", "type": "missing"},
        ]
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_user_schedules(async_client: AsyncClient, created_user):
    await async_client.post("/users", json={})
    data_user2 = {
        "medication_name": "Тренболон",
        "frequency": 3,
        "user_id": 2,
    }
    user2_schedule_id = (await async_client.post("/schedule", json=data_user2)).json()["schedule_id"]
    response = await async_client.get("/schedules", params={"user_id": 2})
    expected_data = {
        "user_id": 2,
        "schedules": [user2_schedule_id],
    }
    assert 200 == response.status_code
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_future_all_schedules(async_client: AsyncClient, created_user):
    data1 = {
        "medication_name": "Финастерид",
        "frequency": 4,
        "duration_days": 4,
        "user_id": 1,
        "start_date": (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d"),
    }
    data2 = {
        "medication_name": "Фенибут",
        "frequency": 4,
        "duration_days": 4,
        "user_id": 1,
        "start_date": (datetime.now() + timedelta(days=11)).strftime("%Y-%m-%d"),
    }
    await async_client.post("/schedule", json=data1)
    await async_client.post("/schedule", json=data2)
    response = await async_client.get("/schedules", params={"user_id": 1})
    assert 200 == response.status_code
    expected_data = {"schedules": [], "user_id": 1}
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_non_existent_user_schedules(async_client: AsyncClient):
    response = await async_client.get("/schedules", params={"user_id": 2})
    assert 200 == response.status_code
    assert {"schedules": [], "user_id": 2} == response.json()


@pytest.mark.asyncio
async def test_get_schedules_not_for_this_user(async_client: AsyncClient, created_user):
    await async_client.post("/users", json={})
    data_user2 = {
        "medication_name": "Тренболон",
        "frequency": 3,
        "user_id": 2,
    }
    await async_client.post("/schedule", json=data_user2)
    response = await async_client.get("/schedules", params={"user_id": 1})
    assert 200 == response.status_code
    expected_data = {"user_id": 1, "schedules": []}
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_user_schedules_with_user_id_not_int(async_client: AsyncClient):
    response = await async_client.get("/schedules", params={"user_id": "abc"})
    assert 422 == response.status_code
    expected_data = [
        {
            "type": "int_parsing",
            "loc": ["query", "user_id"],
            "msg": "Input should be a valid integer, unable to parse string as an integer",
            "input": "abc",
        }
    ]

    assert expected_data == response.json()["detail"]


@pytest.mark.freeze_time("2025-01-01 7:00", real_asyncio=True)
@pytest.mark.asyncio
async def test_get_next_takings(async_client: AsyncClient, created_schedule):
    schedule2_data = {"medication_name": "Кокаколастик", "frequency": 7, "user_id": 1, "duration_days": 8}
    schedule3_data = {"medication_name": "NZT", "frequency": 15, "user_id": 1}
    await async_client.post("/schedule", json=schedule2_data)
    await async_client.post("/schedule", json=schedule3_data)
    response = await async_client.get("/next_takings", params={"user_id": 1})
    assert 200 == response.status_code
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
                "schedule_name": "Кокаколастик",
                "schedule_times": ["08:00"],
            },
            {
                "schedule_id": 3,
                "schedule_name": "NZT",
                "schedule_times": ["08:00", "09:00"],
            },
        ],
    }
    assert expected_data == response.json()


@pytest.mark.freeze_time("2025-01-01 7:59:59", real_asyncio=True)
@pytest.mark.asyncio
async def test_get_next_takings_one_minute_before_first_intake(async_client: AsyncClient, created_schedule):
    response = await async_client.get("/next_takings", params={"user_id": 1})
    expected_data = {
        "user_id": 1,
        "next_takings": [
            {
                "schedule_id": 1,
                "schedule_name": "Вайбкодинг",
                "schedule_times": ["08:00"],
            }
        ],
    }
    assert expected_data == response.json()


@pytest.mark.freeze_time("2025-01-01 8:01:00", real_asyncio=True)
@pytest.mark.asyncio
async def test_get_next_takings_one_minute_after_first_intake(async_client: AsyncClient, created_schedule):
    response = await async_client.get("/next_takings", params={"user_id": 1})
    expected_data = {
        "user_id": 1,
        "next_takings": [
            {
                "schedule_id": 1,
                "schedule_name": "Вайбкодинг",
                "schedule_times": ["08:00", "10:00"],
            }
        ],
    }
    assert expected_data == response.json()


@pytest.mark.freeze_time("2025-01-01 8:30:01", real_asyncio=True)
@pytest.mark.asyncio
async def test_get_next_takings_30_min_after_intake_hides_it(async_client: AsyncClient, created_schedule):
    response = await async_client.get("/next_takings", params={"user_id": 1})
    expected_data = {
        "user_id": 1,
        "next_takings": [
            {
                "schedule_id": 1,
                "schedule_name": "Вайбкодинг",
                "schedule_times": ["10:00"],
            }
        ],
    }
    assert expected_data == response.json()


@pytest.mark.asyncio
async def test_get_next_takings_with_expired_schedule(async_client: AsyncClient, created_user):
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
async def test_get_non_existent_next_takings_for_user(async_client: AsyncClient, created_user):
    response = await async_client.get("/next_takings", params={"user_id": 1})
    assert 200 == response.status_code
    assert {"next_takings": [], "user_id": 1} == response.json()


@pytest.mark.asyncio
async def test_get_next_takings_for_user_id_not_int(async_client: AsyncClient, created_user):
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
async def test_get_future_next_takings(async_client: AsyncClient, created_user):
    data1 = {
        "medication_name": "Финастерид",
        "frequency": 4,
        "duration_days": 4,
        "user_id": 1,
        "start_date": (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d"),
    }
    data2 = data1.copy()
    data2['start_date'] = (datetime.now() + timedelta(days=11)).strftime("%Y-%m-%d")
    await async_client.post("/schedule", json=data1)
    await async_client.post("/schedule", json=data2)
    response = await async_client.get("/next_takings", params={"user_id": 1})
    assert 200 == response.status_code
    expected_data = {"next_takings": [], "user_id": 1}
    assert expected_data == response.json()
