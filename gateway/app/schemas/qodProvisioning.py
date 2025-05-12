from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field

from .device import Device

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


class CredentialType(Enum):
    PLAIN = "PLAIN"
    ACCESSTOKEN = "ACCESSTOKEN"
    REFRESHTOKEN = "REFRESHTOKEN"


class SinkCredential(BaseModel):
    credentialType: Annotated[
        Optional[CredentialType],
        Field(
            description="The type of the credential.\nNote: Type of the credential - MUST be set to ACCESSTOKEN for now.\n",
        ),
    ] = None


class PlainCredential(SinkCredential):
    identifier: Annotated[
        str, Field(description="The identifier might be an account or username.")
    ]
    secret: Annotated[
        str, Field(description="The secret might be a password or passphrase.")
    ]


class AccessTokenType(Enum):
    bearer = "bearer"


class AccessTokenCredential(SinkCredential):
    accessToken: Annotated[
        str,
        Field(
            description="REQUIRED. An access token is a previously acquired token granting access to the target resource.",
        ),
    ]
    accessTokenExpiresUtc: Annotated[
        datetime,
        Field(
            description="REQUIRED. An absolute (UTC) timestamp at which the token shall be considered expired. Token expiration should occur\nafter the termination of the requested provisioning, allowing the client to be notified of any changes during the\nprovisioning's existence. If the token expires while the provisioning is still active, the client will stop receiving notifications.\nIf the access token is a JWT and registered \"exp\" (Expiration Time) claim is present, the two expiry times should match.\nIt must follow [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339#section-5.6) and must have time zone.\nRecommended format is yyyy-MM-dd'T'HH:mm:ss.SSSZ (i.e. which allows 2023-07-03T14:27:08.312+02:00 or 2023-07-03T12:27:08.312Z)\n",
            examples=["2023-07-03T12:27:08.312Z"],
        ),
    ]
    accessTokenType: Annotated[
        AccessTokenType,
        Field(
            description="REQUIRED. Type of the access token (See [OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-7.1)).",
        ),
    ]


class RefreshTokenCredential(SinkCredential):
    accessToken: Annotated[
        str,
        Field(
            description="REQUIRED. An access token is a previously acquired token granting access to the target resource.",
        ),
    ]
    accessTokenExpiresUtc: Annotated[
        datetime,
        Field(
            description="REQUIRED. An absolute UTC instant at which the token shall be considered expired.",
        ),
    ]
    accessTokenType: Annotated[
        AccessTokenType,
        Field(
            description="REQUIRED. Type of the access token (See [OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-7.1)).",
        ),
    ]
    refreshToken: Annotated[
        str,
        Field(
            description="REQUIRED. An refresh token credential used to acquire access tokens.",
        ),
    ]
    refreshTokenEndpoint: Annotated[
        AnyUrl,
        Field(
            description="REQUIRED. A URL at which the refresh token can be traded for an access token.",
        ),
    ]


class Type(Enum):
    org_camaraproject_qod_provisioning_v0_status_changed = (
        "org.camaraproject.qod-provisioning.v0.status-changed"
    )


class Specversion(Enum):
    field_1_0 = "1.0"


class Datacontenttype(Enum):
    application_json = "application/json"


class CloudEvent(BaseModel):
    id: Annotated[
        str,
        Field(
            description="Identifier of this event, that must be unique in the source context.",
        ),
    ]
    source: Annotated[
        str,
        Field(
            description="Identifies the context in which an event happened in the specific Provider Implementation.",
        ),
    ]
    type: Annotated[Type, Field(description="The type of the event.")]
    specversion: Annotated[
        Specversion,
        Field(
            description="Version of the specification to which this event conforms (must be 1.0 if it conforms to cloudevents 1.0.2 version)",
        ),
    ]
    datacontenttype: Annotated[
        Optional[Datacontenttype],
        Field(
            description='media-type that describes the event payload encoding, must be "application/json" for CAMARA APIs',
        ),
    ] = None
    data: Annotated[
        Optional[Dict[str, Any]],
        Field(
            description="Event notification details payload, which depends on the event type",
        ),
    ] = None
    time: Annotated[
        datetime,
        Field(
            description="Timestamp of when the occurrence happened. It must follow RFC 3339\n",
        ),
    ]


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


class ErrorInfo(BaseModel):
    status: Annotated[
        int,
        Field(description="HTTP status code returned along with this error response"),
    ]
    code: Annotated[str, Field(description="Code given to this error")]
    message: Annotated[str, Field(description="Detailed error description")]


class Data(BaseModel):
    provisioningId: ProvisioningId
    status: Optional[StatusChanged] = None
    statusInfo: Optional[StatusInfo] = None


class EventStatusChanged(CloudEvent):
    eventdata: Annotated[
        Data, Field(description="Event details depending on the event type")
    ]


class BaseProvisioningInfo(BaseModel):
    device: Optional[Device]
    qosProfile: QosProfileName
    sink: Annotated[
        Optional[AnyUrl],
        Field(
            description="The address to which events shall be delivered using the selected protocol.",
            examples=["https://endpoint.example.com/sink"],
        ),
    ] = None
    sinkCredential: Optional[SinkCredential] = None


class ProvisioningInfo(BaseProvisioningInfo):
    provisioningId: ProvisioningId
    startedAt: Annotated[
        Optional[datetime],
        Field(
            description='Date and time when the provisioning became "AVAILABLE". Not to be returned when `status` is "REQUESTED". Format must follow RFC 3339 and must indicate time zone (UTC or local).',
            examples=["2024-06-01T12:00:00Z"],
        ),
    ] = None
    status: Status
    statusInfo: Optional[StatusInfo] = None


class TriggerProvisioning(BaseProvisioningInfo):
    pass


class RetrieveProvisioningByDevice(BaseModel):
    device: Optional[Device]
