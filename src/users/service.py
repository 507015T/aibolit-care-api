from sqlalchemy import select

from users import models


async def create_user(user, db):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_users(db):
    results = await db.execute(select(models.User))
    users = results.scalars().all()
    return {"users": users}
