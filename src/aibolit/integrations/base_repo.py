from abc import ABC, abstractmethod

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractBaseRepo(ABC):
    @abstractmethod
    async def create(self, data: BaseModel) -> BaseModel:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> BaseModel:
        raise NotImplementedError


class BaseRepo(AbstractBaseRepo):
    model = None

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
