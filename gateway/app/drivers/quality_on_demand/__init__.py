from typing import Annotated

from fastapi import Depends

from app.interfaces.quality_on_demand import QoDInterface
from app.settings import QodBackend, settings
from app.interfaces.qodProvisioning import QoDProvisioningInterface

qod_provisioning_interface: QoDProvisioningInterface


match settings.qod_provisioning.qod_provisioning_backend:
    case QodBackend.Nef:
        from .nef import nef_qod_interface

        qod_interface = nef_qod_interface


def get_qod_interface() -> QoDInterface:
    return qod_provisioning_interface


QodInterfaceDep = Annotated[QoDProvisioningInterface, Depends(get_qod_interface)]
