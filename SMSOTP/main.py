from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import uuid
import re
from twilio.rest import Client
import redis
from app.main import app

app = FastAPI()

# Conectar ao Redis (por enquanto local)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def create_exception(status_code: int, code: str, message: str):
    return HTTPException(
        status_code=status_code,
        detail={
            "status": status_code,
            "code": code,
            "message": message
        }
    )

def validate_phone_number(phone_number: str) -> bool:
    return bool(re.match(r'^\+(\d{10,15})$', phone_number))

# Função para enviar o SMS via Twilio
def send_sms(phone_number: str, message: str):
    # Credenciais Twilio
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    from_number = '+351932619013'

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=from_number,
        to=phone_number
    )
    return message.sid

#Redis armazenar e obter
def store_code(phone_number: str, code: str):
    redis_client.setex(phone_number, 300, code)  # expira em 5 minutos

def get_code(phone_number: str) -> str:
    return redis_client.get(phone_number)

class PhoneNumberRequest(BaseModel):
    phoneNumber: str
    message: str

@app.post('/send-code')
def send_code(request: PhoneNumberRequest, x_correlator: str = Header(None)):
    phone_number = request.phoneNumber

    if not validate_phone_number(phone_number):
        raise create_exception(
            400,
            "INVALID_ARGUMENT",
            "Client specified an invalid argument. Ensure the phone number is valid, starting with '+' and followed by 10-15 digits."
        )
    
    # Verifica se a mensagem contém '{{code}}'
    if '{{code}}' not in request.message:
        raise create_exception(
            400,
            "INVALID_ARGUMENT",
            "Message must include '{{code}}'."
        )
    
    # Gerador de um código aleatório
    code = str(uuid.uuid4().hex[:6].upper())
    message = request.message.replace("{{code}}", code) 

    send_sms(phone_number, message)

    store_code(phone_number, code) #5 min de armazenamento

    authentication_id = str(uuid.uuid4())
    return {
        "authenticationId": authentication_id,
        "x-correlator": x_correlator,
        "message": "Code sent successfully."
    }

class ValidateCodeBody(BaseModel):
    authenticationId: str
    code: str
    phoneNumber: str

@app.post('/validate-code')
def validate_code(request: ValidateCodeBody, x_correlator: str = Header(None)):
    if not request.authenticationId or not request.code or not request.phoneNumber:
        raise create_exception(
            400,
            "INVALID_ARGUMENT",
            "Client specified an invalid range. Authentication ID, code, and phone number are required."
        )

    stored_code = get_code(request.phoneNumber)

    if stored_code is None:
        raise create_exception(
            400,
            "EXPIRED_CODE",
            "The code has expired or does not exist."
        )
    
    if stored_code.decode("utf-8") != request.code:
        raise create_exception(
            400,
            "INVALID_CODE",
            "The code provided is incorrect."
        )

    return {
        "message": "Code validated successfully.",
        "x-correlator": x_correlator
    }
