from enum import verify
from fastapi import APIRouter, HTTPException
from geopy import distance

from app.drivers.location import LocationInterfaceDep
from app.schemas.location import (
    VerifyLocationRequest,
    VerifyLocationResponse,
    AreaType,
    VerificationResult,
)

router = APIRouter(prefix="/location-verification/v1")


@router.post("/verify")
async def retrieve_location(
    body: VerifyLocationRequest, location_interface: LocationInterfaceDep
) -> VerifyLocationResponse:

    loc = await location_interface.retrieve_location(body.device, body.maxAge, 3)

    print(loc)

    if not loc:
        return VerifyLocationResponse(
            lastLocationTime=loc.lastLocationTime,
            verificationResult=VerificationResult.UNKNOWN,
        )

    if loc.area.areaType != AreaType.CIRCLE:
        raise HTTPException(status_code=501, detail="Area Type not implemented")

    pt1 = [loc.area.center.latitude, loc.area.center.longitude]
    pt2 = [body.area.center.latitude, loc.area.center.longitude]
    d = distance.distance(pt1, pt2).m

    if d <= body.area.radius:
        return VerifyLocationResponse(
            lastLocationTime=loc.lastLocationTime,
            verificationResult=VerificationResult.TRUE,
        )

    return VerifyLocationResponse(
        lastLocationTime=loc.lastLocationTime,
        verificationResult=VerificationResult.FALSE,
    )
