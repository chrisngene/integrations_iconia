from fastapi import (APIRouter, Depends, 
                     status, HTTPException)
from api.routers.v1.groups import groups_repository
from sqlalchemy.orm import Session
from api import service, database
from api.routers.v1.authentication.auth_outh2 import get_current_user
from typing import List

router = APIRouter(
    prefix="/api/v1/groups",
    tags=['Groups']
)
@router.get('/', status_code=status.HTTP_200_OK,
        response_model=List[service.Groups])
def get_all_groups(db: Session = Depends(database.get_db),
                      current_user: service.User = Depends(get_current_user)):
    return groups_repository.get_all(db, current_user)

@router.get('/{group_name}', status_code=status.HTTP_200_OK,
        response_model=service.Groups)
def get_group(group_name, db: Session = Depends(database.get_db),
                      current_user: service.User = Depends(get_current_user)):
    return groups_repository.get_one(group_name, db, current_user)

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_group(roles: service.Groups, db: Session = Depends(database.get_db),
                current_user: service.User = Depends(get_current_user)):
    return groups_repository.create(roles, db, current_user)

@router.put('/{group_name}', status_code=status.HTTP_202_ACCEPTED)
def update_group(group_name, groups: service.Groups, db: Session = Depends(database.get_db),
                current_user: service.User = Depends(get_current_user)):
    return groups_repository.update(group_name, groups, db, current_user)

@router.delete('/{group_name}',status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_name, db: Session = Depends(database.get_db),
                current_user: service.User = Depends(get_current_user)):
    return groups_repository.destroy(group_name, db, current_user)

@router.post('/{group_name}', status_code=status.HTTP_201_CREATED)
def create_role_in_group(group_name, group_priv: service.GroupRoles, db: Session = Depends(database.get_db),
                current_user: service.User = Depends(get_current_user)):
    return groups_repository.create_grp_role(group_name, group_priv, db, current_user)

@router.post('/add_user/{username}', status_code=status.HTTP_201_CREATED)
def create_user_in_group(username, grp_usr: service.UserGroup, db: Session = Depends(database.get_db),
                current_user: service.User = Depends(get_current_user)):
    return groups_repository.create_grp_users(username, grp_usr, db, current_user)