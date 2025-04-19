from datetime import date
from pydantic import BaseModel
from pydantic import ConfigDict


class UserBase(BaseModel):

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    pass
