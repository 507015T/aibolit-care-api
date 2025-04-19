from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings


engine = create_async_engine(
    url=settings.DB_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DB_ECHO,
)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


class Base(DeclarativeBase): ...


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
