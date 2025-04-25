from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

import database
from users import schemas, service

router = APIRouter()


@router.post("/users", status_code=201)
async def create_user(user: schemas.UserCreate, db: Annotated[AsyncSession, Depends(database.get_db)]):
    return await service.create_user(user, db)


@router.get("/users")
async def get_users(db: Annotated[AsyncSession, Depends(database.get_db)]):
    return await service.get_users(db)
