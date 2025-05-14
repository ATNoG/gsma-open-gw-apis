from enum import Enum
from datetime import datetime
from typing import Annotated, Optional, List

from pydantic import Field, BaseModel

from .device import Device

LastStatusTime = Annotated[
    datetime,
    Field(
        description="Last time that the associated device reachability status was updated",
        examples=["2024-02-20T10:41:38.657Z"],
    ),
]


class ConnectivityType(Enum):
    DATA = "DATA"
    SMS = "SMS"


class ReachabilityStatusResponse(BaseModel):
    lastStatusTime: Optional[LastStatusTime] = None
    reachable: Annotated[
        bool, Field(description="Indicates overall device reachability")
    ]
    connectivity: Optional[List[ConnectivityType]] = None


class RequestReachabilityStatus(BaseModel):
    device: Optional[Device] = None
