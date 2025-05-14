from datetime import datetime
from enum import Enum
from typing import Annotated, Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field

from .device import Device
import app.schemas.subscriptions as subscriptions

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


class NotificationEventType(str, Enum):
    org_camaraproject_qod_provisioning_v0_status_changed = (
        "org.camaraproject.qod-provisioning.v0.status-changed"
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


class CloudEventData(BaseModel):
    provisioningId: ProvisioningId
    status: Optional[StatusChanged] = None
    statusInfo: Optional[StatusInfo] = None


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
    sinkCredential: Optional[subscriptions.SinkCredential] = None


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


CloudEvent = subscriptions.CloudEvent[NotificationEventType, CloudEventData]
