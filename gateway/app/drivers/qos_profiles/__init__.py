from fastapi import Depends

from typing import Annotated

from app.settings import QoSProfilesBackend, settings
from app.interfaces.qos_profiles import QoSProfilesInterface

from .nef import NefQoSProfilesInterface

qos_profiles_interface: QoSProfilesInterface
match settings.qos_profiles.backend:
    case QoSProfilesBackend.NEF:
        qos_profiles_interface = NefQoSProfilesInterface(settings.qos_profiles.nef)


async def get_qos_profiles_driver() -> QoSProfilesInterface:
    return qos_profiles_interface


QoSProfilesInterfaceDep = Annotated[
    QoSProfilesInterface, Depends(get_qos_profiles_driver)
]
