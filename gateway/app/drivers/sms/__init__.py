from fastapi import Depends

from typing import Annotated

from app.settings import SMSBackend, settings
from app.interfaces.sms import SMSInterface

sms_interface: SMSInterface
if settings.sms_otp.sms_backend == SMSBackend.Mock:
    from .mock import MockSMSInterface

    sms_interface = MockSMSInterface()
elif settings.sms_otp.sms_backend == SMSBackend.SMSC:
    from .smsc import SMSCSMSInterface

    sms_interface = SMSCSMSInterface(
        settings.sms_otp.smsc_url, settings.sms_otp.sender_id
    )


async def get_sms_driver() -> SMSInterface:
    return sms_interface


SMSInterfaceDep = Annotated[SMSInterface, Depends(get_sms_driver)]
