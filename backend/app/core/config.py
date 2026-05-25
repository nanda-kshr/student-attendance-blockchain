from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mongo_uri: str = Field(alias="MONGO_URI")
    port: int = Field(8000, alias="PORT")
    jwt_secret: str = Field("fakfFBKJEABFKJA-me", alias="JWT_SECRET")
    jwt_alg: str = "HS256"
    access_token_exp_minutes: int = 60 * 24


@lru_cache
def get_settings() -> Settings:
    return Settings()
