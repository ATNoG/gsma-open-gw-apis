from typing import List, Annotated
from fastapi import APIRouter, Path, Depends, HTTPException
from sqlmodel import Session, select

from app.models.truck import Truck
from app.session import get_session

router = APIRouter(prefix="/trucks")


@router.get("")
def list_all_trucks(db: Session = Depends(get_session)) -> List[Truck]:
    return db.exec(select(Truck)).all()


@router.get("/{id}")
def info_truck(
    truck_id: Annotated[int, Path(title="The id of the truck")],
    db: Session = Depends(get_session),
) -> Truck:
    truck = db.get(Truck, truck_id)
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


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
