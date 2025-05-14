from fastapi import Depends

from typing import Annotated

from app.drivers.nef_auth import NEFAuth
from app.settings import ReachabilityStatusBackend, settings
from app.interfaces.reachability_status import ReachabilityStatusInterface

from .nef import NefReachabilityStatusInterface

reachability_status_interface: ReachabilityStatusInterface
match settings.reachability_status.backend:
    case ReachabilityStatusBackend.Nef:
        nef_auth = NEFAuth(
            settings.nef_url, settings.nef_username, settings.nef_password
        )
        reachability_status_interface = NefReachabilityStatusInterface(
            settings.nef_url, nef_auth
        )


async def get_reachability_status_driver() -> ReachabilityStatusInterface:
    return reachability_status_interface


ReachabilityStatusInterfaceDep = Annotated[
    ReachabilityStatusInterface, Depends(get_reachability_status_driver)
]
