import types
import typing
import logging
from enum import Enum
from collections.abc import Generator
from typing import Annotated, Any, Literal, Optional, TypeAliasType, Union

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
                continue

            hint = self._resolve_type(hint)

            for ty in self._walk_type(hint):
                if issubclass(hint, BaseModel):
                    values[field_name] = self._process_model(
                        ty, values.get(field_name, {}), nef_settings
                    )

        return values

    def _resolve_type(self, hint: type) -> type:
        while True:
            if isinstance(hint, TypeAliasType):
                hint = hint.__value__
            elif typing.get_origin(hint) is Annotated:
                hint = typing.get_args(hint)[0]
            else:
                return hint

    def _walk_type(self, hint: type) -> Generator[type]:
        origin = typing.get_origin(hint)
        if origin is Union or origin is types.UnionType:
            type_args = typing.get_args(hint)
            for ty in type_args:
                yield ty
        else:
            yield type

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

            hint = self._resolve_type(hint)

            for ty in self._walk_type(hint):
                if issubclass(ty, BaseModel) and not self._is_nef_settings(ty):
                    values[field_name] = self._process_model(
                        ty, values.get(field_name, {}), nef_settings
                    )

        return values


class SMSBackend(str, Enum):
    Disabled = "disabled"
    Mock = "mock"
    SMSC = "smsc"


class OTPBackend(str, Enum):
    Memory = "memory"
    Redis = "redis"


class BaseSMSOTPSettings(BaseModel):
    otp_backend: OTPBackend = OTPBackend.Memory

    otp_code_size: PositiveInt = 6
    max_attempts: PositiveInt = 5
    otp_expiry_secs: PositiveInt = 1800


class DisabledSMSSettings(BaseSMSOTPSettings):
    sms_backend: Literal[SMSBackend.Disabled] = SMSBackend.Disabled


class MockSMSSettings(BaseSMSOTPSettings):
    sms_backend: Literal[SMSBackend.Mock] = SMSBackend.Mock


class SMSCSMSSettings(BaseSMSOTPSettings):
    sms_backend: Literal[SMSBackend.SMSC] = SMSBackend.SMSC

    smsc_url: AnyHttpUrl
    sender_id: Annotated[str, Field(max_length=11)]


type SMSOTPSettings = Annotated[
    DisabledSMSSettings | MockSMSSettings | SMSCSMSSettings,
    Field(discriminator="sms_backend"),
]


class QoSProfilesBackend(str, Enum):
    Disabled = "disabled"
    NEF = "nef"


class BaseQoSProfilesSettings(BaseModel):
    pass


class DisabledQoSProfilesSettings(BaseQoSProfilesSettings):
    backend: Literal[QoSProfilesBackend.Disabled] = QoSProfilesBackend.Disabled


class NEFQoSProfilesSettings(BaseQoSProfilesSettings):
    backend: Literal[QoSProfilesBackend.NEF] = QoSProfilesBackend.NEF
    nef: NEFSettings


type QoSProfilesSettings = Annotated[
    DisabledQoSProfilesSettings | NEFQoSProfilesSettings, Field(discriminator="backend")
]


class LocationBackend(str, Enum):
    Disabled = "disabled"
    Mock = "mock"
    Nef = "nef"


class BaseLocationSettings(BaseModel):
    pass


class DisabledLocationSettings(BaseLocationSettings):
    backend: Literal[LocationBackend.Disabled] = LocationBackend.Disabled


class MockLocationSettings(BaseLocationSettings):
    backend: Literal[LocationBackend.Mock] = LocationBackend.Mock


class NEFLocationSettings(BaseLocationSettings):
    backend: Literal[LocationBackend.Nef] = LocationBackend.Nef
    nef: NEFSettings


type LocationSettings = Annotated[
    DisabledLocationSettings | MockLocationSettings | NEFLocationSettings,
    Field(discriminator="backend"),
]


class QodProvisioningBackend(str, Enum):
    Disabled = "disabled"
    Nef = "nef"


class BaseProvisioningSettings(BaseModel):
    pass


