from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Real-Time Fraud Scoring API"
    environment: str = "local"
    model_or_policy_version: str = "policy-v1.0.0"
    accept_threshold: int = Field(default=35, ge=0, le=100)
    reject_threshold: int = Field(default=70, ge=0, le=100)
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_prefix="FRAUD_API_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
