from typing import Optional, Annotated, List

from pydantic import BaseModel, Field

from app.schemas.device import Device
from app.schemas.common import LastStatusTime

ActiveRoaming = Annotated[
    bool, Field(description="Roaming status. True, if it is roaming")
]

CountryCode = Annotated[
    int,
    Field(
        description="The Mobile country code (MCC) as an geographic region identifier for the country and the dependent areas.",
    ),
]
CountryName = Annotated[
    List[str],
    Field(
        description="The ISO 3166 ALPHA-2 country-codes of mapped to mobile country code(MCC). If there is mapping of one MCC to multiple countries, then we have list of countries. If there is no mapping of MCC to any country, then an empty array [] shall be returned..",
    ),
]


class RoamingStatusResponse(BaseModel):
    lastStatusTime: Optional[LastStatusTime] = None
    roaming: ActiveRoaming
    countryCode: Optional[CountryCode] = None
    countryName: Optional[CountryName] = None


class RoamingStatusRequest(BaseModel):
    device: Optional[Device] = None
