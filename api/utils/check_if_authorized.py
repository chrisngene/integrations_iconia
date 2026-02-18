from api import database, models
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

def if_authorized(current_user, db: Session = Depends(database.get_db)):
    is_active= db.query(models.User).filter(
        models.User.user_username  == current_user).filter(models.User.user_status == True).first()
    if not is_active:
        raise HTTPException(status_code=401,
                            detail='Not authorized')
    check_user_grp = db.query(models.GroupUser).filter(
                                models.GroupUser.id_user == is_active.id).filter(
                                models.GroupUser.id_company == is_active.id_company).all()
    usergrp = [row.id_group for row in check_user_grp]
    all_roles_grp = []
    for rlegrp in usergrp:
        all_roles = db.query(models.GroupRoles).filter(
                                models.GroupRoles.id_group == rlegrp).filter(
                                models.GroupRoles.id_company == is_active.id_company).all()
        for listroles in all_roles:
            all_roles_grp.append(listroles.id_role)
    all_system_func = []
    for system_func in all_roles_grp:
        all_sys_func = db.query(models.RolesPriviledges).filter(
                                models.RolesPriviledges.id_role == system_func).filter(
                                models.RolesPriviledges.id_company == is_active.id_company).all()
        for sys_func in all_sys_func:
            all_system_func.append(sys_func.id_func)
    return all_system_func 