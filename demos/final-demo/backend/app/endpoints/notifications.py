import json
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.models.truck import Truck
from app.schemas.subscriptions import (
    CloudEvent,
    GeofencingEventType,
    ReachabilityEventType,
)
from app.session import get_session
from app.socketio import SocketIODep

router = APIRouter()


@router.post("/notification/{id}", status_code=HTTPStatus.NO_CONTENT)
async def notification(
    notif: CloudEvent, id: int, sio: SocketIODep, db: Session = Depends(get_session)
):
    truck = db.get(Truck, id)
    if truck is None:
        return

    match notif.type:
        case (
            ReachabilityEventType.v0_reachability_data
            | ReachabilityEventType.v0_reachability_sms
        ):
            truck.isReachable = True
            await sio.emit(
                "reachability", json.dumps({"id": truck.id, "isReachable": True})
            )
        case ReachabilityEventType.v0_reachability_disconnected:
            truck.isReachable = False
            await sio.emit(
                "reachability", json.dumps({"id": truck.id, "isReachable": False})
            )
        case GeofencingEventType.v0_area_entered:
            truck.isQueued = True
            await sio.emit("queue", json.dumps({"id": truck.id, "isQueued": True}))
        case GeofencingEventType.v0_area_left:
            truck.isQueued = False
            await sio.emit("queue", json.dumps({"id": truck.id, "isQueued": False}))
        case _:
            return

    db.add(truck)
    db.commit()
