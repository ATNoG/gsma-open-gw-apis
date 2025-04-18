from __future__ import annotations

from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Any, Dict, Optional, Union
from uuid import UUID

from pydantic import AnyHttpUrl, AnyUrl, BaseModel, Field


class ProvisioningId(BaseModel):
    __root__: UUID = Field(..., description="Provisioning Identifier in UUID format")


class CredentialType(Enum):
    PLAIN = "PLAIN"
    ACCESSTOKEN = "ACCESSTOKEN"
    REFRESHTOKEN = "REFRESHTOKEN"


class SinkCredential(BaseModel):
    credentialType: CredentialType = Field(
        ..., description="The type of the credential."
    )


class PlainCredential(SinkCredential):
    identifier: str = Field(
        ..., description="The identifier might be an account or username."
    )
    secret: str = Field(
        ..., description="The secret might be a password or passphrase."
    )


class AccessTokenType(Enum):
    bearer = "bearer"


class AccessTokenCredential(SinkCredential):
    accessToken: str = Field(
        ...,
        description="REQUIRED. An access token is a previously acquired token granting access to the target resource.",
    )
    accessTokenExpiresUtc: datetime = Field(
        ...,
        description="REQUIRED. An absolute UTC instant at which the token shall be considered expired.",
    )
    accessTokenType: AccessTokenType = Field(
        ...,
        description="REQUIRED. Type of the access token (See [OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-7.1)).",
    )


class RefreshTokenCredential(SinkCredential):
    accessToken: str = Field(
        ...,
        description="REQUIRED. An access token is a previously acquired token granting access to the target resource.",
    )
    accessTokenExpiresUtc: datetime = Field(
        ...,
        description="REQUIRED. An absolute UTC instant at which the token shall be considered expired.",
    )
    accessTokenType: AccessTokenType = Field(
        ...,
        description="REQUIRED. Type of the access token (See [OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-7.1)).",
    )
    refreshToken: str = Field(
        ...,
        description="REQUIRED. An refresh token credential used to acquire access tokens.",
    )
    refreshTokenEndpoint: AnyUrl = Field(
        ...,
        description="REQUIRED. A URL at which the refresh token can be traded for an access token.",
    )


class Port(BaseModel):
    __root__: int = Field(..., ge=0, le=65535, description="TCP or UDP port number.")


class QosProfileName(BaseModel):
    __root__: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9_.-]+$",
        description="A unique name for identifying a specific QoS profile.\nThis may follow different formats depending on the service providers implementation.\nSome options addresses:\n  - A UUID style string\n  - Support for predefined profiles QOS_S, QOS_M, QOS_L, and QOS_E\n  - A searchable descriptive name\nThe set of QoS Profiles that an operator is offering can be retrieved by means of the [QoS Profile API](link TBC).\n",
        max_length=256,
        min_length=3,
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
        ...,
        description="Identifier of this event, that must be unique in the source context.",
    )
    source: str = Field(
        ...,
        description="Identifies the context in which an event happened in the specific Provider Implementation.",
    )
    type: Type = Field(..., description="The type of the event.")
    specversion: Specversion = Field(
        ...,
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
        ...,
        description="Timestamp of when the occurrence happened. It must follow RFC 3339\n",
    )


class StatusInfo(Enum):
    NETWORK_TERMINATED = "NETWORK_TERMINATED"
    DELETE_REQUESTED = "DELETE_REQUESTED"


class NetworkAccessIdentifier(BaseModel):
    __root__: str = Field(
        ...,
        description="A public identifier addressing a subscription in a mobile network. In 3GPP terminology, it corresponds to the GPSI formatted with the External Identifier ({Local Identifier}@{Domain Identifier}). Unlike the telephone number, the network access identifier is not subjected to portability ruling in force, and is individually managed by each operator.",
        examples=["123456789@domain.com"],
    )


class PhoneNumber(BaseModel):
    __root__: str = Field(
        ...,
        pattern=r"^\+[1-9][0-9]{4,14}$",
        description="A public identifier addressing a telephone subscription. In mobile networks it corresponds to the MSISDN (Mobile Station International Subscriber Directory Number). In order to be globally unique it has to be formatted in international format, according to E.164 standard, prefixed with '+'.",
        examples=["+123456789"],
    )


class SingleIpv4Addr(BaseModel):
    __root__: IPv4Address = Field(
        ...,
        description="A single IPv4 address with no subnet mask",
        examples=["203.0.113.0"],
    )


class DeviceIpv6Address(BaseModel):
    __root__: IPv6Address = Field(
        ...,
        description="The device should be identified by the observed IPv6 address, or by any single IPv6 address from within the subnet allocated to the device (e.g. adding ::0 to the /64 prefix).\n",
        examples=["2001:db8:85a3:8d3:1319:8a2e:370:7344"],
    )


class Status(Enum):
    REQUESTED = "REQUESTED"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class StatusChanged(Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class ErrorInfo(BaseModel):
    status: int = Field(
        ..., description="HTTP status code returned along with this error response"
    )
    code: str = Field(..., description="Code given to this error")
    message: str = Field(..., description="Detailed error description")


class Data(BaseModel):
    provisioningId: ProvisioningId
    status: Optional[StatusChanged] = None
    statusInfo: Optional[StatusInfo] = None


class EventStatusChanged(CloudEvent):
    eventData: Data = Field(
        ..., description="Event details depending on the event type"
    )


class DeviceIpv4Addr1(BaseModel):
    publicAddress: SingleIpv4Addr
    privateAddress: SingleIpv4Addr
    publicPort: Optional[Port] = None


class DeviceIpv4Addr2(BaseModel):
    publicAddress: SingleIpv4Addr
    privateAddress: Optional[SingleIpv4Addr] = None
    publicPort: Port


class DeviceIpv4Addr(BaseModel):
    __root__: Union[DeviceIpv4Addr1, DeviceIpv4Addr2] = Field(
        ...,
        description="The device should be identified by either the public (observed) IP address and port as seen by the application server, or the private (local) and any public (observed) IP addresses in use by the device (this information can be obtained by various means, for example from some DNS servers).\n\nIf the allocated and observed IP addresses are the same (i.e. NAT is not in use) then  the same address should be specified for both publicAddress and privateAddress.\n\nIf NAT64 is in use, the device should be identified by its publicAddress and publicPort, or separately by its allocated IPv6 address (field ipv6Address of the Device object)\n\nIn all cases, publicAddress must be specified, along with at least one of either privateAddress or publicPort, dependent upon which is known. In general, mobile devices cannot be identified by their public IPv4 address alone.\n",
        examples=[{"publicAddress": "203.0.113.0", "publicPort": 59765}],
    )


class Device(BaseModel):
    phoneNumber: Optional[PhoneNumber] = None
    networkAccessIdentifier: Optional[NetworkAccessIdentifier] = None
    ipv4Address: DeviceIpv4Addr
    ipv6Address: DeviceIpv6Address


class BaseProvisioningInfo(BaseModel):
    device: Device
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


class UserPlaneNotificationData(BaseModel):
    temp: AnyHttpUrl
