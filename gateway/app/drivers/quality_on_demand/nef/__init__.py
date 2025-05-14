from app.settings import settings
from app.drivers.nef_auth import NEFAuth

from .nef_interface import NEFQoDInterface

_nef_auth = NEFAuth(settings.nef_url, settings.nef_username, settings.nef_password)
nef_qod_provisioning_interface = NEFQoDInterface(settings.nef_url, _nef_auth)
