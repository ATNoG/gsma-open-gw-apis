from enum import Enum

from pydantic import AnyHttpUrl, BaseModel, PositiveInt
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class SMSBackend(str, Enum):
    Mock = "mock"
    SMSC = "smsc"


class SMSOTPSettings(BaseModel):
    backend: SMSBackend

    otp_code_size: PositiveInt = 6
    max_checks: PositiveInt = 5

    smsc_url: AnyHttpUrl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")

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
