from app.settings import settings

from .nef_interface import NEFQoDInterface

nef_qod_interface = NEFQoDInterface(settings.qod.nef, str(settings.gateway_public_url))
