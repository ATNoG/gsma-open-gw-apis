from fastapi import APIRouter, HTTPException
from http import HTTPStatus


router = APIRouter(prefix="/geofencing-subscriptions/v0.4rc1")


@router.get("/subscriptions")
def get_subscritpions() -> None:
    content = {
        "status": HTTPStatus.NOT_IMPLEMENTED,
        "code": "NOT_IMPLEMENTED",
        "message": "Endpoint not implemented",
    }
    raise HTTPException(status_code=HTTPStatus.NOT_IMPLEMENTED, detail=content)


@router.post("/subscriptions")
def post_subscriptions() -> None:
    content = {
        "status": HTTPStatus.NOT_IMPLEMENTED,
        "code": "NOT_IMPLEMENTED",
        "message": "Endpoint not implemented",
    }
    raise HTTPException(status_code=HTTPStatus.NOT_IMPLEMENTED, detail=content)


@router.get("/subscriptions/{subscription_id}")
def get_subscritpion_by_id(subscription_id: int) -> None:
    content = {
        "status": HTTPStatus.NOT_IMPLEMENTED,
        "code": "NOT_IMPLEMENTED",
        "message": "Endpoint not implemented",
    }
    raise HTTPException(status_code=HTTPStatus.NOT_IMPLEMENTED, detail=content)


@router.delete("/subscriptions/{subscription_id}")
def delete_subscritpion_by_id(subscription_id: int) -> None:
    content = {
        "status": HTTPStatus.NOT_IMPLEMENTED,
        "code": "NOT_IMPLEMENTED",
        "message": "Endpoint not implemented",
    }
    raise HTTPException(status_code=HTTPStatus.NOT_IMPLEMENTED, detail=content)
