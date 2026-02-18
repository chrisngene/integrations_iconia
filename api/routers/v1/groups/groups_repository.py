from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from api import database, models, service
import logging
from api.routers.v1.authentication.auth_outh2 import get_current_user
from api.utils.check_if_authorized import if_authorized
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler(filename="logs/groups.log")
file_handler.setFormatter(fmt=formatter)

logger.addHandler(hdlr=file_handler)

def get_all(db: Session = Depends(database.get_db),
            current_user: service.User = Depends(get_current_user)):
    priv_name = "Can_View_Groups"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    groups = db.query(models.Groups).filter(
        models.Groups.id_company == is_active.id_company).all()
    logs_user = f"User {current_user} viewed groups for {is_active.id_company}"
    logger.info(logs_user)
    return groups

def get_one(group_name, db: Session = Depends(database.get_db),
            current_user: service.User = Depends(get_current_user)):
    priv_name = "Can_View_Group"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    group = db.query(models.Groups).filter(
        models.Groups.group_name == group_name).filter(
        models.Groups.id_company == is_active.id_company).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'group {group_name} not available')
    logs_user = f"User {current_user} viewed group {group_name} for {is_active.id_company}"
    logger.info(logs_user)
    return group

def create(groups: service.Groups, db: Session = Depends(database.get_db),
           current_user: service.User = Depends(get_current_user)):
    priv_name = "Can_Create_Group"
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
    group_name = db.query(models.Groups).filter(
        models.Groups.group_name == groups.group_name).filter(
        models.Groups.id_company == company_id.id_company).first()
    if group_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'group {groups.group_name} is already in existence')

    new_group = models.Groups(group_name=groups.group_name,
                            description=groups.description,
                            created_at=datetime.datetime.now(),
                            updated_at=datetime.datetime.now(),
                            id_company =company_id.id_company)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    logs_user = f"User {current_user} created group {new_group.group_name} for company {new_group.id_company}"
    logger.info(logs_user)
    return {"message": f"group with name {groups.group_name} was created succesfully"}

def update(group_name, groups: service.Groups, db: Session, current_user):
    priv_name = "Can_Update_Group"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    updated_group = db.query(models.Groups).filter(
        models.Groups.group_name == group_name).filter(
        models.Groups.id_company == is_active.id_company)
    if not updated_group.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"group with group name {groups.group_name} was not found")
    updated_group.first().updated_at = datetime.datetime.now()
    updated_group.update(groups.dict())
    db.commit()
    logs_user = f"User {current_user} updated group {updated_group.first().group_name} for company {updated_group.first().id_company}"
    logger.info(logs_user)
    return {'message': 'updated'}

def destroy(group_name, db: Session = Depends(database.get_db),
            current_user: service.User = Depends(get_current_user)):
    priv_name = "Can_Delete_Group"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    group = db.query(models.Groups).filter(
        models.Groups.group_name == group_name).filter(
        models.Groups.id_company == is_active.id_company)
    if not group.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'group deleted successfully')
    db.query(models.Groups).filter(models.Groups.group_name ==
                                  group_name).delete(synchronize_session=False)
    db.commit()
    logs_user = f"User {current_user} deleted group {group.first().group_name} for company {group.first().id_company}"
    logger.info(logs_user)
    return {"message": f"group deleted successfully"}

def create_grp_role(group_name: str, grp_priv: service.GroupRoles, db: Session, current_user):
    priv_name = "Can_Add_Role_To_Group"
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
    groups_name = db.query(models.Groups).filter(
        models.Groups.group_name == group_name).filter(
        models.Groups.id_company == company_id.id_company).first()
    if not groups_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"group {groups_name.group_name} doesn't exist")
    role_name = db.query(models.Roles).filter(
        models.Roles.role_name == grp_priv.role_name).first()
    if not role_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"role name {grp_priv.role_name} doesn't exist")
    existing_grp_role = db.query(models.GroupRoles).filter(
                                 models.GroupRoles.id_group == groups_name.id).filter(
                                 models.GroupRoles.id_role == role_name.id).first()
    if existing_grp_role:
        raise HTTPException(status_code=400,
                            detail=f"group {groups_name.group_name} with role {role_name.role_name} already exists.")
    new_grp_role = models.GroupRoles(id_role=role_name.id,
                                     id_group=groups_name.id,
                                     id_company=is_active.id_company)
    db.add(new_grp_role)
    db.commit()
    db.refresh(new_grp_role)
    logs_user = f"User {current_user} created group role {groups_name.group_name} for company {groups_name.id_company}"
    logger.info(logs_user)
    return {"message": f"role {grp_priv.role_name} added to group {group_name}"}

def create_grp_users(username: str, grp_usr: service.UserGroup, db: Session, current_user):
    priv_name = "Can_Add_User_To_Group"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    is_active = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401, detail='Not Authorized')
    groups_name = db.query(models.Groups).filter(
        models.Groups.group_name == grp_usr.group_name).filter(
        models.Groups.id_company == is_active.id_company).first()
    if not groups_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"group {grp_usr.group_name} doesn't exist")
    fetched_username = db.query(models.User).filter(
        models.User.user_username == username).first()
    if not fetched_username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"username {username} doesn't exist")
    existing_grp_user = db.query(models.GroupUser).filter(
                                 models.GroupUser.id_group == groups_name.id).filter(
                                 models.GroupUser.id_user == fetched_username.id).first()
    if existing_grp_user:
        raise HTTPException(status_code=400,
                            detail=f"user {username} already in group {groups_name.group_name}.")
    new_grp_user = models.GroupUser(id_group=groups_name.id,
                                    id_user=fetched_username.id,
                                    id_company=is_active.id_company)
    db.add(new_grp_user)
    db.commit()
    db.refresh(new_grp_user)
    logs_user = f"User {current_user} added {username} to group {groups_name.group_name} for company {groups_name.id_company} "
    logger.info(logs_user)
    return {"message": f"user {username} added to group {groups_name.group_name}"}
    