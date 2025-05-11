from typing import Annotated

from fastapi import Depends

from app.settings import QodProvisioningBackend, settings
from app.drivers.nef_auth import NEFAuth


from .nef import NEFQoDProvisioningInterface
from app.interfaces.qodProvisioning import QoDProvisioningInterface

qodProvisioning_interface: QoDProvisioningInterface
match settings.qod_provisioning.qod_provisioning_backend:
    case QodProvisioningBackend.Nef:
        nef_auth = NEFAuth(
            settings.nef_url, settings.nef_username, settings.nef_password
        )
        qod_provisioning_interface = NEFQoDProvisioningInterface(
            settings.nef_url, nef_auth
        )


def get_qodProvisioning_interface() -> QoDProvisioningInterface:
    return qod_provisioning_interface


QodProvisioningInterfaceDep = Annotated[
    QoDProvisioningInterface, Depends(get_qodProvisioning_interface)
]
