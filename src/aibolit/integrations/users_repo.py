from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aibolit.models.user import UserOrm
from aibolit.transport.rest.users.schemas import UserCreateRequest


class UsersRepo:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_user(self, user: UserCreateRequest) -> UserOrm:
        db_user = UserOrm(**user.model_dump())
        self._db.add(db_user)
        await self._db.commit()
        await self._db.refresh(db_user)
        return db_user

    async def get_user_by_id(self, user_id: int) -> Optional[UserOrm]:
        filtering = await self._db.execute(select(UserOrm).filter(UserOrm.id == user_id))
        user = filtering.scalar_one_or_none()
        return user

    async def get_users(self) -> Sequence[UserOrm]:
        results = await self._db.execute(select(UserOrm))
        users = results.scalars().all()
        return users
