import logging
from app.interfaces.sms import SMSInterface


class MockSMSInterface(SMSInterface):
    async def send_sms(self, msisdn: str, text: str) -> None:
        logging.info(f"Would send SMS to {msisdn}: {text}")
