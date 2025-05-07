from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from aibolit.database import get_db
from aibolit.integrations.users_repo import UsersRepo
from aibolit.integrations.schedules_repo import SchedulesRepo


def get_users_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> UsersRepo:
    return UsersRepo(session)


def get_schedules_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> SchedulesRepo:
    return SchedulesRepo(session)
