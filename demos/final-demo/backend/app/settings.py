from typing import Any
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file="config.toml",
    )

    gateway_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")


settings = Settings()
