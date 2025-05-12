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


class SMSBackend(Enum):
    Mock = "mock"
    SMSC = "smsc"


class OTPBackend(Enum):
    Memory = "memory"
    Redis = "redis"


class QodProvisioningBackend(str, Enum):
    Nef = "nef"


class SMSOTPSettings(BaseModel):
    sms_backend: SMSBackend
    otp_backend: OTPBackend

    otp_code_size: PositiveInt = 6
    max_attempts: PositiveInt = 5
    otp_expiry_secs: PositiveInt = 1800

    smsc_url: AnyHttpUrl
    sender_id: Annotated[str, Field(max_length=11)]


class QoSProfilesBackend(Enum):
    NEF = "nef"


class QoSProfilesSettings(BaseModel):
    backend: QoSProfilesBackend


class LocationBackend(str, Enum):
    Mock = "mock"
    Nef = "nef"


class LocationSettings(BaseModel):
    backend: LocationBackend


class ProvisioningSettings(BaseModel):
    qod_provisioning_backend: QodProvisioningBackend
    af_id: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")

    log_level: LogLevel = "INFO"
    redis_url: str = "redis://localhost:6379"

    gateway_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

    nef_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8888/")
    nef_gateway_url: AnyHttpUrl = AnyHttpUrl("http://host.docker.internal:8000")
    nef_username: str = "admin@my-email.com"
    nef_password: str = "pass"

    sms_otp: SMSOTPSettings
    qos_profiles: QoSProfilesSettings
    location: LocationSettings
    qod_provisioning: ProvisioningSettings

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
