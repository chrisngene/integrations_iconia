from fastapi import APIRouter, Depends, status, HTTPException
from api.routers.v1.brand import brand_repository as vi
from sqlalchemy.orm import Session
from api import service, database
from api.routers.v1.authentication.auth_outh2 import get_current_user
from typing import List

router = APIRouter(prefix="/api/v1/brand", tags=["Brands"])


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[service.Brand]
)
def get_all_brands(
    current_user: service.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    return vi.get_all(current_user, db)


