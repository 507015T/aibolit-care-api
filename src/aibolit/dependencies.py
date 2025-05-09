from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from aibolit.database import get_db
from aibolit.integrations.schedules_repo import SchedulesRepo
from aibolit.integrations.users_repo import UsersRepo
from aibolit.services.schedules_service import ScheduleService
from aibolit.services.users_service import UserService


def get_users_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> UsersRepo:
    return UsersRepo(session)


def get_schedules_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> SchedulesRepo:
    return SchedulesRepo(session)


async def get_schedule_service(
    schedules_repo: Annotated[SchedulesRepo, Depends(get_schedules_repo)]
) -> ScheduleService:
    return ScheduleService(schedules_repo)


async def get_user_service(users_repo: Annotated[UsersRepo, Depends(get_users_repo)]) -> UserService:
    return UserService(users_repo)
