from logging import error
from fastapi import HTTPException, status
import httpx
from app.models import auth
from app.settings import settings


class SmsService:
    def __init__(self) -> None:
        self.httpx_client = httpx.AsyncClient(base_url=str(settings.gateway_url))

    async def send_otp(self, phoneNumber: str) -> str:
        data = {
            "phoneNumber": phoneNumber,
            "message": "Your authentication code is {{code}}",
        }

        doc = await self.httpx_client.post(
            "/one-time-password-sms/v1/send-code", json=data
        )

        if not doc.is_success:
            raise HTTPException(
                status_code=503, detail="Could not send the Authentication Code"
            )

        return doc.json().get("authenticationId")

    async def verify_otp(self, authenticationId: str, code: str) -> bool:
        data = {"authenticationId": authenticationId, "code": code}
        doc = await self.httpx_client.post(
            "/one-time-password-sms/v1/validate-code", json=data
        )

        if doc.is_success:
            return True

        raise HTTPException(status_code=400, detail=doc.json().get("message"))


sms_service = SmsService()
