from pydantic import BaseModel

from app.schemas.location import Point


class TruckResponse(BaseModel):
    id: int
    phoneNumber: str
    isQueued: bool
    isReachable: bool


class DetailedTruckResponse(BaseModel):
    id: int
    phoneNumber: str
    isQueued: bool
    isReachable: bool
    coords: Point
