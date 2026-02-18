from fastapi import (APIRouter, Depends, 
                     status, HTTPException)
from api.routers.v1.system_functions import system_functions_repository
from sqlalchemy.orm import Session
from api import service, database
from api.routers.v1.authentication.auth_outh2 import get_current_user
from typing import List

router = APIRouter(
    prefix="/api/v1/system_functions",
    tags=['System Functions']
)
@router.get('/', status_code=status.HTTP_200_OK,
        response_model=List[service.SystemFunctions])
def get_all_functions(db: Session = Depends(database.get_db),
                      current_user: service.User = Depends(get_current_user)):
    return system_functions_repository.get_all(db, current_user)

@router.get('/{system_function}', status_code=status.HTTP_200_OK,
        response_model=service.SystemFunctions)
def get_system_function(system_function, db: Session = Depends(database.get_db),
                      current_user: service.User = Depends(get_current_user)):
    return system_functions_repository.get_one(system_function, db, current_user)