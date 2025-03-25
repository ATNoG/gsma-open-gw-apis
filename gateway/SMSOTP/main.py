import re
import uuid
import requests
from fastapi import APIRouter, HTTPException, Header
from http import HTTPStatus
from pydantic import BaseModel

router = APIRouter(prefix="/one-time-password-sms/v1.1.0-rc.1")

# Simulação de armazenamento do código temporário (substituir por Redis ou banco de dados)
code_storage = {}

def store_code(phone_number: str, code: str):
    code_storage[phone_number] = code

def get_code(phone_number: str):
    return code_storage.get(phone_number)

api_key = "SUA_CHAVE_DE_API" #por agora não implementado

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
    return bool(re.match(r'^\+\d{10,15}$', phone_number))

def send_sms_via_gateway(phone_number: str, message: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": phone_number,
        "message": message,
        "sender": "+351932619013"
    }

    # Substituir pela URL correta da API de envio de SMS
    sms_gateway_url = "https://api.sms-gateway.com/send"

    response = requests.post(sms_gateway_url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Falha ao enviar mensagem. Status code: {response.status_code}, Erro: {response.text}")

    return response.json()

def send_sms(phone_number: str, message: str):
    return send_sms_via_gateway(phone_number, message)

class PhoneNumberRequest(BaseModel):
    phoneNumber: str
    message: str

@router.post('/send-code')
def send_code(request: PhoneNumberRequest, x_correlator: str = Header(None)):
    phone_number = request.phoneNumber

    if not validate_phone_number(phone_number):
        raise create_exception(
            400,
            "INVALID_ARGUMENT",
            "Número de telefone inválido. Deve começar com '+' seguido de 10 a 15 dígitos."
        )

    if '{{code}}' not in request.message:
        raise create_exception(
            400,
            "INVALID_ARGUMENT",
            "A mensagem deve conter '{{code}}'."
        )

    code = str(uuid.uuid4().hex[:6].upper())
    message = request.message.replace("{{code}}", code)

    send_sms(phone_number, message)
    store_code(phone_number, code)

    authentication_id = str(uuid.uuid4())
    return {
        "authenticationId": authentication_id,
        "x-correlator": x_correlator,
        "message": "Código enviado com sucesso."
    }

class ValidateCodeBody(BaseModel):
    authenticationId: str
    code: str
    phoneNumber: str

@router.post('/validate-code')
def validate_code(request: ValidateCodeBody, x_correlator: str = Header(None)):
    if not request.authenticationId or not request.code or not request.phoneNumber:
        raise create_exception(
            400,
            "INVALID_ARGUMENT",
            "Authentication ID, código e número de telefone são obrigatórios."
        )

    stored_code = get_code(request.phoneNumber)

    if stored_code is None:
        raise create_exception(
            400,
            "EXPIRED_CODE",
            "O código expirou ou não existe."
        )

    if stored_code != request.code:
        raise create_exception(
            400,
            "INVALID_CODE",
            "O código fornecido está incorreto."
        )

    return {
        "message": "Código validado com sucesso.",
        "x-correlator": x_correlator
    }
