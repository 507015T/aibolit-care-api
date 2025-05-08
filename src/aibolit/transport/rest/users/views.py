from fastapi import APIRouter, Depends
from typing_extensions import Annotated

from aibolit.dependencies import get_user_service
from aibolit.services.users_service import UserService
from aibolit.transport.rest.users.schemas import AllUsers, UserCreateRequest, User, UserCreateResponse

router = APIRouter()


@router.post("/users", status_code=201, response_model=UserCreateResponse)
async def create_user(user: UserCreateRequest, user_service: Annotated[UserService, Depends(get_user_service)]):
    new_user_id = await user_service.create_user(user)
    return UserCreateResponse(id=new_user_id)


@router.get("/users", response_model=AllUsers)
async def get_users(user_service: Annotated[UserService, Depends(get_user_service)]):
    all_users = await user_service.list_users()
    all_users = [User(id=user.id) for user in all_users.users]
    return AllUsers(users=all_users)
