from datetime import time
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOGS_DIR: Path = BASE_DIR / "logs"
    # env variables
    APP_PORT: int = 8000
    APP_HOST: str = "localhost"
    DB_USER: str = "aibolit_user"
    DB_PASS: str = "aibolit_password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 6543
    DB_NAME: str = "aibolit_db"
    DB_ECHO: bool = False
    GRPC_PORT: int = 50051
    # for tests
    TEST_DB_USER: str = "aibolit_user"
    TEST_DB_NAME: str = "test_aibolit_db"
    TEST_DB_PASS: str = "aibolit_password"
    TEST_DB_HOST: str = "localhost"
    TEST_DB_PORT: int = 6543
    # -------------
    TIME_DAY_START: time = time(8, 0)
    TIME_DAY_END: time = time(22, 0)
    NEXT_TAKINGS_PERIOD: int = 120
    INTAKE_WINDOW: int = 30
    TIME_ROUNDING_INTERVAL: int = 15

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8")


settings = Settings()
