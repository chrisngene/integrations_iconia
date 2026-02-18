from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from api import service, database
from api.routers.v1.user import user_repository
from api.routers.v1.authentication.auth_outh2 import get_current_user
from typing import List

router = APIRouter(
    prefix="/api/v1/user",
    tags=['User']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(user: service.User, db: Session = Depends(database.get_db),
                current_user: service.User = Depends(get_current_user)):
    return user_repository.create(user, db, current_user)

@router.get('/{username}',status_code=status.HTTP_200_OK,response_model=service.ShowUser)
def fetch_user(username, db: Session = Depends(database.get_db),
               current_user: service.User = Depends(get_current_user)):
    return user_repository.fetchone(username, db, current_user)

@router.get('/',status_code=status.HTTP_200_OK,response_model=List[service.ShowUser])
def fetch_users(db: Session = Depends(database.get_db),
               current_user: service.User = Depends(get_current_user)):
    return user_repository.fetchall(db, current_user)

@router.put('/', status_code=status.HTTP_202_ACCEPTED)
def update_user(user: service.UpdateUser, db: Session = Depends(database.get_db),
                   current_user: service.User = Depends(get_current_user)):
    return user_repository.update(user, db, current_user)

@router.put('/{username}', status_code=status.HTTP_202_ACCEPTED)
def update_user_admin(username, user: service.UpdateUserAdmin, db: Session = Depends(database.get_db),
                   current_user: service.User = Depends(get_current_user)):
    return user_repository.update_to_admin(username, user, db, current_user)

@router.delete('/{username}',status_code=status.HTTP_204_NO_CONTENT)
def delete_user(username, db: Session = Depends(database.get_db),
                current_user: service.User = Depends(get_current_user)):
    return user_repository.destroy(username, db, current_user)