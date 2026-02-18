from fastapi import (APIRouter, Depends, 
                     status, HTTPException)
from api.routers.v1.line_clearance import line_clearance_repository as lc
from sqlalchemy.orm import Session
from api import service, database
from api.routers.v1.authentication.auth_outh2 import get_current_user
from typing import List

router = APIRouter(
    prefix="/api/v1/line_clearance",
    tags=['Line Clearance']
)

@router.get('/', status_code=status.HTTP_200_OK,
        response_model=List[service.LineClearance])
def get_all_line_clearances(current_user: service.User = Depends(get_current_user)):
    return lc.get_all(current_user)