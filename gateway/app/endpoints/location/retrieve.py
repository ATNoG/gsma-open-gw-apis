from fastapi import APIRouter, HTTPException
from app.schemas.location import (
    RetrievalLocationRequest,
    Location,
)
from app.drivers.location import LocationInterfaceDep

router = APIRouter()


@router.post("/retrieve")
async def send_code(
    body: RetrievalLocationRequest, location_interface: LocationInterfaceDep
) -> Location:

    device = body.device

    if not device.phoneNumber:
        raise HTTPException(status_code=501, detail="Identifier not implemented")

    loc = await location_interface.retrieve_location(
        device, body.maxAge, body.maxSurface
    )

    return loc
