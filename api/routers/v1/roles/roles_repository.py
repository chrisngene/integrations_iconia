from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from api import database, models, service
from api.routers.v1.authentication.auth_outh2 import get_current_user
from api.utils.check_if_authorized import if_authorized
import logging
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler(filename="logs/roles.log")
file_handler.setFormatter(fmt=formatter)

logger.addHandler(hdlr=file_handler)

def get_all(db: Session = Depends(database.get_db),
            current_user: service.User = Depends(get_current_user)):
    priv_name = "Can_View_Roles"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status== True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    roles = db.query(models.Roles).filter(
        models.Roles.id_company == is_active.id_company).all()
    logs_user = f"User {current_user} viewed roles for {is_active.id_company}"
    logger.info(logs_user)
    return roles

def get_one(role_name, db: Session = Depends(database.get_db),
            current_user: service.User = Depends(get_current_user)):
    priv_name = "Can_View_Role"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    role = db.query(models.Roles).filter(
        models.Roles.role_name == role_name).filter(
        models.Roles.id_company == is_active.id_company).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'role {role_name} not available')
    logs_user = f"User {current_user} viewed role {role_name} for {is_active.id_company}"
    logger.info(logs_user)
    return role

def create(roles: service.Roles, db: Session = Depends(database.get_db),
           current_user: service.User = Depends(get_current_user)):
    priv_name = "Can_Create_Role"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    company_id = db.query(models.User).filter(
        models.User.user_username == current_user).first()
    role_name = db.query(models.Roles).filter(
        models.Roles.role_name == roles.role_name).filter(
        models.Roles.id_company == company_id.id_company).first()
    if role_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'role {role_name.role_name} is already in existence')

    new_role = models.Roles(role_name=roles.role_name,
                            description=roles.description,
                            created_at=datetime.datetime.now(),
                            updated_at=datetime.datetime.now(),
                            id_company=company_id.id_company)

    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    logs_user = f"User {current_user} created role {new_role.role_name} for company {new_role.id_company}"
    logger.info(logs_user)
    return {"message": f"role with name {new_role.role_name} was created succesfully"}

def update(role_name, roles: service.Roles, db: Session, current_user):
    priv_name = "Can_Update_Role"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    updated_role = db.query(models.Roles).filter(
        models.Roles.role_name == role_name).filter(
        models.Roles.id_company == is_active.id_company)
    if not updated_role.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"role with {roles.role_name} was not found")

    updated_role.first().updated_at = datetime.datetime.now()
    updated_role.update(roles.dict())
    db.commit()
    logs_user = f"User {current_user} updated group {updated_role.first().role_name} for company {updated_role.first().id_company}"
    logger.info(logs_user)
    return {'message': 'updated'}

def destroy(role_name, db: Session = Depends(database.get_db),
            current_user: service.User = Depends(get_current_user)):
    priv_name = "Can_Delete_Role"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    role = db.query(models.Roles).filter(
        models.Roles.role_name == role_name).filter(
        models.Roles.id_company == is_active.id_company)
    if not role.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'role deleted successfully')
    db.query(models.Roles).filter(models.Roles.role_name ==
                                  role_name).delete(synchronize_session=False)
    db.commit()
    logs_user = f"User {current_user} deleted group {role.first().role_name} for company {role.first().id_company}"
    logger.info(logs_user)
    return {"message": f"role deleted successfully"}

def create_role_priv(role_name, role_priv: service.RolesPriviledges, db: Session, current_user):
    priv_name = "Can_Add_SystemFunction_To_Role"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    company_id = db.query(models.User).filter(
        models.User.user_username == current_user).first()
    rol_nam = db.query(models.Roles).filter(
        models.Roles.role_name == role_name).filter(
        models.Roles.id_company == company_id.id_company).first()
    if not rol_nam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"role {rol_nam.role_name} doesn't exist")
    func_name = db.query(models.SystemFunction).filter(
        models.SystemFunction.func_name == role_priv.func_name).first()
    if not func_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"system function {role_priv.func_name} doesn't exist")
    existing_rol_priv = db.query(models.RolesPriviledges).filter(
                                 models.RolesPriviledges.id_role == rol_nam.id).filter(
                                 models.RolesPriviledges.id_func == func_name.id).first()
    if existing_rol_priv:
        raise HTTPException(status_code=400,
                            detail=f"role {rol_nam.role_name} with system function {func_name.func_name} already exists.")
    new_role_func = models.RolesPriviledges(id_role=rol_nam.id,
                                            id_func=func_name.id,
                                            id_company=company_id.id_company)
    db.add(new_role_func)
    db.commit()
    db.refresh(new_role_func)
    logs_user = f"User {current_user} added function {func_name.func_name} to role {rol_nam.role_name} for company {company_id.id_company} "
    logger.info(logs_user)
    return {"message": f"system function {role_priv.func_name} added to role {role_name}"}
    