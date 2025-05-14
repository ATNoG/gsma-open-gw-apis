from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field

from app.schemas.device import Device


SessionId = Annotated[UUID, Field(description="Session ID in UUID format")]

Port = Annotated[int, Field(ge=0, le=65535, description="TCP or UDP port number.")]

QosProfileName = Annotated[
    str,
    Field(
        pattern=r"^[a-zA-Z0-9_.-]+$",
        description="A unique name for identifying a specific QoS profile.\nThis may follow different formats depending on the API provider implementation.\nSome options addresses:\n  - A UUID style string\n  - Support for predefined profiles QOS_S, QOS_M, QOS_L, and QOS_E\n  - A searchable descriptive name\nThe set of QoS Profiles that an API provider is offering may be retrieved by means of the QoS Profile API (qos-profile) or agreed on onboarding time.\n",
        min_length=3,
        max_length=256,
        examples=["voice"],
    ),
]

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


class Range(BaseModel):
    from_: Annotated[Port, Field(alias="from")]
    to: Port


class PortsSpec(BaseModel):
    ranges: Annotated[
        Optional[List[Range]],
        Field(description="Range of TCP or UDP ports", min_length=1),
    ] = None
    ports: Annotated[
        Optional[List[Port]],
        Field(description="Array of TCP or UDP ports", min_length=1),
    ] = None


class CredentialType(Enum):
    PLAIN = "PLAIN"
    ACCESSTOKEN = "ACCESSTOKEN"
    REFRESHTOKEN = "REFRESHTOKEN"


