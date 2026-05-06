from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Service
    APP_NAME: str = "MFDataService"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "MFData"

    # Data Loading
    DATADUMP_ROOT: str = "/Users/jpsinha/Documents/MFDataService"

    # API Keys (comma-separated)
    API_KEYS: str = ""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8100

    @property
    def api_keys_list(self) -> List[str]:
        if not self.API_KEYS:
            return []
        return [k.strip() for k in self.API_KEYS.split(",") if k.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
