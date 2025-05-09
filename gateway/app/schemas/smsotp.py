from typing import Annotated
from pydantic import BaseModel, Field

from .common import PhoneNumber

Message = Annotated[
    str,
    Field(
        pattern=r".*\{\{code\}\}.*",
        max_length=160,
        description="Message template used to compose the content of the SMS sent to the phone number. It must include the following label indicating where to include the short code `{{code}}`",
        examples=["{{code}} is your short code to authenticate with Cool App via SMS"],
    ),
]

AuthenticationId = Annotated[
    str,
    Field(
        max_length=36,
        description="unique id of the verification attempt the code belongs to.",
        examples=["ea0840f3-3663-4149-bd10-c7c6b8912105"],
    ),
]

Code = Annotated[
    str,
    Field(
        max_length=10,
        description="temporal, short code to be validated",
        examples=["AJY3"],
    ),
]


class SendCodeBody(BaseModel):
    phoneNumber: PhoneNumber
    message: Message


class SendCodeResponse(BaseModel):
    authenticationId: AuthenticationId


class ValidateCodeBody(BaseModel):
    authenticationId: AuthenticationId
    code: Code
