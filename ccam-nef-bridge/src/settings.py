import logging
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


class BrokerSettings(BaseModel):
    client_id: str = "gsma-open-gateway"

    host: str = "es-broker.av.it.pt"
    port: int = 8090

    username: str | None = None
    password: str | None = None

    transport: Literal["tcp", "websockets", "unix"] = "websockets"
    ws_path: str = "/WS"


class NEFSettings(BaseModel):
    url: AnyHttpUrl = AnyHttpUrl("http://localhost:8888")

    username: str = "admin@my-email.com"
    password: str = "pass"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file="config.toml",
        env_prefix="CCAM_BRIDGE_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    log_level: LogLevel = "INFO"

    broker: BrokerSettings = BrokerSettings()
    nef: NEFSettings = NEFSettings()

    event_throttling: float = 2.5
    topic_base_path: str = "its_center/inqueue/json"
    vehicle_supis: dict[str, str] = {}

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
            env_settings,
            dotenv_settings,
            TomlConfigSettingsSource(settings_cls),
        )


settings = Settings()

logging.basicConfig(level=settings.log_level)
