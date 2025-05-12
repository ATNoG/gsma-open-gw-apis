from fastapi import Depends

from typing import Annotated

from app.settings import LocationBackend, settings
from app.drivers.nef_auth import NEFAuth
from app.interfaces.location import LocationInterface

from .mock import MockLocationDriver
from .nef import NEFDriver

location_interface: LocationInterface
match settings.location.backend:
    case LocationBackend.Mock:
        location_interface = MockLocationDriver()
    case LocationBackend.Nef:
        nef_auth = NEFAuth(
            settings.nef_url, settings.nef_username, settings.nef_password
        )

        location_interface = NEFDriver(settings.nef_url, nef_auth)


async def get_location_driver() -> LocationInterface:
    return location_interface


LocationInterfaceDep = Annotated[LocationInterface, Depends(get_location_driver)]
