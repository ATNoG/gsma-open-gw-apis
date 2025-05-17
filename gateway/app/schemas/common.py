from typing import Annotated
from datetime import datetime

from pydantic import BaseModel, Field

PhoneNumber = Annotated[
    str,
    Field(
        pattern=r"^\+[1-9][0-9]{4,14}$",
        description="A public identifier addressing a telephone subscription. In mobile networks it corresponds to the MSISDN (Mobile Station International Subscriber Directory Number). In order to be globally unique it has to be formatted in international format, according to E.164 standard, prefixed with '+'.",
        examples=["+346661113334"],
    ),
]

NetworkAccessIdentifier = Annotated[
    str,
    Field(
        description="A public identifier addressing a subscription in a mobile network. In 3GPP terminology, it corresponds to the GPSI formatted with the External Identifier ({Local Identifier}@{Domain Identifier}). Unlike the telephone number, the network access identifier is not subjected to portability ruling in force, and is individually managed by each operator.",
        examples=["123456789@domain.com"],
    ),
]

Port = Annotated[int, Field(ge=0, le=65535, description="TCP or UDP port number")]

Latitude = Annotated[
    float,
    Field(
        ge=-90.0,
        le=90.0,
        description="Latitude component of a location.",
        examples=[50.735851],
    ),
]

Longitude = Annotated[
    float,
    Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude component of location.",
        examples=[7.10066],
    ),
]


class Point(BaseModel):
    latitude: Latitude
    longitude: Longitude


LastStatusTime = Annotated[
    datetime,
    Field(
        description="Last time that the associated device reachability status was updated",
        examples=["2024-02-20T10:41:38.657Z"],
    ),
]
