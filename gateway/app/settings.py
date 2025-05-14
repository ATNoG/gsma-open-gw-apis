import typing
import logging
from enum import Enum
from typing import Annotated, Any, Literal, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, Field, PositiveInt, RedisDsn
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


class NEFSettings(BaseModel):
    url: AnyHttpUrl
    base_path: str

    gateway_af_id: str
    gateway_notification_url: AnyHttpUrl

    username: str
    password: str

    def get_base_url(self) -> str:
        stripped_url = str(self.url).rstrip("/")
        stripped_base_path = self.base_path.strip("/")
        return f"{stripped_url}/{stripped_base_path}"

    def get_notification_url(self) -> str:
        return str(self.gateway_notification_url).rstrip("/")


class NEFSettingsHierachySettingsSource(PydanticBaseSettingsSource):
    """
    A settings source class that loads variables from the parent (if available)
    for the nef settings.
    """

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        # Nothing to do here. Only implement the return statement to make mypy happy
        return None, "", False

    def _is_nef_settings(self, hint: type) -> bool:
        type_args = typing.get_args(hint)
        if typing.get_origin(hint) is Union and type(None) in type_args:
            hint = next(t for t in type_args if t is not type(None))

        return issubclass(hint, NEFSettings)

    def _process_model(
        self,
        model: type[BaseModel],
        values: dict[str, Any],
        nef_settings: dict[str, Any],
    ) -> dict[str, Any]:
        hints = typing.get_type_hints(model)

        if hints is None or hints == {}:
            return values

        for field_name in self.settings_cls.model_fields.keys():
            hint = hints.get(field_name)

            if hint is None:
                continue

            if self._is_nef_settings(hint):
                existing_values = values.get(field_name, {})
                values[field_name] = nef_settings | existing_values
            elif issubclass(hint, BaseModel):
                values[field_name] = self._process_model(
                    hint, values.get(field_name, {}), nef_settings
                )

        return values

    def __call__(self) -> dict[str, Any]:
        values = self.current_state
        hints = typing.get_type_hints(self.settings_cls)

        nef_settings = None

        for field_name in self.settings_cls.model_fields.keys():
            hint = hints.get(field_name)

            if hint is None:
                continue

            if self._is_nef_settings(hint):
                if nef_settings is not None:
                    raise ValueError("Class has multiple nef settings at the top level")

                nef_settings = values.get(field_name, {})

        if nef_settings is None:
            raise ValueError("Class does not have nef settings at the top level")

        if nef_settings == {}:
            return values

        for field_name in self.settings_cls.model_fields.keys():
            hint = hints.get(field_name)

            if hint is None:
                continue

            if issubclass(hint, BaseModel) and not self._is_nef_settings(hint):
                values[field_name] = self._process_model(
                    hint, values.get(field_name, {}), nef_settings
                )

        return values


class SMSBackend(Enum):
    Mock = "mock"
    SMSC = "smsc"


class OTPBackend(Enum):
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


class QoSProfilesBackend(Enum):
    NEF = "nef"


class QoSProfilesSettings(BaseModel):
    backend: QoSProfilesBackend

    nef: NEFSettings


class LocationBackend(str, Enum):
    Mock = "mock"
    Nef = "nef"


class LocationSettings(BaseModel):
    backend: LocationBackend

    nef: NEFSettings


class QodProvisioningBackend(str, Enum):
    Nef = "nef"


class ProvisioningSettings(BaseModel):
    backend: QodProvisioningBackend

    nef: NEFSettings


class GeofencingBackend(Enum):
    NEF = "nef"


class GeofencingSettings(BaseModel):
    backend: GeofencingBackend

    nef: NEFSettings


class ReachabilityStatusBackend(str, Enum):
    Nef = "nef"


class ReachabilityStatusSettings(BaseModel):
    backend: ReachabilityStatusBackend

    nef: NEFSettings


class RedisSettings(BaseModel):
    url: RedisDsn = RedisDsn("redis://localhost:6379")
    username: Optional[str] = None
    password: Optional[str] = None


class QodBackend(str, Enum):
    Nef = "nef"


class QodSettings(BaseModel):
    qod_backend: QodProvisioningBackend
    af_id: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file="config.toml",
        env_prefix="GATEWAY_",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
    )

    log_level: LogLevel = "INFO"

    redis: RedisSettings

    gateway_public_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

    nef: Optional[NEFSettings] = None

    sms_otp: SMSOTPSettings
    qos_profiles: QoSProfilesSettings
    location: LocationSettings
    qod_provisioning: ProvisioningSettings
    reachability_status: ReachabilityStatusSettings
    geofencing: GeofencingSettings
    qod: QodSettings

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
            NEFSettingsHierachySettingsSource(settings_cls),
        )


settings = Settings()

logging.basicConfig(level=settings.log_level)
