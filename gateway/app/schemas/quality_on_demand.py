from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict, Field

from app.schemas import subscriptions
from app.schemas.device import Device, Port
from app.schemas.qodProvisioning import (
    QosProfileName,
    Status,
)
from app.schemas.subscriptions import SinkCredential


SessionId = Annotated[UUID, Field(description="Session ID in UUID format")]


class Range(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)
    from_: Annotated[Port, Field(alias="from")]
    to: Port


class StatusInfo(Enum):
    DURATION_EXPIRED = "DURATION_EXPIRED"
    NETWORK_TERMINATED = "NETWORK_TERMINATED"
    DELETE_REQUESTED = "DELETE_REQUESTED"


class PortsSpec(BaseModel):
    ranges: Annotated[
        Optional[List[Range]],
        Field(description="Range of TCP or UDP ports", min_length=1),
    ] = None
    ports: Annotated[
        Optional[List[Port]],
        Field(description="Array of TCP or UDP ports", min_length=1),
    ] = None


class ExtendSessionDuration(BaseModel):
    requestedAdditionalDuration: Annotated[
        int,
        Field(
            ge=1,
            description="Additional duration in seconds to be added to the current session duration. The overall session duration, including extensions, shall not exceed the maximum duration limit for the QoS Profile.\n",
            examples=[1800],
        ),
    ]


class NotificationEventType(str, Enum):
    org_camaraproject_quality_on_demand_v1_qos_status_changed = (
        "org.camaraproject.quality-on-demand.v1.qos-status-changed"
    )


class RetrieveSessionsInput(BaseModel):
    device: Optional[Device] = None


class ApplicationServer(BaseModel):
    ipv4Address: Annotated[
        Optional[str],
        Field(
            description="IPv4 address may be specified in form <address/mask> as:\n  - address - an IPv4 number in dotted-quad form 1.2.3.4. Only this exact IP number will match the flow control rule.\n  - address/mask - an IP number as above with a mask width of the form 1.2.3.4/24.\n    In this case, all IP numbers from 1.2.3.0 to 1.2.3.255 will match. The bit width MUST be valid for the IP version.",
            examples=["198.51.100.0/24"],
        ),
    ] = None
    ipv6Address: Annotated[
        Optional[str],
        Field(
            description="IPv6 address may be specified in form <address/mask> as:\n  - address - The /128 subnet is optional for single addresses:\n    - 2001:db8:85a3:8d3:1319:8a2e:370:7344\n    - 2001:db8:85a3:8d3:1319:8a2e:370:7344/128\n  - address/mask - an IP v6 number with a mask:\n    - 2001:db8:85a3:8d3::0/64\n    - 2001:db8:85a3:8d3::/64",
            examples=["2001:db8:85a3:8d3:1319:8a2e:370:7344"],
        ),
    ] = None


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
    qosStatus: Status
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


class EventQosStatus(Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class Data(BaseModel):
    sessionId: SessionId
    qosStatus: EventQosStatus
    statusInfo: Optional[StatusInfo] = None


CloudEvent = subscriptions.CloudEvent[NotificationEventType, Data]
