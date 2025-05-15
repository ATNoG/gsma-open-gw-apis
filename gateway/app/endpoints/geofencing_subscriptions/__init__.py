from fastapi import APIRouter

from . import (
    create_subscription,
    delete_subscription,
    get_subscriptions,
    get_subscriptions_by_id,
)

router = APIRouter(prefix="/geofencing-subscriptions/v0.4")
router.include_router(get_subscriptions.router)
router.include_router(get_subscriptions_by_id.router)
router.include_router(delete_subscription.router)
router.include_router(create_subscription.router)
