from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    jwt_secret: str = Field(..., env="JWT_SECRET")
    base_url: str = Field(..., env="BASE_URL")

    model_config = SettingsConfigDict(env_file=".env")


def get_settings():
    return Settings()
