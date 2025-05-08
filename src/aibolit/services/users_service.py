from typing import Optional


from aibolit.integrations.users_repo import UsersRepo
from aibolit.transport.rest.users.schemas import AllUsers, User, UserCreateRequest


# TODO: ЗДЕСЬ ЗАКОНЧИЛ list_users низя возвращать модель это нарушает че то там
class UserService:
    def __init__(self, users_repo: UsersRepo) -> None:
        self._users_repo = users_repo

    async def create_user(self, user: UserCreateRequest) -> int:
        db_user = await self._users_repo.create_user(user)
        return db_user.id

    async def list_users(self) -> AllUsers:
        db_users = [User(id=user.id) for user in await self._users_repo.get_users()]
        users = AllUsers(users=db_users)
        return users

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        db_user = await self._users_repo.get_user_by_id(user_id)
        user = User.model_validate(db_user) if db_user else None
        return user
