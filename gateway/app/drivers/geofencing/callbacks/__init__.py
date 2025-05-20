import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import APIRouter, FastAPI

from app.drivers.geofencing.nef import nef_geofencing_subscription_interface
from app.settings import GeofencingBackend, settings

from .nef import router as nef_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(nef_geofencing_subscription_interface.clear_loop())

    yield

    task.cancel()


router: APIRouter
match settings.geofencing.backend:
    case GeofencingBackend.NEF:
        router = APIRouter(prefix="/callbacks/v1", lifespan=lifespan)
        router.include_router(nef_router)
