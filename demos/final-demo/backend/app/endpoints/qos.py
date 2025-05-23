from sqlmodel import Session
from fastapi import APIRouter, Depends
from http import HTTPStatus

from app.services.qos import QosService
from app.models.truck import Truck
from app.session import get_session

router = APIRouter()


@router.post("/increase-bandwidth/{id}", status_code=HTTPStatus.NO_CONTENT)
async def increase_bandwidth(id: int, db: Session = Depends(get_session)):
    service = QosService()
    truck = db.get(Truck, id)

    if truck is None:
        return

    await service.increase_bandwidth(truck)
