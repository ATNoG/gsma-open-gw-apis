from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Annotated, List, Literal, Optional, Union

from pydantic import AnyHttpUrl, AnyUrl, BaseModel, ConfigDict, Field


class MonitoringType(str, Enum):
    LOCATION_REPORTING = "LOCATION_REPORTING"
    LOSS_OF_CONNECTIVITY = "LOSS_OF_CONNECTIVITY"
    UE_REACHABILITY = "UE_REACHABILITY"


class ReachabilityType(str, Enum):
    SMS = "SMS"
    DATA = "DATA"


class MonitoringEventSubscription(BaseModel):
    externalId: Optional[
        Annotated[
            str,
            Field(
                description="Globally unique identifier containing a Domain Identifier and a Local Identifier. <Local Identifier>@<Domain Identifier>",
                title="Externalid",
            ),
        ]
    ] = None
    msisdn: Optional[str] = None

    notificationDestination: Optional[
        Annotated[
            AnyUrl,
            Field(
                description="Reference resource (URL) identifying service consumer's endpoint, in order to receive the asynchronous notification.",
                title="Notificationdestination",
            ),
        ]
    ] = None

    monitoringType: MonitoringType

    maximumNumberOfReports: Optional[
        Annotated[
            int,
            Field(
                ge=1,
                description="Identifies the maximum number of event reports to be generated. Value 1 makes the Monitoring Request a One-time Request",
                title="Maximumnumberofreports",
            ),
        ]
    ] = None

    monitorExpireTime: Optional[
        Annotated[
            datetime,
            Field(
                description="Identifies the absolute time at which the related monitoring event request is considered to expire",
                title="Monitorexpiretime",
            ),
        ]
    ] = None

    self: Optional[AnyUrl] = None

    immediateRep: Optional[bool] = None

    addnMonTypes: Optional[List[MonitoringType]] = None
    reachabilityType: Optional[ReachabilityType] = None

    ipv4Addr: Optional[IPv4Address] = None
    ipv6Addr: Optional[IPv6Address] = None


class SupportedGADShapes(str, Enum):
    POINT = "POINT"
    POINT_UNCERTAINTY_CIRCLE = "POINT_UNCERTAINTY_CIRCLE"
    POINT_UNCERTAINTY_ELLIPSE = "POINT_UNCERTAINTY_ELLIPSE"
    POLYGON = "POLYGON"
    POINT_ALTITUDE = "POINT_ALTITUDE"
    POINT_ALTITUDE_UNCERTAINTY = "POINT_ALTITUDE_UNCERTAINTY"
    ELLIPSOID_ARC = "ELLIPSOID_ARC"
    LOCAL_2D_POINT_UNCERTAINTY_ELLIPSE = "LOCAL_2D_POINT_UNCERTAINTY_ELLIPSE"
    LOCAL_3D_POINT_UNCERTAINTY_ELLIPSOID = "LOCAL_3D_POINT_UNCERTAINTY_ELLIPSOID"
    DISTANCE_DIRECTION = "DISTANCE_DIRECTION"
    RELATIVE_2D_LOCATION_UNCERTAINTY_ELLIPSE = (
        "RELATIVE_2D_LOCATION_UNCERTAINTY_ELLIPSE"
    )
    RELATIVE_3D_LOCATION_UNCERTAINTY_ELLIPSOID = (
        "RELATIVE_3D_LOCATION_UNCERTAINTY_ELLIPSOID"
    )


class GeographicalCoordinates(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    lon: Annotated[float, Field(ge=-180.0, le=180.0, title="Lon")]
    lat: Annotated[float, Field(ge=-90.0, le=90.0, title="Lat")]


class Point(BaseModel):
    shape: Literal[SupportedGADShapes.POINT] = SupportedGADShapes.POINT
    point: GeographicalCoordinates


GeographicArea = Annotated[
    Union[Point],
    Field(description="Geographic area specified by different shape."),
]


class LocationInfo(BaseModel):
    geographicArea: Optional[GeographicArea] = None


class MonitoringEventReport(BaseModel):
    locationInfo: Optional[LocationInfo] = None
    monitoringType: MonitoringType
    reachabilityType: Optional[ReachabilityType] = None
    lossOfConnectReason: Annotated[
        Optional[int],
        Field(
            description='If "monitoringType" is "LOSS_OF_CONNECTIVITY", this parameter shall be included if available to identify the reason why loss of connectivity is reported. Refer to 3GPP TS 29.336 clause 8.4.58.',
        ),
    ] = None


class MonitoringNotification(BaseModel):
    subscription: Annotated[AnyHttpUrl, Field(title="Subscription endpoint")]
    monitoringEventReports: Optional[
        Annotated[
            List[MonitoringEventReport],
            Field(
                description="Monitoring event reports.",
                min_length=1,
                title="Monitoringeventreports",
            ),
        ]
    ] = None
