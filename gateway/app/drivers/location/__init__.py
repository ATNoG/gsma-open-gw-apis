from fastapi import Depends

from typing import Annotated

from app.settings import LocationBackend, settings
from app.interfaces.location import LocationInterface

from .mock import MockLocationDriver
from .emulator import NEFEmulatorDriver

location_interface: LocationInterface
match settings.emulator.location_backend:
    case LocationBackend.Mock:
        location_interface = MockLocationDriver()
    case LocationBackend.NefEmulator:
        location_interface = NEFEmulatorDriver(settings.emulator.emulator_url)


async def get_location_driver() -> LocationInterface:
    return location_interface


LocationInterfaceDep = Annotated[LocationInterface, Depends(get_location_driver)]
