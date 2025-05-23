from inspect import stack
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import auth
from app.schemas.auth import (
    CreateUserRequest,
    CreateUserResponse,
    LoginRequest,
    OtpRequest,
)
from app.models.auth import User, Logged
from app.session import get_session
from app.services.sms import sms_service

router = APIRouter(prefix="/auth")


@router.post("/register")
async def register(item_in: CreateUserRequest, db: Session = Depends(get_session)):
    authId = await sms_service.send_otp(item_in.phoneNumber)
    user = User(username=item_in.username, password=item_in.password, otpId=authId)
    db.add(user)
    db.commit()
    db.refresh(user)
    if user.id is None:
        raise HTTPException(status_code=500, detail="An error has occured")

    return CreateUserResponse(id=user.id, username=user.username)


@router.post("/verify")
async def verify(item_in: OtpRequest, db: Session = Depends(get_session)):
    user = db.get(User, item_in.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    valid = await sms_service.verify_otp(user.otpId, item_in.code)

    if valid:
        user.isVerified = True
        db.add(user)
        db.commit()


@router.post("/login")
def login(item_in: LoginRequest, db: Session = Depends(get_session)):
    stmt = (
        select(User)
        .where(User.username == item_in.username)
        .where(User.password == item_in.password)
        .where(User.isVerified)
    )
    user = db.exec(stmt).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id is None:
        raise HTTPException(status_code=500, detail="An error has occured")

    db.add(Logged(user=user.id, token=uuid4()))
    db.commit()
