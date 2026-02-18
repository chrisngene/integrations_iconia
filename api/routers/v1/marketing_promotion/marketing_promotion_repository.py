from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from api import database, models, service
import logging
from api.routers.v1.authentication.auth_outh2 import get_current_user
from api.routers.v1.vehicles_inspection.vehicles_inspection_model import (
    get_vehicles_data,
    push_maintenance_to_endpoint,
)
from api.utils.check_if_authorized import if_authorized
import datetime
from datetime import datetime
import pandas as pd
from typing import Dict, Any, List
from pydantic import BaseModel
import pytz

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler(filename="logs/vehicles_inspection.log")
file_handler.setFormatter(fmt=formatter)

logger.addHandler(hdlr=file_handler)


class MarketingPromotion(BaseModel):
    item_description: Dict[str, str]
    data: Dict[str, Any]

    class Config:
        from_attributes = True


# def get_all_1(db: Session = Depends(database.get_db)):
#     promo_data = (
#         db.query(models.FormRowsLogs)
#         .filter(models.FormRowsLogs.instance_id == 3526)
#         .all()
#     )

#     formatted_data: List[MarketingPromotion] = []

#     for row in promo_data:
#         # Hardcoded keys, dynamic values from DB
#         item_description = {"741": row.q_one}
#         data = {"742": row.q_two}

#         formatted_data.append(
#             MarketingPromotion(item_description=item_description, data=data)
#         )

#     # print(formatted_data)  # You can log or return this
#     return formatted_data


# def get_all_2(db: Session = Depends(database.get_db)):
#     promo_data = (
#         db.query(models.FormRowsLogs)
#         .filter(models.FormRowsLogs.instance_id == 3526)
#         .all()
#     )

#     formatted_data: List[MarketingPromotion] = []

#     for row in promo_data:
#         # Hardcoded keys, dynamic values from DB
#         item_description = {"758": row.q_one}
#         data = {"759": row.q_two}

#         formatted_data.append(
#             MarketingPromotion(item_description=item_description, data=data)
#         )

#     # print(formatted_data)  # You can log or return this
#     return formatted_data


# Define the (item_description_key, data_key, instance_id) for each function
promotion_configs = [
    (741, 742, 3526),
    (758, 759, 3526),
    (764, 765, 3526),
    (770, 771, 3526),
    (776, 777, 3526),
    (782, 783, 3526),
    (788, 789, 3526),
    (794, 795, 3526),
    (800, 801, 3526),
    (806, 807, 3526),
]


def build_get_all_func(item_key: int, data_key: int, instance_id: int):
    """
    Dynamically create a repository function that fetches and formats marketing promo data.
    """

    def func(db: Session = database.get_db()):
        promo_data = (
            db.query(models.FormRowsLogs)
            .filter(models.FormRowsLogs.instance_id == instance_id)
            .all()
        )

        formatted_data: List[MarketingPromotion] = []

        for row in promo_data:
            item_description = {str(item_key): row.q_one}
            data = {str(data_key): row.q_two}

            formatted_data.append(
                MarketingPromotion(item_description=item_description, data=data)
            )

        # print(f"[DEBUG] get_all_marketing_promotions func for {instance_id}")
        # print(formatted_data)  # You can log or return this
        return formatted_data

    return func


# Dynamically assign 10 functions to the module
for i, (item_key, data_key, instance_id) in enumerate(promotion_configs, start=1):
    func_name = f"get_all_marketing_promotions_{i}"
    globals()[func_name] = build_get_all_func(item_key, data_key, instance_id)


# def update_product_quantity(instance_id: int, db: Session = Depends(database.get_db)):
#     try:
#         # Define Nairobi timezone
#         nairobi_tz = pytz.timezone("Africa/Nairobi")

#         # 1️⃣ Get product name (form_item_id = 741)
#         product_row = (
#             db.query(models.FormLogs)
#             .filter(models.FormLogs.instance_id == instance_id)
#             .filter(models.FormLogs.form_item_id == 741)
#             .first()
#         )

