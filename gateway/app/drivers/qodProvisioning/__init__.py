from app.settings import QodProvisioningBackend, settings
from app.drivers.nef_auth import NEFAuth


from app.interfaces.qodProvisioning import QoDProvisioningInterface

qodProvisioning_interface: QoDProvisioningInterface


def get_qodProvisioning_interface() -> QoDProvisioningInterface:
    return qod_provisioning_interface


match settings.qod_provisioning.qod_provisioning_backend:
    case QodProvisioningBackend.Nef:
        from .nef.nef_interface import NEFQoDProvisioningInterface

        nef_auth = NEFAuth(
            settings.nef_url, settings.nef_username, settings.nef_password
        )
        qod_provisioning_interface = NEFQoDProvisioningInterface(
            settings.nef_url, nef_auth
        )
