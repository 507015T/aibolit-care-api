from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aibolit.models.users import UserOrm

# from aibolit.schemas.users import UserCreateRequest
from aibolit.schemas.openapi_generated import UserCreateRequest


class UserRepo:
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
