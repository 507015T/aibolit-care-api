from datetime import datetime, timedelta
from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp
import pytest
import grpc
import pytest_asyncio

from aibolit.grpc.generated import schedules_pb2, users_pb2


@pytest_asyncio.fixture
async def created_user(stub_for_users):
    return await stub_for_users.CreateUser(users_pb2.CreateUserRequest())


@pytest_asyncio.fixture
async def created_schedule(created_user, stub_for_schedules):
    data = {"user_id": 1, "medication_name": "Pill", "frequency": 15, "duration_days": 10}
    return await stub_for_schedules.CreateSchedule(schedules_pb2.CreateScheduleRequest(**data))


@pytest_asyncio.fixture
async def created_future_schedule(created_user, stub_for_schedules):
    start_date = Timestamp()
    start_date.FromDatetime(datetime.now() + timedelta(days=4))
    data = {"user_id": 1, "medication_name": "Pill", "frequency": 15, "duration_days": 10, "start_date": start_date}
    return await stub_for_schedules.CreateSchedule(schedules_pb2.CreateScheduleRequest(**data))


@pytest.mark.asyncio
async def test_create_schedule(stub_for_schedules, created_user):
    start_date = Timestamp()
    start_date.FromDatetime(datetime.now())
    data = {"user_id": 1, "medication_name": "Pill", "start_date": start_date, "frequency": 15, "duration_days": 10}
    request = schedules_pb2.CreateScheduleRequest(**data)
    response = await stub_for_schedules.CreateSchedule(request)
    assert 1 == response.schedule_id


@pytest.mark.asyncio
async def test_create_schedule_without_start_date(stub_for_schedules, created_user):
    data = {"user_id": 1, "medication_name": "Pill", "frequency": 15, "duration_days": 10}
    request = schedules_pb2.CreateScheduleRequest(**data)
    response = await stub_for_schedules.CreateSchedule(request)
    assert 1 == response.schedule_id


@pytest.mark.asyncio
async def test_create_schedule_without_duration_days_and_start_date(stub_for_schedules, created_user):
    data = {"user_id": 1, "medication_name": "Pill", "frequency": 15}
    request = schedules_pb2.CreateScheduleRequest(**data)
    response = await stub_for_schedules.CreateSchedule(request)
    assert 1 == response.schedule_id


@pytest.mark.asyncio
async def test_create_schedule_with_non_existent_user(stub_for_schedules):
    start_date = Timestamp()
    start_date.FromDatetime(datetime.now())
    data = {"user_id": 1, "medication_name": "Pill", "start_date": start_date, "frequency": 15, "duration_days": 10}
    request = schedules_pb2.CreateScheduleRequest(**data)
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await stub_for_schedules.CreateSchedule(request)
    err = exc_info.value.details()
    expected_data = "User with id=1 not found"
    assert expected_data == err


@pytest.mark.asyncio
async def test_create_schedule_with_greater_frequency(stub_for_schedules, created_user):
    data = {"user_id": 1, "medication_name": "Pill", "frequency": 16, "duration_days": 10}
    request = schedules_pb2.CreateScheduleRequest(**data)
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await stub_for_schedules.CreateSchedule(request)
    err = exc_info.value.details()
    assert "Input should be less than 16" in err


@pytest.mark.asyncio
async def test_create_schedule_with_negative_frequency(stub_for_schedules, created_user):
    data = {"user_id": 1, "medication_name": "Pill", "frequency": -2, "duration_days": 10}
    request = schedules_pb2.CreateScheduleRequest(**data)
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await stub_for_schedules.CreateSchedule(request)
    err = exc_info.value.details()
    assert "Input should be greater than 0" in err


@pytest.mark.asyncio
async def test_create_schedule_with_negative_duration_days(stub_for_schedules, created_user):
    data = {"user_id": 1, "medication_name": "Pill", "frequency": 2, "duration_days": -10}
    request = schedules_pb2.CreateScheduleRequest(**data)
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await stub_for_schedules.CreateSchedule(request)
    err = exc_info.value.details()
    assert "Input should be greater than 0" in err


@pytest.mark.asyncio
async def test_create_schedule_with_negative_user_id(stub_for_schedules, created_user):
    data = {"user_id": -1, "medication_name": "Pill", "frequency": 2, "duration_days": 10}
    request = schedules_pb2.CreateScheduleRequest(**data)
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await stub_for_schedules.CreateSchedule(request)
    err = exc_info.value.details()
    assert "Input should be greater than 0" in err


