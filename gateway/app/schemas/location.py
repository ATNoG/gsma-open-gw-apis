from datetime import datetime
from enum import Enum
from typing import Annotated, Optional, Self

from pydantic import BaseModel, Field, SerializeAsAny, model_validator

from app.schemas.common import Point
from app.schemas.device import Device


class AreaType(Enum):
    CIRCLE = "CIRCLE"
    POLYGON = "POLYGON"


class Area(BaseModel):
    areaType: AreaType


PointList = Annotated[
    list[Point],
    Field(min_length=3, max_length=15, description="List of points defining a polygon"),
]


class Polygon(Area):
    boundary: PointList
    areaType: AreaType = AreaType.POLYGON


class Circle(Area):
    center: Point
    radius: Annotated[
        float, Field(ge=1, description="Distance from the center in meters")
    ]
    areaType: AreaType = AreaType.CIRCLE


class Location(BaseModel):
    lastLocationTime: Annotated[
        datetime,
        Field(
            description="Last date and time when the device was localized. It must follow RFC 3339 and must have time zone. Recommended format is yyyy-MM-dd'T'HH:mm:ss.SSSZ (i.e. which allows 2023-07-03T14:27:08.312+02:00 or 2023-07-03T12:27:08.312Z)"
        ),
    ]
    area: SerializeAsAny[Area]


class RetrievalLocationRequest(BaseModel):
    device: Device
    maxAge: Annotated[
        Optional[int],
        'Maximum age of the location information which is accepted for the location retrieval (in seconds). Absence of maxAge means "any age" and maxAge=0 means a fresh calculation.',
    ] = None
    maxSurface: Annotated[
        Optional[int],
        Field(
            ge=1,
            description='Maximum surface in square meters which is accepted by the client for the location retrieval. Absence of maxSurface means "any surface size".',
        ),
    ] = None


class VerifyLocationRequest(BaseModel):
    device: Device
    area: Circle
    maxAge: Annotated[
        Optional[int],
        'Maximum age of the location information which is accepted for the location retrieval (in seconds). Absence of maxAge means "any age" and maxAge=0 means a fresh calculation.',
    ] = None


class VerificationResult(Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


class VerifyLocationResponse(BaseModel):
    lastLocationTime: Annotated[
        datetime,
        Field(
            description="Last date and time when the device was localized. It must follow RFC 3339 and must have time zone. Recommended format is yyyy-MM-dd'T'HH:mm:ss.SSSZ (i.e. which allows 2023-07-03T14:27:08.312+02:00 or 2023-07-03T12:27:08.312Z)"
        ),
    ]
    verificationResult: VerificationResult
    matchRate: Annotated[
        Optional[int],
        Field(
            ge=1,
            le=99,
            description="Estimation of the match rate between the area in the request (R), and area where the network locates the device (N), calculated as the percent value of the intersection of both areas divided by the network area, that is (R ∩ N) / N * 100. Included only if VerificationResult is PARTIAL.",
        ),
    ] = None

    @model_validator(mode="after")
    def check_field(self) -> Self:
        if (
            self.verificationResult == VerificationResult.PARTIAL
            and self.matchRate is None
        ):
            raise ValueError("Partial values must contain a match rate")

        if (
            self.matchRate is not None
            and self.verificationResult != VerificationResult.PARTIAL
        ):
            raise ValueError("Only partial values can contain a match rate")

        return self
