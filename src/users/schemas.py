from datetime import date
from pydantic import BaseModel


class UserBase(BaseModel):
    id: int

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    pass
