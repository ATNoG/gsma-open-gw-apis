# Types for Nnef_AFsessionWithQoS defined in TS 29.122

from ipaddress import IPv4Address, IPv6Address
from typing import Optional, List
from typing_extensions import Annotated
from pydantic import BaseModel, Field

from .commonData import (
    SupportedFeatures,
    Link,
    Gpsi,
    FlowInfo,
    UsageThreshold,
    UserPlaneEvent,
)


class AsSessionWithQoSSubscription(BaseModel):
    self: Optional[Link] = None
    supportedFeatures: Optional[SupportedFeatures] = None
    notificationDestination: Link
    gpsi: Optional[Gpsi] = None
    flowInfo: Annotated[
        Optional[List[FlowInfo]],
        Field(description="Describe the data flow which requires QoS.", min_length=1),
    ] = None
    qosReference: Annotated[
        Optional[str], Field(description="Identifies a pre-defined QoS information")
    ] = None
    ueIpv4Addr: Optional[IPv4Address] = None
    ueIpv6Addr: Optional[IPv6Address] = None
    usageThreshold: Optional[UsageThreshold] = None


class UserPlaneEventReport(BaseModel):
    event: UserPlaneEvent


class UserPlaneNotificationData(BaseModel):
    transaction: Link
    eventReports: Annotated[
        List[UserPlaneEventReport],
        Field(
            description="Contains the reported event and applicable information",
            min_length=1,
        ),
    ]
