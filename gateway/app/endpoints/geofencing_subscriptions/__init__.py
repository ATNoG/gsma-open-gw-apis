from fastapi import APIRouter

from . import (
    get_subscriptions,
    get_subscriptions_by_id,
    delete_subscription,
    create_subscription,
)

router = APIRouter(prefix="/geofencing-subscriptions/v0")
router.include_router(get_subscriptions.router)
router.include_router(get_subscriptions_by_id.router)
router.include_router(delete_subscription.router)
router.include_router(create_subscription.router)
