from fastapi import APIRouter, Depends
import database
from users import service, schemas
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.post("/users")
async def create_user(
    user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)
):
    return await service.create_user(user, db)


@router.get("/users")
async def get_users(db: AsyncSession = Depends(database.get_db)):
    return await service.get_users(db)
