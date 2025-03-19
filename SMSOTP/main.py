from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import uuid
app = FastAPI()

class PhoneNumberRequest(BaseModel):
    phoneNumber: str
    message: str


@app.post('/send-code')
def validate(request: PhoneNumberRequest, x_correlator: str = Header(None)):
    phone_number = request.phoneNumber

    if not (phone_number.startswith('+') and phone_number[1:].isdigit() and len(phone_number) > 10):
        raise HTTPException(
            status_code=400,
            detail={
                "status": 400,
                "code": "INVALID_ARGUMENT",
                "message": "Client specified an invalid argument, request body or query param."
            }
        )
    
    if '{{code}}' not in request.message:
        raise HTTPException(
            status_code=400,
            detail={
                "status": 400,
                "code": "INVALID_ARGUMENT",
                "message": "Message must include '{{code}}'."
            }
        )

    return {
        "authenticationId": str(uuid.uuid4()),
        "x-correlator": x_correlator
    }


class ValidateCodeBody(BaseModel):
    authenticationId: str
    code: str

@app.post('/validate-code')
def validate_code(request: ValidateCodeBody, x_correlator: str = Header(None)):
    if not request.authenticationId or not request.code:
        raise HTTPException(
            status_code=400,
            detail={
                "status": 400,
                "code": "INVALID_ARGUMENT",
                "message": "Client specified an invalid range"
            }
        )

    return {
        "message": "Code validated successfully.",
        "x-correlator": x_correlator
    }
