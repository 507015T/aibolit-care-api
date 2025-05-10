from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from aibolit.core.database import get_db
from aibolit.repositories.schedules.repository import ScheduleRepo
from aibolit.repositories.users.repository import UserRepo
from aibolit.services.schedules.service import ScheduleService
from aibolit.services.users.service import UserService


def get_users_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> UserRepo:
    return UserRepo(session)


def get_schedules_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> ScheduleRepo:
    return ScheduleRepo(session)


async def get_schedule_service(schedules_repo: Annotated[ScheduleRepo, Depends(get_schedules_repo)]) -> ScheduleService:
    return ScheduleService(schedules_repo)


async def get_user_service(users_repo: Annotated[UserRepo, Depends(get_users_repo)]) -> UserService:
    return UserService(users_repo)
