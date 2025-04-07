from fastapi import APIRouter, HTTPException
from app.schemas.location import (
    RetrievalLocationRequest,
    Location,
)
from app.drivers.location import LocationInterfaceDep

router = APIRouter(prefix="/location-retrieval/v1")


@router.post("/retrieve")
async def retrieve_location(
    body: RetrievalLocationRequest, location_interface: LocationInterfaceDep
) -> Location:
    device = body.device

    loc = await location_interface.retrieve_location(
        device, body.maxAge, body.maxSurface
    )

    return loc
