from fastapi import APIRouter

from . import (
    create_subscription,
    delete_subscription,
    get_subscriptions,
    get_subscriptions_by_id,
)

router = APIRouter(prefix="/device-roaming-status-subscriptions/v0.7")
router.include_router(get_subscriptions.router)
router.include_router(get_subscriptions_by_id.router)
router.include_router(delete_subscription.router)
router.include_router(create_subscription.router)
