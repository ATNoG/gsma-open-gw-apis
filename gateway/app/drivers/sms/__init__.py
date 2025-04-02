from fastapi import Depends

from typing import Annotated

from app.settings import SMSBackend, settings
from app.interfaces.sms import SMSInterface

from .mock import MockSMSInterface
from .smsc import SMSCSMSInterface

sms_interface: SMSInterface
match settings.sms_otp.backend:
    case SMSBackend.Mock:
        sms_interface = MockSMSInterface()
    case SMSBackend.SMSC:
        sms_interface = SMSCSMSInterface(settings.sms_otp.smsc_url)


async def get_sms_driver() -> SMSInterface:
    return sms_interface


SMSInterfaceDep = Annotated[SMSInterface, Depends(get_sms_driver)]
