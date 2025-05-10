from typing import List
from pydantic import BaseModel, ConfigDict, PositiveInt


class UserBase(BaseModel):

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    id: PositiveInt


class UserCreateRequest(UserBase):
    pass


class UserCreateResponse(User): ...


class AllUsers(BaseModel):
    users: List[User]
