from pydantic import BaseModel


class ReferencePositionWithConfidence(BaseModel):
    latitude: int
    """Latitude in degrees (-90 to 90) times 10^-7"""
    longitude: int
    """Longitude in degrees (-180 to 180) times 10^-7"""


class BasicContainer(BaseModel):
    referencePosition: ReferencePositionWithConfidence


class MCMMessageInner(BaseModel):
    basicContainer: BasicContainer


class MCMMessage(BaseModel):
    payload: MCMMessageInner


class CPMMessageInner(BaseModel):
    managementContainer: BasicContainer


class CPMMessage(BaseModel):
    cpm: CPMMessageInner