class DisabledProvisioningSettings(BaseProvisioningSettings):
    backend: Literal[QodProvisioningBackend.Disabled] = QodProvisioningBackend.Disabled


class NEFProvisioningSettings(BaseProvisioningSettings):
    backend: Literal[QodProvisioningBackend.Nef] = QodProvisioningBackend.Nef
    nef: NEFSettings


type ProvisioningSettings = Annotated[
    DisabledProvisioningSettings | NEFProvisioningSettings,
    Field(discriminator="backend"),
]


class QodBackend(str, Enum):
    Disabled = "disabled"
    Nef = "nef"


class BaseQodSettings(BaseModel):
    pass


class DisabledQodSettings(BaseQodSettings):
    backend: Literal[QodBackend.Disabled] = QodBackend.Disabled


class NEFQodSettings(BaseQodSettings):
    backend: Literal[QodBackend.Nef] = QodBackend.Nef
    nef: NEFSettings


type QodSettings = Annotated[
    DisabledQodSettings | NEFQodSettings, Field(discriminator="backend")
]


class GeofencingBackend(str, Enum):
    Disabled = "disabled"
    NEF = "nef"


class BaseGeofencingSettings(BaseModel):
    pass


class DisabledGeofencingSettings(BaseGeofencingSettings):
    backend: Literal[GeofencingBackend.Disabled] = GeofencingBackend.Disabled


class NefGeofencingSettings(BaseGeofencingSettings):
    backend: Literal[GeofencingBackend.NEF] = GeofencingBackend.NEF
    nef: NEFSettings


type GeofencingSettings = Annotated[
    DisabledGeofencingSettings | NefGeofencingSettings, Field(discriminator="backend")
]


class ReachabilityStatusBackend(str, Enum):
    Disabled = "disabled"
    Nef = "nef"


class BaseReachabilityStatusSettings(BaseModel):
    pass


class DisabledReachabilityStatusSettings(BaseReachabilityStatusSettings):
    backend: Literal[ReachabilityStatusBackend.Disabled] = (
        ReachabilityStatusBackend.Disabled
    )


class NefReachabilityStatusSettings(BaseReachabilityStatusSettings):
    backend: Literal[ReachabilityStatusBackend.Nef] = ReachabilityStatusBackend.Nef
    nef: NEFSettings


type ReachabilityStatusSettings = Annotated[
    DisabledReachabilityStatusSettings | NefReachabilityStatusSettings,
    Field(discriminator="backend"),
]


class RoamingStatusBackend(str, Enum):
    Disabled = "disabled"
    Nef = "nef"


class BaseRoamingStatusSettings(BaseModel):
    pass


class DisabledRoamingStatusSettings(BaseRoamingStatusSettings):
    backend: Literal[RoamingStatusBackend.Disabled] = RoamingStatusBackend.Disabled


class NefRoamingStatusSettings(BaseRoamingStatusSettings):
    backend: Literal[RoamingStatusBackend.Nef] = RoamingStatusBackend.Nef
    nef: NEFSettings


type RoamingStatusSettings = Annotated[
    DisabledRoamingStatusSettings | NefRoamingStatusSettings,
    Field(discriminator="backend"),
]


class RedisSettings(BaseModel):
    url: RedisDsn = RedisDsn("redis://localhost:6379")
    username: Optional[str] = None
    password: Optional[str] = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file="config.toml",
        env_prefix="GATEWAY_",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
    )

    log_level: LogLevel = "INFO"

    redis: RedisSettings = RedisSettings()

    gateway_public_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

    nef: Optional[NEFSettings] = None

    sms_otp: SMSOTPSettings = DisabledSMSSettings()
    qos_profiles: QoSProfilesSettings = DisabledQoSProfilesSettings()
    location: LocationSettings = DisabledLocationSettings()
    qod_provisioning: ProvisioningSettings = DisabledProvisioningSettings()
    reachability_status: ReachabilityStatusSettings = (
        DisabledReachabilityStatusSettings()
    )
    geofencing: GeofencingSettings = DisabledGeofencingSettings()
    qod: QodSettings = DisabledQodSettings()
    roaming_status: RoamingStatusSettings = DisabledRoamingStatusSettings()

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
