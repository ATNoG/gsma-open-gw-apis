from typing import Annotated

from fastapi import Depends

from .provisioning import QoDProvisioningInterface
from app.interfaces.qodProvisioning import QoDProvisioningAbstractInterface

qodProvisioning_interface: QoDProvisioningAbstractInterface = QoDProvisioningInterface()


def get_qodProvisioning_interface() -> QoDProvisioningAbstractInterface:
    return qodProvisioning_interface


qodProvisioningInterfaceDep = Annotated[
    QoDProvisioningAbstractInterface, Depends(get_qodProvisioning_interface)
]
