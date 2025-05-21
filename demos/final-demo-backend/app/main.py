import logging
import contextlib
from fastapi import FastAPI, Depends
from fastapi_socketio import SocketManager

from app.schemas.location import Point
from app.services.reachability import reachability_service
from app.services.location import location_service
from app.session import create_db_and_tables
from app import endpoints
from app.models.truck import Truck
from app.session import get_session
from sqlmodel import Session

app = FastAPI()
app.include_router(endpoints.router)
socket_manager = SocketManager(app=app)


@app.on_event("startup")
async def on_startup():
    get_db = contextlib.contextmanager(get_session)
    with get_db() as db:
        logging.warning("Initializing the tables")
        create_db_and_tables()

        trucks = [
            Truck(phoneNumber="+900000000"),
            Truck(phoneNumber="+900000001"),
        ]

        for truck in trucks:
            reachability = await reachability_service.reachability_retrieve(truck)
            in_queue = await location_service.location_verification(
                truck, Point(latitude=0, longitude=0), radius=10
            )
            truck.isQueued = in_queue
            truck.isReachable = reachability

            db.add(truck)
            db.commit()
