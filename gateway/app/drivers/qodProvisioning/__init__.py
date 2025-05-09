from typing import Annotated

from fastapi import Depends

from .nef import NEFQoDProvisioningInterface
from app.interfaces.qodProvisioning import QoDProvisioningInterface

qodProvisioning_interface: QoDProvisioningInterface = NEFQoDProvisioningInterface()


def get_qodProvisioning_interface() -> QoDProvisioningInterface:
    return qodProvisioning_interface


qodProvisioningInterfaceDep = Annotated[
    QoDProvisioningInterface, Depends(get_qodProvisioning_interface)
]
