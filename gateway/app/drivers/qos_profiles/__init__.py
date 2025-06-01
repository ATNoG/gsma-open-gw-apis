from fastapi import Depends

from typing import Annotated

from app.settings import QoSProfilesBackend, settings
from app.interfaces.qos_profiles import QoSProfilesInterface

qos_profiles_interface: QoSProfilesInterface
if settings.qos_profiles.backend == QoSProfilesBackend.NEF:
    from .nef import NefQoSProfilesInterface

    qos_profiles_interface = NefQoSProfilesInterface(settings.qos_profiles.nef)


async def get_qos_profiles_driver() -> QoSProfilesInterface:
    return qos_profiles_interface


QoSProfilesInterfaceDep = Annotated[
    QoSProfilesInterface, Depends(get_qos_profiles_driver)
]
