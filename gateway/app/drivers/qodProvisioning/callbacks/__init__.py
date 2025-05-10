from fastapi import APIRouter
from . import nef

router = APIRouter(prefix="/callbacks/v1")
router.include_router(nef.router)
