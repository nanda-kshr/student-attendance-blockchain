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
    contract_address: str | None = Field(None, alias="CONTRACT_ADDRESS")
    rpc_url: str | None = Field(None, alias="RPC_URL")
    private_key: str | None = Field(None, alias="PRIVATE_KEY")
    blockchain_url: str | None = Field(None, alias="BLOCKCHAIN_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
