from fastapi import (APIRouter, Depends, 
                     status, HTTPException)
from api.routers.v1.roles import roles_repository
from sqlalchemy.orm import Session
from api import service, database
from api.routers.v1.authentication.auth_outh2 import get_current_user
from typing import List

router = APIRouter(
    prefix="/api/v1/roles",
    tags=['Roles']
)
@router.get('/', status_code=status.HTTP_200_OK,
        response_model=List[service.Roles])
def get_all_roles(db: Session = Depends(database.get_db),
                      current_user: service.User = Depends(get_current_user)):
    return roles_repository.get_all(db, current_user)

@router.get('/{role_name}', status_code=status.HTTP_200_OK,
        response_model=service.Roles)
def get_role(role_name, db: Session = Depends(database.get_db),
                      current_user: service.User = Depends(get_current_user)):
    return roles_repository.get_one(role_name, db, current_user)

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_role(roles: service.Roles, db: Session = Depends(database.get_db),
                current_user: service.User = Depends(get_current_user)):
    return roles_repository.create(roles, db, current_user)

@router.put('/{role_name}', status_code=status.HTTP_202_ACCEPTED)
def update_role(role_name, roles: service.Roles, db: Session = Depends(database.get_db),
                current_user: service.User = Depends(get_current_user)):
    return roles_repository.update(role_name, roles, db, current_user)

@router.delete('/{role_name}',status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_name, db: Session = Depends(database.get_db),
                current_user: service.User = Depends(get_current_user)):
    return roles_repository.destroy(role_name, db, current_user)

@router.post('/{role_name}', status_code=status.HTTP_201_CREATED)
def create_system_function_in_role(role_name, role_priv: service.RolesPriviledges, db: Session = Depends(database.get_db),
                current_user: service.User = Depends(get_current_user)):
    return roles_repository.create_role_priv(role_name, role_priv, db, current_user)