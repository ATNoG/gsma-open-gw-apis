from typing import Annotated

from pydantic import AnyHttpUrl, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class QueueGeofencingSettings(BaseSettings):
    latitude: Annotated[float, Field(ge=-90, le=90)] = 38.000392
    longitude: Annotated[float, Field(ge=-180, le=180)] = 23.818231
    radius: Annotated[int, Field(gt=0)] = 65


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file="config.toml",
    )

    queue_geofencing: QueueGeofencingSettings
    gateway_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

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
            TomlConfigSettingsSource(settings_cls),
        )


settings = Settings()
