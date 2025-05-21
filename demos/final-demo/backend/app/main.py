import contextlib
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from socketio import ASGIApp
from starlette.types import Lifespan

from app import endpoints
from app.models.truck import Truck
from app.schemas.location import Point
from app.services.location import location_service
from app.services.reachability import reachability_service
from app.session import create_db_and_tables, get_session
from app.socketio import sio

logging.basicConfig(level="DEBUG")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logging.warning("Initializing the tables")
    create_db_and_tables()
    trucks = [
        Truck(phoneNumber="+900000000"),
        Truck(phoneNumber="+900000001"),
    ]
    reachability_subscriptions = []
    geofencing_subscriptions = []

    with next(get_session()) as db:
        for truck in trucks:
            reachability = await reachability_service.reachability_retrieve(truck)
            in_queue = await location_service.location_verification(
                truck, Point(latitude=0, longitude=0), radius=10
            )
            truck.isQueued = in_queue
            truck.isReachable = reachability

            db.add(truck)
            db.commit()

            reachability_subscriptions.extend(
                await reachability_service.reachability_subscription(truck)
            )
            geofencing_subscriptions.extend(
                await location_service.geofencing_subscription(
                    truck, Point(latitude=0, longitude=0), radius=10
                )
            )

    yield

    for sub in reachability_subscriptions:
        sub_id = sub["id"]

        await reachability_service.delete_reachability_subscription(sub_id)

    for sub in geofencing_subscriptions:
        sub_id = sub["id"]

        await location_service.delete_geofencing_subscription(sub_id)


app = FastAPI(lifespan=lifespan)
app.include_router(endpoints.router)
app.mount("/", ASGIApp(sio))
