from fastapi import Depends

from typing import Annotated

from app.settings import RoamingStatusBackend, settings
from app.interfaces.roaming_status import RoamingStatusInterface

roaming_status_interface: RoamingStatusInterface
match settings.roaming_status.backend:
    case RoamingStatusBackend.Nef:
        from .nef import nef_roaming_status_interface

        roaming_status_interface = nef_roaming_status_interface


async def get_roaming_status_driver() -> RoamingStatusInterface:
    return roaming_status_interface


RoamingStatusInterfaceDep = Annotated[
    RoamingStatusInterface, Depends(get_roaming_status_driver)
]
