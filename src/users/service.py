from sqlalchemy import select

from users import models


async def create_user(user, db):
    db_user = models.UserOrm(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(user_id, db):
    filtering = await db.execute(select(models.UserOrm).filter(models.UserOrm.id == user_id))
    user = filtering.scalar_one_or_none()
    return user


async def validate_user_exists(user_id, db):
    user = await get_user_by_id(user_id, db)
    return user is not None


async def get_users(db):
    results = await db.execute(select(models.UserOrm))
    users = results.scalars().all()
    return users
