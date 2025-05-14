from fastapi import Depends

from typing import Annotated

from app.drivers.nef_auth import NEFAuth
from app.settings import QoSProfilesBackend, settings
from app.interfaces.qos_profiles import QoSProfilesInterface

from .nef import NefQoSProfilesInterface

qos_profiles_interface: QoSProfilesInterface
match settings.qos_profiles.backend:
    case QoSProfilesBackend.NEF:
        nef_auth = NEFAuth(
            settings.nef_url, settings.nef_username, settings.nef_password
        )
        qos_profiles_interface = NefQoSProfilesInterface(settings.nef_url, nef_auth)


async def get_qos_profiles_driver() -> QoSProfilesInterface:
    return qos_profiles_interface


QoSProfilesInterfaceDep = Annotated[
    QoSProfilesInterface, Depends(get_qos_profiles_driver)
]
