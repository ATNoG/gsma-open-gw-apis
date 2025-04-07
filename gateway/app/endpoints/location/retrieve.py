from fastapi import APIRouter
from app.schemas.location import (
    RetrievalLocationRequest,
    Location,
)
from app.drivers.location import LocationInterfaceDep

router = APIRouter(prefix="/location-retrieval/v0.4")


@router.post("/retrieve")
async def retrieve_location(
    body: RetrievalLocationRequest, location_interface: LocationInterfaceDep
) -> Location:
    device = body.device

    return await location_interface.retrieve_location(
        device, body.maxAge, body.maxSurface
    )
