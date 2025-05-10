from __future__ import annotations

from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Annotated, Any, Dict, Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field, model_validator


ProvisioningId = Annotated[
    UUID, Field(description="Provisioning Identifier in UUID format")
]

QosProfileName = Annotated[
    str,
    Field(
        pattern=r"^[a-zA-Z0-9_.-]+$",
        description="A unique name for identifying a specific QoS profile.\nThis may follow different formats depending on the service providers implementation.\nSome options addresses:\n  - A UUID style string\n  - Support for predefined profiles QOS_S, QOS_M, QOS_L, and QOS_E\n  - A searchable descriptive name\nThe set of QoS Profiles that an operator is offering can be retrieved by means of the [QoS Profile API](link TBC).\n",
        max_length=256,
        min_length=3,
    ),
]

Port = Annotated[int, Field(ge=0, le=65535, description="TCP or UDP port number.")]

NetworkAccessIdentifier = Annotated[
    str,
    Field(
        description="A public identifier addressing a subscription in a mobile network. In 3GPP terminology, it corresponds to the GPSI formatted with the External Identifier ({Local Identifier}@{Domain Identifier}). Unlike the telephone number, the network access identifier is not subjected to portability ruling in force, and is individually managed by each operator.",
        examples=["123456789@domain.com"],
    ),
]

PhoneNumber = Annotated[
    str,
    Field(
        pattern=r"^\+[1-9][0-9]{4,14}$",
        description="A public identifier addressing a telephone subscription. In mobile networks it corresponds to the MSISDN (Mobile Station International Subscriber Directory Number). In order to be globally unique it has to be formatted in international format, according to E.164 standard, prefixed with '+'.",
        examples=["+123456789"],
    ),
]

DeviceIpv6Address = Annotated[
    IPv6Address,
    Field(
        description="The device should be identified by the observed IPv6 address, or by any single IPv6 address from within the subnet allocated to the device (e.g. adding ::0 to the /64 prefix).\n",
        examples=["2001:db8:85a3:8d3:1319:8a2e:370:7344"],
    ),
]


class CredentialType(Enum):
    PLAIN = "PLAIN"
    ACCESSTOKEN = "ACCESSTOKEN"
    REFRESHTOKEN = "REFRESHTOKEN"


class SinkCredential(BaseModel):
    credentialType: CredentialType = Field(description="The type of the credential.")


class PlainCredential(SinkCredential):
    identifier: str = Field(
        description="The identifier might be an account or username."
    )
    secret: str = Field(description="The secret might be a password or passphrase.")


class AccessTokenType(Enum):
    bearer = "bearer"


class AccessTokenCredential(SinkCredential):
    accessToken: str = Field(
        description="REQUIRED. An access token is a previously acquired token granting access to the target resource.",
    )
    accessTokenExpiresUtc: datetime = Field(
        description="REQUIRED. An absolute UTC instant at which the token shall be considered expired.",
    )
    accessTokenType: AccessTokenType = Field(
        description="REQUIRED. Type of the access token (See [OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-7.1)).",
    )


class RefreshTokenCredential(SinkCredential):
    accessToken: str = Field(
        description="REQUIRED. An access token is a previously acquired token granting access to the target resource.",
    )
    accessTokenExpiresUtc: datetime = Field(
        description="REQUIRED. An absolute UTC instant at which the token shall be considered expired.",
    )
    accessTokenType: AccessTokenType = Field(
        description="REQUIRED. Type of the access token (See [OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-7.1)).",
    )
    refreshToken: str = Field(
        description="REQUIRED. An refresh token credential used to acquire access tokens.",
    )
    refreshTokenEndpoint: AnyUrl = Field(
        description="REQUIRED. A URL at which the refresh token can be traded for an access token.",
    )


class Type(Enum):
    org_camaraproject_qod_provisioning_v0_status_changed = (
        "org.camaraproject.qod-provisioning.v0.status-changed"
    )


class Specversion(Enum):
    field_1_0 = "1.0"


class Datacontenttype(Enum):
    application_json = "application/json"


class CloudEvent(BaseModel):
    id: str = Field(
        description="Identifier of this event, that must be unique in the source context.",
    )
    source: str = Field(
        description="Identifies the context in which an event happened in the specific Provider Implementation.",
    )
    type: Type = Field(description="The type of the event.")
    specversion: Specversion = Field(
        description="Version of the specification to which this event conforms (must be 1.0 if it conforms to cloudevents 1.0.2 version)",
    )
    datacontenttype: Optional[Datacontenttype] = Field(
        None,
        description='media-type that describes the event payload encoding, must be "application/json" for CAMARA APIs',
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Event notification details payload, which depends on the event type",
    )
    time: datetime = Field(
        description="Timestamp of when the occurrence happened. It must follow RFC 3339\n",
    )


class StatusInfo(Enum):
    NETWORK_TERMINATED = "NETWORK_TERMINATED"
    DELETE_REQUESTED = "DELETE_REQUESTED"


class Status(Enum):
    REQUESTED = "REQUESTED"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class StatusChanged(Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class Data(BaseModel):
    provisioningId: ProvisioningId
    status: Optional[StatusChanged] = None
    statusInfo: Optional[StatusInfo] = None


class EventStatusChanged(CloudEvent):
    eventData: Data = Field(description="Event details depending on the event type")


class DeviceIpv4Addr(BaseModel):
    publicAddress: IPv4Address
    privateAddress: Optional[IPv4Address] = None
    publicPort: Optional[Port] = None

    @model_validator(mode="after")
    def any_of(cls, v: Any) -> Any:
        if not v.privateAddress and not (v.publicAddress and v.publicPort):
            raise ValueError(
                "Either the private address or the public address and public port should be set."
            )
        return v


class Device(BaseModel):
    phoneNumber: Optional[PhoneNumber] = None
    networkAccessIdentifier: Optional[NetworkAccessIdentifier] = None
    ipv4Address: DeviceIpv4Addr
    ipv6Address: DeviceIpv6Address


class BaseProvisioningInfo(BaseModel):
    device: Optional[Device] = None
    qosProfile: QosProfileName
    sink: Optional[str] = Field(
        None,
        description="The address to which events shall be delivered, using the HTTP protocol.",
        examples=["https://endpoint.example.com/sink"],
    )
    sinkCredential: Optional[SinkCredential] = None


class ProvisioningInfo(BaseProvisioningInfo):
    provisioningId: ProvisioningId
    startedAt: Optional[datetime] = Field(
        None,
        description='Date and time when the provisioning became "AVAILABLE". Not to be returned when `status` is "REQUESTED". Format must follow RFC 3339 and must indicate time zone (UTC or local).',
        examples=["2024-06-01T12:00:00Z"],
    )
    status: Status
    statusInfo: Optional[StatusInfo] = None


class CreateProvisioning(BaseProvisioningInfo):
    pass


class RetrieveProvisioningByDevice(BaseModel):
    device: Optional[Device] = None
