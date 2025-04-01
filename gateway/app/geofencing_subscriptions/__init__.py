from fastapi import APIRouter


from . import (
    post_subscriptions,
    get_subscriptions,
    get_subscriptions_by_id,
    delete_subscriptions_by_id,
)

router = APIRouter(prefix="/geofencing-subscriptions/v0.4rc1")
router.include_router(post_subscriptions.router)
router.include_router(get_subscriptions.router)
router.include_router(get_subscriptions_by_id.router)
router.include_router(delete_subscriptions_by_id.router)
