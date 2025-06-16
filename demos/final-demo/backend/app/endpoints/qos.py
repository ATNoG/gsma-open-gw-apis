from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.models.truck import Truck
from app.services.qos import QosService
from app.session import get_session

router = APIRouter()


async def increase_bandwidth(id: int):
    db = next(get_session())
    service = QosService()
    truck = db.get(Truck, id)
    await service.increase_bandwidth(truck)


async def decrease_bandwidth(id: int):
    db = next(get_session())
    service = QosService()
    truck = db.get(Truck, id)
    await service.decrease_bandwidth(truck)
