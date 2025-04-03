from fastapi import APIRouter

from app.settings import settings
from app.drivers.sms import SMSInterfaceDep
from app.drivers.otp import OTPInterfaceDep
from app.schemas.smsotp import SendCodeBody, SendCodeResponse

router = APIRouter()


@router.post("/send-code")
async def send_code(
    body: SendCodeBody, sms_interface: SMSInterfaceDep, otp_interface: OTPInterfaceDep
) -> SendCodeResponse:
    authentication_id = await otp_interface.generate_authentication_id()
    code = await otp_interface.generate_otp(settings.sms_otp.otp_code_size)
    message = body.message.replace("{{code}}", code)

    await otp_interface.store_otp(
        authentication_id,
        code,
        settings.sms_otp.max_attempts,
        settings.sms_otp.otp_expiry_secs,
    )

    await sms_interface.send_sms(body.phoneNumber, message)

    return SendCodeResponse(authenticationId=str(authentication_id))
