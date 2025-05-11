from typing import Annotated

from fastapi import Depends

from app.settings import settings
from app.drivers.nef_auth import NEFAuth


from .nef import NEFQoDProvisioningInterface
from app.interfaces.qodProvisioning import QoDProvisioningInterface

nef_auth = NEFAuth(settings.nef_url, settings.nef_username, settings.nef_password)
qodProvisioning_interface: QoDProvisioningInterface = NEFQoDProvisioningInterface(
    settings.nef_url, nef_auth
)


def get_qodProvisioning_interface() -> QoDProvisioningInterface:
    return qodProvisioning_interface


qodProvisioningInterfaceDep = Annotated[
    QoDProvisioningInterface, Depends(get_qodProvisioning_interface)
]
