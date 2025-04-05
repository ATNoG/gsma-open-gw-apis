from enum import Enum
from typing import Annotated, override
from pydantic import BaseModel, Field, SerializeAsAny
from datetime import datetime

from app.schemas.device import Device


class AreaType(Enum):
    CIRCLE = "CIRCLE"
    POLYGON = "POLYGON"


class Area(BaseModel):
    areaType: AreaType


Latitude = Annotated[
    float, Field(ge=-90, le=90, description="Latitude component of a location")
]
Longitude = Annotated[
    float, Field(ge=-90, le=90, description="Longitude component of a location")
]


class Point(BaseModel):
    latitude: Latitude
    longitude: Longitude


PointList = Annotated[
    list[Point],
    Field(min_length=3, max_length=15, description="List of points defining a polygon"),
]


class Polygon(Area):
    boundary: PointList

    def __init__(self, **data) -> None:
        super().__init__(areaType=AreaType.POLYGON, **data)


@override
class Circle(Area):
    center: Point
    radius: Annotated[
        float, Field(ge=1, description="Distance from the center in meters")
    ]

    def __init__(self, **data) -> None:
        super().__init__(**data, areaType=AreaType.CIRCLE)


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
        int,
        'Maximum age of the location information which is accepted for the location retrieval (in seconds). Absence of maxAge means "any age" and maxAge=0 means a fresh calculation.',
    ]
    maxSurface: Annotated[
        int,
        Field(
            ge=1,
            description='Maximum surface in square meters which is accepted by the client for the location retrieval. Absence of maxSurface means "any surface size".',
        ),
    ]
