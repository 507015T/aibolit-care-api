from datetime import time
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent


class Setting(BaseSettings):
    DB_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/db.sqlite3"
    DB_ECHO: bool = True
    TIME_DAY_START: time = time(8, 0)
    TIME_DAY_END: time = time(22, 0)
    NEXT_TAKINGS_PERIOD: int = 120
    GRPC_PORT: int = 50051


settings = Setting()
