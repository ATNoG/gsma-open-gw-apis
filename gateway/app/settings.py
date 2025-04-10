import logging
from enum import Enum
from typing import Annotated, Literal

from pydantic import AnyHttpUrl, BaseModel, Field, PositiveInt
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


class SMSBackend(str, Enum):
    Mock = "mock"
    SMSC = "smsc"


class OTPBackend(str, Enum):
    Memory = "memory"
    Redis = "redis"


class SMSOTPSettings(BaseModel):
    sms_backend: SMSBackend
    otp_backend: OTPBackend

    otp_code_size: PositiveInt = 6
    max_attempts: PositiveInt = 5
    otp_expiry_secs: PositiveInt = 1800

    smsc_url: AnyHttpUrl
    sender_id: Annotated[str, Field(max_length=11)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")

    log_level: LogLevel = "INFO"
    redis_url: str = "redis://localhost:6379"

    sms_otp: SMSOTPSettings

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


settings = Settings()

logging.basicConfig(level=settings.log_level)
