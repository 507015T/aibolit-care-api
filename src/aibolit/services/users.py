from typing import Optional


from aibolit.repositories.users import UserRepo

# from aibolit.schemas.users import User, UserCreateRequest
from aibolit.schemas.openapi_generated import UserCreateResponse as User, UserCreateRequest
from aibolit.core.logger import get_logger

logger = get_logger(__name__)


class UserService:
    def __init__(self, users_repo: UserRepo) -> None:
        self._users_repo = users_repo

    async def create_user(self, user: UserCreateRequest) -> int:
        logger.info("Creating user")
        db_user = await self._users_repo.create_user(user)
        logger.info(f"User with id={db_user.id} was created")
        return db_user.id

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        logger.info(f"Get user with id={user_id}")
        db_user = await self._users_repo.get_user_by_id(user_id)
        user = User.model_validate(db_user.__dict__) if db_user else None
        return user
