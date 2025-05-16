from fastapi import Depends

from typing import Annotated

from app.settings import ReachabilityStatusBackend, settings
from app.interfaces.reachability_status import ReachabilityStatusInterface

reachability_status_interface: ReachabilityStatusInterface
match settings.reachability_status.backend:
    case ReachabilityStatusBackend.Nef:
        from .nef import nef_reachability_status_interface

        reachability_status_interface = nef_reachability_status_interface


async def get_reachability_status_driver() -> ReachabilityStatusInterface:
    return reachability_status_interface


ReachabilityStatusInterfaceDep = Annotated[
    ReachabilityStatusInterface, Depends(get_reachability_status_driver)
]
