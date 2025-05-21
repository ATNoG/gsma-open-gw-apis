from typing import Annotated

from fastapi import Depends

from app.services.location import LocationService

location_service = LocationService()


def get_location_service() -> LocationService:
    return location_service


LocationServiceDep = Annotated[LocationService, Depends(get_location_service)]
