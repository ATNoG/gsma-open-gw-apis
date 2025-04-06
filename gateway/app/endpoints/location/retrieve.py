from fastapi import APIRouter
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

    loc = await location_interface.retrieve_location(
        device, body.maxAge, body.maxSurface
    )

    return loc
