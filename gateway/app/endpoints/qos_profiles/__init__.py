from fastapi import APIRouter

from . import fetch

router = APIRouter(prefix="/qos-profiles/v1")
router.include_router(fetch.router)
