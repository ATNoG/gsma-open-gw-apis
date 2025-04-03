import httpx
from pydantic import AnyHttpUrl
from urllib.parse import urlencode

from app.settings import settings
from app.interfaces.sms import SMSInterface


class SMSCSMSInterface(SMSInterface):
    def __init__(self, smsc_url: AnyHttpUrl) -> None:
        super().__init__()

        self.smsc_url = smsc_url
        self.httpx_client = httpx.AsyncClient()

    async def send_sms(self, msisdn: str, text: str) -> None:
        query = urlencode(
            {
                "msisdn": settings.sms_otp.sender_id,
                # Remove the plus sign as the SMSC doesn't expect a plus sign
                "to": msisdn.lstrip("+"),
                "text": text,
            }
        )
        await self.httpx_client.get(f"{self.smsc_url}?{query}")
