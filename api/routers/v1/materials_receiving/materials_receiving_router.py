from fastapi import (APIRouter, Depends, 
                     status, HTTPException)
from api.routers.v1.materials_receiving import materials_receiving_repository as mr
from sqlalchemy.orm import Session
from api import service, database
from api.routers.v1.authentication.auth_outh2 import get_current_user
from typing import List

router = APIRouter(
    prefix="/api/v1/materials_receiving",
    tags=['Materials Receiving']
)

@router.get('/', status_code=status.HTTP_200_OK,
        response_model=List[service.MaterialsReceiving])
def get_all_materials_receivings(current_user: service.User = Depends(get_current_user)):
    return mr.get_all(current_user)