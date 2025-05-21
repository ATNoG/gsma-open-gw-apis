from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select

from app.models.truck import Truck
from app.schemas.truck import DetailedTruckResponse, TruckResponse
from app.services import LocationServiceDep
from app.session import get_session

router = APIRouter(prefix="/trucks")


@router.get("")
def list_all_trucks(db: Session = Depends(get_session)) -> List[TruckResponse]:
    return [
        TruckResponse(
            id=truck.id,
            phoneNumber=truck.phoneNumber,
            isReachable=truck.isReachable,
            isQueued=truck.isQueued,
        )
        for truck in db.exec(select(Truck)).all()
        if truck.id is not None
    ]


@router.get("/{truckId}")
async def info_truck(
    truckId: Annotated[int, Path(title="The id of the truck")],
    location_service: LocationServiceDep,
    db: Session = Depends(get_session),
) -> DetailedTruckResponse:
    truck = db.get(Truck, truckId)
    if truck is None or truck.id is None:
        raise HTTPException(status_code=404, detail="Truck not found")

    coords = await location_service.location_retrieval(truck)

    return DetailedTruckResponse(
        id=truck.id,
        phoneNumber=truck.phoneNumber,
        isQueued=truck.isQueued,
        isReachable=truck.isReachable,
        coords=coords,
    )


@router.post("/")
def create_truck(item_in: Truck, db: Session = Depends(get_session)) -> Truck:
    db.add(item_in)
    db.commit()
    db.refresh(item_in)
    return item_in


@router.delete("/{truck_id}")
def delete_truck(
    truck_id: Annotated[int, Path(title="The id of the truck")],
    db: Session = Depends(get_session),
) -> Truck:
    truck = db.get(Truck, truck_id)
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    db.delete(truck)
    db.commit()
    return truck
