from datetime import datetime, timedelta
from freezegun import freeze_time
from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp
import pytest
import grpc

from aibolit.transport.grpc.generated import schedule_pb2, user_pb2


@pytest.mark.asyncio
async def test_create_schedule(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())
    start_date = Timestamp()
    start_date.FromDatetime(datetime.now())
    request = schedule_pb2.CreateScheduleRequest(
        user_id=1, medication_name="Test Medication", start_date=start_date, frequency=15, duration_days=10
    )
    response = await stub_for_schedules.CreateSchedule(request)
    assert 1 == response.schedule_id


@pytest.mark.asyncio
async def test_create_schedule_without_start_date(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())
    request = schedule_pb2.CreateScheduleRequest(
        user_id=1, medication_name="Test Medication", frequency=15, duration_days=10
    )
    response = await stub_for_schedules.CreateSchedule(request)
    assert 1 == response.schedule_id


@pytest.mark.asyncio
async def test_create_schedule_without_duration_days_and_start_date(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())
    request = schedule_pb2.CreateScheduleRequest(user_id=1, medication_name="Test Medication", frequency=15)
    response = await stub_for_schedules.CreateSchedule(request)
    assert 1 == response.schedule_id


@pytest.mark.asyncio
async def test_create_schedule_with_non_existent_user(stub_for_schedules):
    start_date = Timestamp()
    start_date.FromDatetime(datetime.now())
    request = schedule_pb2.CreateScheduleRequest(
        user_id=1, medication_name="Test Medication", start_date=start_date, frequency=15, duration_days=10
    )
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await stub_for_schedules.CreateSchedule(request)
    err = exc_info.value.details()
    expected_data = 'User with id=1 not found'
    assert expected_data == err


@pytest.mark.asyncio
async def test_create_schedule_with_greater_frequency(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())
    request = schedule_pb2.CreateScheduleRequest(
        user_id=1, medication_name="Test Medication", frequency=16, duration_days=10
    )
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await stub_for_schedules.CreateSchedule(request)
    err = exc_info.value.details()
    assert 'Input should be less than 16' in err


@pytest.mark.asyncio
async def test_create_schedule_with_negative_frequency(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())
    request = schedule_pb2.CreateScheduleRequest(
        user_id=1, medication_name="Test Medication", frequency=-2, duration_days=10
    )
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await stub_for_schedules.CreateSchedule(request)
    err = exc_info.value.details()
    assert 'Input should be greater than 0' in err


@pytest.mark.asyncio
async def test_create_schedule_with_negative_duration_days(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())
    request = schedule_pb2.CreateScheduleRequest(
        user_id=1, medication_name="Test Medication", frequency=2, duration_days=-10
    )
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await stub_for_schedules.CreateSchedule(request)
    err = exc_info.value.details()
    assert 'Input should be greater than 0' in err


@pytest.mark.asyncio
async def test_create_schedule_with_negative_user_id(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())
    request = schedule_pb2.CreateScheduleRequest(
        user_id=-1, medication_name="Test Medication", frequency=2, duration_days=-10
    )
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await stub_for_schedules.CreateSchedule(request)
    err = exc_info.value.details()
    assert 'Input should be greater than 0' in err


@pytest.mark.asyncio
async def test_create_schedule_with_start_date_not_today(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())
    start_date = Timestamp()
    start_date.FromDatetime(datetime.now() - timedelta(days=10))
    request = schedule_pb2.CreateScheduleRequest(
        user_id=1, medication_name="Test Medication", frequency=2, duration_days=10, start_date=start_date
    )
    response = await stub_for_schedules.CreateSchedule(request)
    assert 1 == response.schedule_id


@pytest.mark.asyncio
async def test_create_schedule_with_old_start_date(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())
    start_date = Timestamp()
    start_date.FromDatetime(datetime.fromisoformat('2000-01-01'))
    request = schedule_pb2.CreateScheduleRequest(
        user_id=1, medication_name="Test Medication", frequency=2, duration_days=10, start_date=start_date
    )
    response = await stub_for_schedules.CreateSchedule(request)
    assert 1 == response.schedule_id


@pytest.mark.asyncio
async def test_get_all_user_schedules(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())

    create_schedule = schedule_pb2.CreateScheduleRequest(
        user_id=1, medication_name="Test Medication", frequency=15, duration_days=10
    )
    await stub_for_schedules.CreateSchedule(create_schedule)
    request = schedule_pb2.GetAllSchedulesRequest(user_id=1)
    response = await stub_for_schedules.GetAllSchedules(request)
    assert [1] == response.schedules
    assert 1 == response.user_id


@freeze_time("2025-01-01 7:59:59")
@pytest.mark.asyncio
async def test_get_user_schedule(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())

    create_schedule = schedule_pb2.CreateScheduleRequest(
        user_id=1, medication_name="Test Medication", frequency=15, duration_days=10
    )
    await stub_for_schedules.CreateSchedule(create_schedule)
    request = schedule_pb2.GetUserScheduleRequest(user_id=1, schedule_id=1)
    response = MessageToDict(await stub_for_schedules.GetUserSchedule(request), preserving_proto_field_name=True)
    expected_data = {
        'id': 1,
        'medication_name': 'Test Medication',
        'frequency': 15,
        'duration_days': 10,
        'start_date': '2025-01-01T00:00:00Z',
        'end_date': '2025-01-11T00:00:00Z',
        'user_id': 1,
        'daily_plan': [
            '08:00',
            '09:00',
            '10:00',
            '11:00',
            '12:00',
            '13:00',
            '14:00',
            '15:00',
            '16:00',
            '17:00',
            '18:00',
            '19:00',
            '20:00',
            '21:00',
            '22:00',
        ],
    }

    assert expected_data == response


@freeze_time("2025-01-01 7:59:59")
@pytest.mark.asyncio
async def test_get_user_next_takings(stub_for_schedules, stub_for_users):
    await stub_for_users.CreateUser(user_pb2.CreateUserRequest())

    create_schedule = schedule_pb2.CreateScheduleRequest(
        user_id=1, medication_name="Test Medication", frequency=15, duration_days=10
    )
    await stub_for_schedules.CreateSchedule(create_schedule)
    request = schedule_pb2.GetUserNextTakingsRequest(user_id=1)
    response = MessageToDict(await stub_for_schedules.GetUserNextTakings(request), preserving_proto_field_name=True)
    expected_data = {
        'user_id': 1,
        'next_takings': [{'schedule_id': 1, 'schedule_name': 'Test Medication', 'schedule_times': ['08:00', '09:00']}],
    }
    assert expected_data == response
