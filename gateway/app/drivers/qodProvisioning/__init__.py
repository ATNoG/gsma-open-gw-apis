from typing import Annotated

from fastapi import Depends

from app.settings import QodProvisioningBackend, settings
from app.interfaces.qodProvisioning import QoDProvisioningInterface

qod_provisioning_interface: QoDProvisioningInterface


match settings.qod_provisioning.backend:
    case QodProvisioningBackend.Nef:
        from .nef import nef_qod_provisioning_interface

        qod_provisioning_interface = nef_qod_provisioning_interface


def get_qod_provisioning_interface() -> QoDProvisioningInterface:
    return qod_provisioning_interface


QodProvisioningInterfaceDep = Annotated[
    QoDProvisioningInterface, Depends(get_qod_provisioning_interface)
]
