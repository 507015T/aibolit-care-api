from datetime import time
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent.parent


class Setting(BaseSettings):

    load_dotenv(BASE_DIR / ".env.dev")
    DB_USER: str = os.getenv('DB_USER')
    DB_PASS: str = os.getenv('DB_PASS')
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: str = os.getenv('DB_PORT')
    DB_NAME: str = os.getenv('DB_NAME')
    DB_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DB_ECHO: bool = True
    GRPC_PORT: int = 50051
    TIME_DAY_START: time = time(8, 0)
    TIME_DAY_END: time = time(22, 0)
    # in minutes
    NEXT_TAKINGS_PERIOD: int = 120
    INTAKE_WINDOW: int = 30
    TIME_ROUNDING_INTERVAL: int = 15


settings = Setting()
