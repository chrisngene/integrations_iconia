from fastapi import APIRouter, Depends, status, HTTPException
from api.routers.v1.vehicles_inspection import vehicles_inspection_repository as vi
from sqlalchemy.orm import Session
from api import service, database
from api.routers.v1.authentication.auth_outh2 import get_current_user
from typing import List

router = APIRouter(prefix="/api/v1/vehicles_inspection", tags=["Assets"])


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[service.VehiclesInspection]
)
def get_all_vehicles_inspections(
    current_user: service.User = Depends(get_current_user),
):
    return vi.get_all(current_user)


# Post vehicles recorded mileage to ERP
@router.post(
    "/create-inspection-log/{instance_id}", status_code=status.HTTP_201_CREATED
)
def create_vehicles_inspection(
    instance_id: int,
    db: Session = Depends(database.get_db),
):
    return vi.create(instance_id, db)
