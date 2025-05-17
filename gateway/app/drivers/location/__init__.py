from fastapi import Depends

from typing import Annotated

from app.settings import LocationBackend, settings
from app.interfaces.location import LocationInterface

from .mock import MockLocationDriver
from .nef import NEFDriver

location_interface: LocationInterface
match settings.location.backend:
    case LocationBackend.Mock:
        location_interface = MockLocationDriver()
    case LocationBackend.Nef:
        location_interface = NEFDriver(settings.location.nef)


async def get_location_driver() -> LocationInterface:
    return location_interface


LocationInterfaceDep = Annotated[LocationInterface, Depends(get_location_driver)]
