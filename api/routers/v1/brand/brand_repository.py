from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from api import database, models, service
import logging
from api.routers.v1.authentication.auth_outh2 import get_current_user
from api.routers.v1.brand.brand_model import (
    get_vehicles_data,
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


def get_all(current_user: service.User = Depends(get_current_user)):
    vehicles_data = get_vehicles_data()

    # Transform the data to match the LineClearance model
    brand_data = [
        {
            "item_description": item["item_description"],
            "data": item["data"],
        }
        for item in vehicles_data
    ]

    return brand_data


def create(instance_id: int, db: Session = Depends(database.get_db)):
    # Get the form id from the instance
    try:
        instance = (
            db.query(models.Instance).filter(models.Instance.id == instance_id).first()
        )
        if not instance:
            raise HTTPException(status_code=404, detail="Instance not found")
        instance_id = instance.id  # Extract the integer ID

        # print(instance_id)
    except Exception as e:
        logger.error(f"Error fetching form ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching form ID",
        )
    # Get the vehicles data
    try:
        vehicles_data = (
            db.query(models.FormLogs)
            .filter(models.FormLogs.instance_id == instance_id)
            .all()
        )
        if not vehicles_data:
            raise HTTPException(status_code=404, detail="No data found for instance")
        # registration_number = vehicles_data[0].form_item_id  # Example field
    except Exception as e:
        logger.error(f"Error fetching vehicles data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching vehicles data",
        )
    # loop through vehicles data and print
    for data in vehicles_data:
        # print(data.form_item_id, data.form_item_feedback_value)
        # where data.form_item_id = 507 get the registration number
        if data.form_item_id == 507:
            registration_number = data.form_item_feedback_value
        if data.form_item_id == 508:
            current_mileage = data.form_item_feedback_value
        if data.form_item_id == 510:
            asset_entry_no = data.form_item_feedback_value
        if data.form_item_id == 541:
            service_type = data.form_item_feedback_value
        if data.form_item_id == 512:
            service_description = data.form_item_feedback_value

    # Get current date for logging purposes
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Define a sample DataFrame with the required columns.
    sample_data = {
        "serialNo": [registration_number],
        "description": ["Update from Compliance Tool"]
        if service_type == "Log"
        else ["Service: " + service_description],
        "entryType": [2] if service_type == "Log" else [1],
        "postingDate": [current_date],
        "value": [current_mileage],
        "assetEntryNo": [asset_entry_no],
    }

    df = pd.DataFrame(sample_data)

    if not df.empty:
        # print(f"Extracted {len(df)} rows for {df['serialNo'].nunique()} assets")
        # print("\nFirst few rows:")
        # print(df.head())
        # logger.info(f"Extracted {len(df)} rows for {df['serialNo'].nunique()} assets")
        # Push the data to the API endpoint
        results = push_maintenance_to_endpoint(df)
        logger.info(f"Push results: {results}")
    else:
        logger.info("No data found in the DataFrame.")
        results = "Failed"

    return results