#         if not product_row:
#             print("⚠️ Product (form_item_id=741) not found")
#             return "Failed"

#         product_name = product_row.form_item_feedback_value
#         print(f"🧾 Product name: {product_name}")

#         # 2️⃣ Get quantity (form_item_id = 744)
#         quantity_row = (
#             db.query(models.FormLogs)
#             .filter(models.FormLogs.instance_id == instance_id)
#             .filter(models.FormLogs.form_item_id == 744)
#             .first()
#         )

#         if not quantity_row:
#             print("⚠️ Quantity (form_item_id=744) not found")
#             return "Failed"

#         quantity_value = quantity_row.form_item_feedback_value
#         print(f"📦 Quantity: {quantity_value}")

#         # 3️⃣ Current Nairobi time
#         nairobi_time = datetime.now(nairobi_tz)

#         # 4️⃣ Update FormRowsLogs
#         affected = (
#             db.query(models.FormRowsLogs)
#             .filter(models.FormRowsLogs.instance_id == 3526)
#             .filter(models.FormRowsLogs.q_one == product_name)
#             .update(
#                 {
#                     "q_two": quantity_value,
#                     "q_three": nairobi_time,
#                 },
#                 synchronize_session=False,
#             )
#         )

#         db.commit()

#         if affected > 0:
#             print(
#                 f"✅ Updated {affected} row(s) for '{product_name}' at {nairobi_time}"
#             )
#             return "Success"
#         else:
#             print("⚠️ No matching rows found in FormRowsLogs")
#             return "Failed"

#     except Exception as e:
#         db.rollback()
#         print("❌ Error:", e)
#         return "Failed"


def update_product_quantity(instance_id: int, db: Session = Depends(database.get_db)):
    try:
        nairobi_tz = pytz.timezone("Africa/Nairobi")

        # Define pairs of (product_form_item_id, quantity_form_item_id)
        product_qty_pairs = [
            (741, 744),
            (758, 761),
            (764, 767),
            (770, 773),
            (776, 779),
            (782, 785),
            (788, 791),
            (794, 797),
            (800, 803),
            (806, 809),
        ]

        total_updated = 0
        total_skipped = 0

        for product_id, qty_id in product_qty_pairs:
            # Fetch product name
            product_row = (
                db.query(models.FormLogs)
                .filter(models.FormLogs.instance_id == instance_id)
                .filter(models.FormLogs.form_item_id == product_id)
                .first()
            )

            if not product_row or not product_row.form_item_feedback_value:
                total_skipped += 1
                continue

            product_name = product_row.form_item_feedback_value

            # Fetch quantity value
            quantity_row = (
                db.query(models.FormLogs)
                .filter(models.FormLogs.instance_id == instance_id)
                .filter(models.FormLogs.form_item_id == qty_id)
                .first()
            )

            if not quantity_row or not quantity_row.form_item_feedback_value:
                total_skipped += 1
                continue

            # Remove commas from quantity (e.g., 1,000 -> 1000)
            quantity_value = quantity_row.form_item_feedback_value.replace(",", "")
            nairobi_time = datetime.now(nairobi_tz)

            # Update FormRowsLogs
            affected = (
                db.query(models.FormRowsLogs)
                .filter(models.FormRowsLogs.instance_id == 3526)
                .filter(models.FormRowsLogs.q_one == product_name)
                .update(
                    {
                        "q_two": quantity_value,
                        "q_three": nairobi_time,
                    },
                    synchronize_session=False,
                )
            )

            if affected > 0:
                total_updated += affected

        db.commit()

        return {
            "status": "Success",
            "updated_rows": total_updated,
            "skipped": total_skipped,
        }

    except Exception as e:
        db.rollback()
        print("❌ Error:", e)
        return {"status": "Failed", "error": str(e)}
