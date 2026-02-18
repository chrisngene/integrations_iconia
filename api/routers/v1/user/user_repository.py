from api import models, service
from api.libs.hashing import Hash
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from api.utils.check_if_authorized import if_authorized
import datetime

def create(user: service.User, db: Session, current_user):
    priv_name = "Can_Create_User"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    get_current_user = db.query(models.User).filter(
        models.User.user_username == current_user).first()
    check_user = db.query(models.User).filter(
        models.User.user_username == user.user_username).first()
    if check_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='username is invalid or already taken')
    check_email = db.query(models.User).filter(
        models.User.user_email == user.user_email).first()
    if check_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='email is invalid or already taken')  
    get_current_user = db.query(models.User).filter(
        models.User.user_username == current_user
    ).first()
    get_id_roles = db.query(models.CompanyRoles).filter(
        models.CompanyRoles.id_company == get_current_user.id_company
    ).filter(
        models.CompanyRoles.company_role_status == True
    ).all()
    if not get_id_roles:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                            detail="No roles available.")
    company_roles = [row.id for row in get_id_roles]
    if user.id_role not in company_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="check if id role is correct.")
    try:
        new_user = models.User(
            user_fname=user.user_fname,
            user_lname=user.user_lname,
            user_fullname = f"{user.user_fname} {user.user_lname}",
            user_username = user.user_username,
            user_gender = user.user_gender,
            user_phone = user.user_phone,
            user_password = Hash.bcrypt(user.user_password), 
            user_email=user.user_email,
            user_address = user.user_address,
            user_joindate = datetime.datetime.now(),
            user_status=True, 
            id_role = user.id_role,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            created_by=current_user,
            id_company=get_current_user.id_company
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {
            "respnose": "success",
            "details": {"username": f"{user.user_username}",
                        "email": f"{user.user_email}",
                        "firstname": f"{user.user_fname}",
                        "lastname": f"{user.user_lname}"
                        }
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
      
def fetchone(username, db: Session, current_user):
    priv_name = "Can_View_User"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    if current_user != username:
        raise HTTPException(status_code=401,
                            detail='Not authorized') 
    user = db.query(models.User).filter(models.User.user_username == username).first() 
    return user

def update(user: service.UpdateUser, db: Session, current_user):
    priv_name = "Can_Update_User"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    updated_user = db.query(models.User).filter(
        models.User.user_username == current_user)
    if not updated_user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"username {current_user} was not found") 
    try:
        user.user_password = Hash.bcrypt(user.user_password)
        updated_user.update(user.dict())
        db.commit()
        return {'message': 'updated'}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
def update_to_admin(username, user: service.UpdateUserAdmin, db: Session, current_user):
    priv_name = "Can_Update_User_To_Admin"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    updated_user = db.query(models.User).filter(
        models.User.user_username == username)
    if not updated_user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"username {current_user} was not found") 
    try:
        user.user_password = Hash.bcrypt(user.user_password)
        updated_user.update(user.dict())
        db.commit()
        return {'message': 'updated'}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def fetchall(db: Session, current_user):
    priv_name = "Can_View_Users"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active= db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401,
                            detail='Not authorized')
    users = db.query(models.User).filter(
        models.User.id_company == is_active.id_company
    ).all()
    return users

def destroy(username, db: Session, current_user):
    is_superuser = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_is_superuser == True)
    if is_superuser.first():
        raise HTTPException(status_code=401, detail='Not Authorized')
    priv_name = "Can_Delete_User"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active= db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401,
                            detail='Not authorized')
    delete_user = db.query(models.User).filter(models.User.user_username == username).first()
    if not delete_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with username {username} was not found")
    if current_user != delete_user.user_username:
        raise HTTPException(status_code=401,
                            detail='Not authorized')
    try:
        delete_user.user_status = False
        db.commit()
        db.refresh(delete_user)
        return {'message': 'user deleted successfully'}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