class SinkCredential(BaseModel):
    credentialType: Annotated[
        CredentialType,
        Field(
            description="The type of the credential.\nNote: Type of the credential - MUST be set to ACCESSTOKEN for now\n",
        ),
    ]


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
            description="REQUIRED. An absolute (UTC) timestamp at which the token shall be considered expired. Token expiration should occur\nafter the termination of the requested session, allowing the client to be notified of any changes during the\nsessions's existence. If the token expires while the session is still active, the client will stop receiving notifications.\nIf the access token is a JWT and registered \"exp\" (Expiration Time) claim is present, the two expiry times should match.\nIt must follow [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339#section-5.6) and must have time zone.\nRecommended format is yyyy-MM-dd'T'HH:mm:ss.SSSZ (i.e. which allows 2023-07-03T14:27:08.312+02:00 or 2023-07-03T12:27:08.312Z)\n",
            examples=["2023-07-03T12:27:08.312Z"],
        ),
    ]
    accessTokenType: Annotated[
        AccessTokenType,
        Field(
            description="REQUIRED. Type of the access token (See [OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-7.1)). For the current version of the API the type MUST be set to `Bearer`.",
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


class ExtendSessionDuration(BaseModel):
    requestedAdditionalDuration: Annotated[
        int,
        Field(
            ge=1,
            description="Additional duration in seconds to be added to the current session duration. The overall session duration, including extensions, shall not exceed the maximum duration limit for the QoS Profile.\n",
            examples=[1800],
        ),
    ]


class Type(Enum):
    org_camaraproject_quality_on_demand_v1_qos_status_changed = (
        "org.camaraproject.quality-on-demand.v1.qos-status-changed"
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
            description="Identifies the context in which an event happened in the specific provider implementation.",
        ),
    ]
    type: Annotated[Type, Field(description="The type of the event.")]
    specversion: Annotated[
        Specversion,
        Field(
            description="Version of the specification to which this event conforms (must be 1.0 if it conforms to Cloudevents 1.0.2 version)",
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
    DURATION_EXPIRED = "DURATION_EXPIRED"
    NETWORK_TERMINATED = "NETWORK_TERMINATED"
    DELETE_REQUESTED = "DELETE_REQUESTED"


class QosStatus(Enum):
    REQUESTED = "REQUESTED"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class EventQosStatus(Enum):
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
    sessionId: SessionId
    qosStatus: EventQosStatus
    statusInfo: Optional[StatusInfo] = None


class EventQosStatusChanged(CloudEvent):
    eventData: Annotated[
        Data, Field(description="Event details depending on the event type")
    ]


class ApplicationServer(BaseModel):
    ipv4Address: Annotated[
        Optional[str],
        Field(
            description="IPv4 address may be specified in form <address/mask> as:\n  - address - an IPv4 number in dotted-quad form 1.2.3.4. Only this exact IP number will match the flow control rule.\n  - address/mask - an IP number as above with a mask width of the form 1.2.3.4/24.\n    In this case, all IP numbers from 1.2.3.0 to 1.2.3.255 will match. The bit width MUST be valid for the IP version.\n",
            examples=["198.51.100.0/24"],
        ),
    ] = None
    ipv6Address: Annotated[
        Optional[str],
        Field(
            description="IPv6 address may be specified in form <address/mask> as:\n  - address - The /128 subnet is optional for single addresses:\n    - 2001:db8:85a3:8d3:1319:8a2e:370:7344\n    - 2001:db8:85a3:8d3:1319:8a2e:370:7344/128\n  - address/mask - an IP v6 number with a mask:\n    - 2001:db8:85a3:8d3::0/64\n    - 2001:db8:85a3:8d3::/64\n",
            examples=["2001:db8:85a3:8d3:1319:8a2e:370:7344"],
        ),
    ] = None


class RetrieveSessionsInput(BaseModel):
    device: Optional[Device] = None


class BaseSessionInfo(BaseModel):
    device: Optional[Device] = None
    applicationServer: ApplicationServer
    devicePorts: Annotated[
        Optional[PortsSpec],
        Field(
            description="The ports used locally by the device for flows to which the requested QoS profile should apply. If omitted, then the qosProfile will apply to all flows between the device and the specified application server address and ports",
        ),
    ] = None
    applicationServerPorts: Annotated[
        Optional[PortsSpec],
        Field(
            description="A list of single ports or port ranges on the application server",
        ),
    ] = None
    qosProfile: QosProfileName
    sink: Annotated[
        Optional[AnyUrl],
        Field(
            description="The address to which events about all status changes of the session (e.g. session termination) shall be delivered using the selected protocol.",
            examples=["https://endpoint.example.com/sink"],
        ),
    ] = None
    sinkCredential: Annotated[
        Optional[SinkCredential],
        Field(
            description="A sink credential provides authentication or authorization information necessary to enable delivery of events to a target.",
        ),
    ] = None


class SessionInfo(BaseSessionInfo):
    sessionId: SessionId
    duration: Annotated[
        int,
        Field(
            ge=1,
            description='Session duration in seconds. Implementations can grant the requested session duration or set a different duration, based on network policies or conditions.\n- When `qosStatus` is "REQUESTED", the value is the duration to be scheduled, granted by the implementation.\n- When `qosStatus` is AVAILABLE", the value is the overall duration since `startedAt. When the session is extended, the value is the new overall duration of the session.\n- When `qosStatus` is "UNAVAILABLE", the value is the overall effective duration since `startedAt` until the session was terminated.\n',
            examples=[3600],
        ),
    ]
    startedAt: Annotated[
        Optional[datetime],
        Field(
            description='Date and time when the QoS status became "AVAILABLE". Not to be returned when `qosStatus` is "REQUESTED". Format must follow RFC 3339 and must indicate time zone (UTC or local).',
            examples=["2024-06-01T12:00:00Z"],
        ),
    ] = None
    expiresAt: Annotated[
        Optional[datetime],
        Field(
            description='Date and time of the QoS session expiration. Format must follow RFC 3339 and must indicate time zone (UTC or local).\n- When `qosStatus` is "AVAILABLE", it is the limit time when the session is scheduled to finnish, if not terminated by other means.\n- When `qosStatus` is "UNAVAILABLE", it is the time when the session was terminated.\n- Not to be returned when `qosStatus` is "REQUESTED".\nWhen the session is extended, the value is the new expiration time of the session.\n',
            examples=["2024-06-01T13:00:00Z"],
        ),
    ] = None
    qosStatus: QosStatus
    statusInfo: Optional[StatusInfo] = None


class CreateSession(BaseSessionInfo):
    duration: Annotated[
        int,
        Field(
            ge=1,
            description="Requested session duration in seconds. Value may be explicitly limited for the QoS profile, as specified in the Qos Profile (see qos-profile API). Implementations can grant the requested session duration or set a different duration, based on network policies or conditions.\n",
            examples=[3600],
        ),
    ]


RetrieveSessionsOutput = Annotated[
    List[SessionInfo],
    Field(description="QoS session information for a given device", min_length=0),
]
