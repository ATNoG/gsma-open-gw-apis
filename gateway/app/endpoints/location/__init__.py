from fastapi import APIRouter

from . import retrieve, verify

router = APIRouter()
router.include_router(retrieve.router)
router.include_router(verify.router)