@pytest.mark.asyncio
async def test_create_schedule_with_start_date_not_today(stub_for_schedules, created_user):
    start_date = Timestamp()
    start_date.FromDatetime(datetime.now() - timedelta(days=10))
    data = {
        "user_id": 1,
        "medication_name": "Pill",
        "frequency": 2,
        "duration_days": 10,
        "start_date": start_date,
    }
    request = schedules_pb2.CreateScheduleRequest(**data)
    response = await stub_for_schedules.CreateSchedule(request)
    assert 1 == response.schedule_id


@pytest.mark.asyncio
async def test_create_schedule_with_old_start_date(stub_for_schedules, created_user):
    start_date = Timestamp()
    start_date.FromDatetime(datetime.fromisoformat("2000-01-01"))
    data = {
        "user_id": 1,
        "medication_name": "Pill",
        "frequency": 2,
        "duration_days": 10,
        "start_date": start_date,
    }
    request = schedules_pb2.CreateScheduleRequest(**data)
    response = await stub_for_schedules.CreateSchedule(request)
    assert 1 == response.schedule_id


@pytest.mark.asyncio
async def test_get_all_user_schedules(stub_for_schedules, created_schedule):
    request = schedules_pb2.GetAllSchedulesRequest(user_id=1)
    response = await stub_for_schedules.GetAllSchedules(request)
    assert [1] == response.schedules
    assert 1 == response.user_id


@pytest.mark.freeze_time("2025-01-01 7:59:59")
@pytest.mark.asyncio
async def test_get_user_schedule(stub_for_schedules, created_schedule):
    request = schedules_pb2.GetUserScheduleRequest(user_id=1, schedule_id=1)
    response = MessageToDict(await stub_for_schedules.GetUserSchedule(request), preserving_proto_field_name=True)
    expected_data = {
        "id": 1,
        "medication_name": "Pill",
        "frequency": 15,
        "duration_days": 10,
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-01-11T00:00:00Z",
        "user_id": 1,
        "daily_plan": [
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
    }

    assert expected_data == response


@pytest.mark.freeze_time("2025-01-01 7:59:59")
@pytest.mark.asyncio
async def test_get_user_next_takings(stub_for_schedules, created_schedule):
    data_schedule2 = {"user_id": 1, "medication_name": "Pill 2", "frequency": 15, "duration_days": 10}
    created_schedule_2 = schedules_pb2.CreateScheduleRequest(**data_schedule2)
    await stub_for_schedules.CreateSchedule(created_schedule_2)
    request = schedules_pb2.GetUserNextTakingsRequest(user_id=1)
    response = MessageToDict(await stub_for_schedules.GetUserNextTakings(request), preserving_proto_field_name=True)
    expected_data = {
        "user_id": 1,
        "next_takings": [
            {"schedule_id": 1, "schedule_name": "Pill", "schedule_times": ["08:00", "09:00"]},
            {"schedule_id": 2, "schedule_name": "Pill 2", "schedule_times": ["08:00", "09:00"]},
        ],
    }
    assert expected_data == response


@pytest.mark.asyncio
async def test_get_future_next_takings(stub_for_schedules, created_future_schedule):
    request = schedules_pb2.GetUserNextTakingsRequest(user_id=1)
    response = MessageToDict(
        await stub_for_schedules.GetUserNextTakings(request),
        preserving_proto_field_name=True,
        always_print_fields_with_no_presence=True,
    )
    expected_data = {"user_id": 1, "next_takings": []}
    assert expected_data == response


@pytest.mark.asyncio
async def test_get_future_schedule(stub_for_schedules, created_future_schedule):
    request = schedules_pb2.GetUserScheduleRequest(user_id=1, schedule_id=1)
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await stub_for_schedules.GetUserSchedule(request)
    err = exc_info.value.details()
    expected_data = (
        f"The medication 'Pill' intake will begin {(datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')}"
    )
    assert expected_data == err


@pytest.mark.asyncio
async def test_get_all_future_schedules(stub_for_schedules, created_future_schedule):
    request = schedules_pb2.GetAllSchedulesRequest(user_id=1)
    response = MessageToDict(
        await stub_for_schedules.GetAllSchedules(request),
        preserving_proto_field_name=True,
        always_print_fields_with_no_presence=True,
    )
    expected_data = {"schedules": [], "user_id": 1}
    assert expected_data == response
