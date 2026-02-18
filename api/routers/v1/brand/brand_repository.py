from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from api import database, models, service
import logging
from api.routers.v1.authentication.auth_outh2 import get_current_user
from api.routers.v1.brand.brand_model import (
    get_brand_data,
    push_maintenance_to_endpoint,
)
from api.utils.check_if_authorized import if_authorized
import datetime
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler(filename="logs/brand.log")
file_handler.setFormatter(fmt=formatter)

logger.addHandler(hdlr=file_handler)


def get_all(current_user: service.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    
    #  select FormRowsLogs table where instance_id = 11545 and is_active = True
    brand_data = (
    db.query(models.FormRowsLogs)
    .filter(
        models.FormRowsLogs.instance_id == 11545,
        models.FormRowsLogs.is_active.is_(True)
    )
    .order_by(models.FormRowsLogs.id.asc())
    .all()
)
 
    # print(brand_data)

    result = []

    for b in brand_data:
        result.append(
            {
                "item_description": {
                    "4511": b.q_one 
                },
                "data": {
                    "4512": b.q_two
                }
            }
        )

    return result

    

