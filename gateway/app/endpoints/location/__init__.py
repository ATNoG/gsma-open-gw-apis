from fastapi import APIRouter

from . import retrieve

router = APIRouter(prefix="/location-retrieval/v1")
router.include_router(retrieve.router)
