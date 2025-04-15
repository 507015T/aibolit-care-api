from users import models
from sqlalchemy import select


async def create_user(user, db):
    db_users = models.User(**user.model_dump())
    db.add(db_users)
    await db.commit()
    await db.refresh(db_users)
    return db_users


async def get_users(db):
    results = await db.execute(select(models.User))
    users = results.scalars().all()
    return {"users": users}
