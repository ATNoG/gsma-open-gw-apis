from abc import ABC, abstractmethod


class SMSInterface(ABC):
    @abstractmethod
    async def send_sms(self, msisdn: str, text: str) -> None:
        pass
