from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings


engine = create_async_engine(
    settings.DB_URL, connect_args={"check_same_thread": False}, echo=settings.DB_ECHO
)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


class Base(DeclarativeBase): ...


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    await create_tables()
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
