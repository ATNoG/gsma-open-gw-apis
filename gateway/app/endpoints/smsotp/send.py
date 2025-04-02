from fastapi import APIRouter

import os
import base64
from uuid import UUID

from app.settings import settings
from app.drivers.sms import SMSInterfaceDep
from app.schemas.smsotp import SendCodeBody, SendCodeResponse

router = APIRouter()


def generate_otp_code(code_size: int) -> str:
    # Each base32 letter has 5 bits of information, so in order to obtain
    # a code with size N, ceil(5/8 * N) = ((5 * N) + 7) // 8
    needed_bytes = ((5 * code_size) + 7) // 8
    random_data = os.urandom(needed_bytes)
    raw_code = base64.b32hexencode(random_data).decode("utf-8")
    # Codes might have 1 character more than the requested size, so truncate it
    return raw_code[:code_size]


@router.post("/send-code")
async def send_code(
    body: SendCodeBody, sms_interface: SMSInterfaceDep
) -> SendCodeResponse:
    # SAFETY: urandom generates cryptographically secure randomness, and with 16
    #         bytes, the risk of collision is acceptable.
    authenticationId = UUID(bytes=os.urandom(16), version=4)

    code = generate_otp_code(settings.sms_otp.otp_code_size)
    message = body.message.replace("{{code}}", code)

    # TODO: Store OTP data

    await sms_interface.send_sms(body.phoneNumber, message)

    return SendCodeResponse(authenticationId=str(authenticationId))
