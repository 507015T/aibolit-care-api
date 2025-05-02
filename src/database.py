from contextlib import asynccontextmanager
from typing import Annotated

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column

from config import settings

engine = create_async_engine(
    url=settings.DB_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DB_ECHO,
)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


class Base(DeclarativeBase): ...


# for grpc
@asynccontextmanager
async def get_db_ctx():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


async def get_db():
    async with get_db_ctx() as db:
        yield db


intpk = Annotated[int, mapped_column(primary_key=True, index=True)]
