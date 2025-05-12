from fastapi import APIRouter

from . import retrieve

router = APIRouter(prefix="/location-retrieval/v0.4")
router.include_router(retrieve.router)
