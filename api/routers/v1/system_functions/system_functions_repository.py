from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from api import database, models, service
from api.routers.v1.authentication.auth_outh2 import get_current_user
from api.utils.check_if_authorized import if_authorized
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler(filename="logs/sys_func.log")
file_handler.setFormatter(fmt=formatter)

logger.addHandler(hdlr=file_handler)

def get_all(db: Session = Depends(database.get_db),
            current_user: service.User = Depends(get_current_user)):
    is_superuser = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_is_superuser == True)
    if is_superuser.first():
        raise HTTPException(status_code=401, detail='Not Authorized')
    priv_name = "Can_View_System_Functions"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    system_functions = db.query(models.SystemFunction).filter(
        models.SystemFunction.is_active==True).all()
    logs_user = f"User {current_user} viewed all System Functions"
    logger.info(logs_user)
    return system_functions

def get_one(system_function, db: Session = Depends(database.get_db),
            current_user: service.User = Depends(get_current_user)):
    is_superuser = db.query(models.User).filter(
        models.User.user_username == current_user).filter(models.User.user_is_superuser == True)
    if is_superuser.first():
        raise HTTPException(status_code=401, detail='Not Authorized')
    priv_name = "Can_View_System_Function"
    priv = db.query(models.SystemFunction).filter(models.SystemFunction.func_name == priv_name).first()
    all_system_func = if_authorized(current_user, db)
    if priv.id not in all_system_func:
        raise HTTPException(status_code=401, detail='Not Authorized')
    sys_func = db.query(models.SystemFunction).filter(
        models.SystemFunction.func_name == system_function
    ).filter(
        models.SystemFunction.is_active == True
    ).first()
    if not sys_func:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'system function {system_function} not available')
    logs_user = f"User {current_user} viewed System Function {sys_func.func_name}"
    logger.info(logs_user)
    return sys_func