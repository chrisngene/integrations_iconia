from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from api import database, models, service
import logging
from api.routers.v1.authentication.auth_outh2 import get_current_user
from api.routers.v1.line_clearance.line_clearance_model import get_production_data
from api.utils.check_if_authorized import if_authorized
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler(filename="logs/line_clearance.log")
file_handler.setFormatter(fmt=formatter)

logger.addHandler(hdlr=file_handler)

def get_all(current_user: service.User = Depends(get_current_user)):
    production_data = get_production_data()
    
    # Transform the data to match the LineClearance model
    line_clearance_data = [
        {
            "item_description": item["item_description"],
            "data": item["data"]
        }
        for item in production_data
    ]
    
    return line_clearance_data

    