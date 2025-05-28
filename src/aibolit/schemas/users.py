from pydantic import BaseModel, ConfigDict, PositiveInt


class UserCreateRequest(BaseModel): ...


class User(BaseModel):
    id: PositiveInt
    model_config = ConfigDict(from_attributes=True)


class UserCreateResponse(User): ...
