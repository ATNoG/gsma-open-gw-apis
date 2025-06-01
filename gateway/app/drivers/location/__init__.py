from fastapi import Depends

from typing import Annotated

from app.settings import LocationBackend, settings
from app.interfaces.location import LocationInterface


location_interface: LocationInterface
if settings.location.backend == LocationBackend.Mock:
    from .mock import MockLocationDriver

    location_interface = MockLocationDriver()
elif settings.location.backend == LocationBackend.Nef:
    from .nef import NEFDriver

    location_interface = NEFDriver(settings.location.nef)


async def get_location_driver() -> LocationInterface:
    return location_interface


LocationInterfaceDep = Annotated[LocationInterface, Depends(get_location_driver)]
