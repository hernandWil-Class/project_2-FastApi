from functools import lru_cache

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class Settings(BaseSettings):
    app_name: str = "Real-Time Fraud Scoring API"
    environment: str = "local"
    model_or_policy_version: str = "policy-v1.0.0"
    accept_threshold: int = Field(default=35, ge=0, le=100)
    reject_threshold: int = Field(default=70, ge=0, le=100)
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="FRAUD_API_",
        env_file=".env",
        yaml_file="config.yaml",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
