from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    pass
