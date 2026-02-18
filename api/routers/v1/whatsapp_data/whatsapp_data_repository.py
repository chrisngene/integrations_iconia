from datetime import date
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status

from api import models, service
from api.utils.check_if_authorized import if_authorized
from api.routers.v1.whatsapp_data.whatsapp_data_model import WhatsAppChat, AIChat



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_cs_messages(
    *,
    client_phone: str | None,
    client_id: int | None,
    customer_support_id: int | None,
    rating: str | None,
    page: int,
    page_size: int,
    day_time_from: date | None,
    day_time_to: date | None,
    db: Session,
    current_user: service.User,
):
    filters = {
        "client_phone": client_phone,
        "client_id": client_id,
        "customer_support_id": customer_support_id,
        "rating": rating,
        "day_time_from": day_time_from,
        "day_time_to": day_time_to,
    }

    active_filters = {k: v for k, v in filters.items() if v is not None}

    where_clauses: List[str] = []
    params: Dict[str, Any] = {}

    FILTER_MAP = {
        "client_phone": ("client_phone", "="),
        "client_id": ("client_id", "="),
        "customer_support_id": ("customer_support_id", "="),
        "rating": ("ratings", "="),

        # date range
        "day_time_from": ("day_time", ">="),
        "day_time_to": ("day_time", "<="),
    }


    for key, column in FILTER_MAP.items():
        if key in active_filters:
            where_clauses.append(f"{column[0]} {column[1]} :{key}")
            params[key] = active_filters[key]

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    limit = page_size
    offset = (page - 1) * page_size

    print(f"Where SQL: {where_sql}")

    data_sql = f"""
        SELECT
            chat_id,
            customer_support_id,
            customer_support,
            client_id,
            client_name,
            client_phone,
            chat_originator,
            chat_message,
            "timestamp",
            day_time,
            first_day_of_month,
            ratings
        FROM cb_jipange_whatsapp.v_customer_service_chats
        {where_sql}
        ORDER BY chat_id asc
        LIMIT :limit OFFSET :offset
    """

    count_sql = f"""
        SELECT COUNT(1)
        FROM cb_jipange_whatsapp.v_customer_service_chats
        {where_sql}
    """

    try:
        total_records = db.execute(
            text(count_sql),
            params
        ).scalar()

        rows = db.execute(
            text(data_sql),
            {**params, "limit": limit, "offset": offset}
        ).mappings().all()

        logger.info(
            "Fetched %s WhatsApp chats | filters=%s | user=%s",
            len(rows),
            active_filters,
            current_user,
        )

        return {
            "data": [WhatsAppChat(**row) for row in rows],
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "applied_filters": active_filters,
        }

    except Exception as e:
        logger.exception("Failed to fetch WhatsApp chats")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )




def get_chat_ai_messages(
    *,
    client_phone: str | None,
    # client_id: int | None,
    # customer_support_id: int | None,
    # rating: int | None,
    page: int,
    page_size: int,
    day_time_from: date | None,
    day_time_to: date | None,
    db: Session,
    current_user: service.User,
):
    filters = {
        "client_phone": client_phone,
        # "client_id": client_id,
        # "customer_support_id": customer_support_id,
        # "rating": rating,
        "day_time_from": day_time_from,
        "day_time_to": day_time_to,
    }

    active_filters = {k: v for k, v in filters.items() if v is not None}

    where_clauses: List[str] = []
    params: Dict[str, Any] = {}

    FILTER_MAP = {
        "client_phone": ("client_phone", "="),
        # "client_id": ("client_id", "="),
        # "customer_support_id": ("customer_support_id", "="),
        # "rating": ("ratings", "="),

        # date range
        "day_time_from": ("day_time", ">="),
        "day_time_to": ("day_time", "<="),
    }


    for key, column in FILTER_MAP.items():
        if key in active_filters:
            where_clauses.append(f"{column[0]} {column[1]} :{key}")
            params[key] = active_filters[key]

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    limit = page_size
    offset = (page - 1) * page_size

    print(f"Where SQL: {where_sql}")

    data_sql = f"""
        SELECT id, 
        msg_classification, 
        sentiment, 
        sentiment_meaning, 
        "timestamp", 
        day_time, 
        first_day_of_month, 
        product, 
        client_phone, 
        client_name, 
        town, 
        two_word_summary, 
        human, 
        ai
        FROM cb_jipange_whatsapp.v_ai_chats
        {where_sql}
        ORDER BY id asc
        LIMIT :limit OFFSET :offset
    """

    count_sql = f"""
        SELECT COUNT(1)
        FROM cb_jipange_whatsapp.v_ai_chats
        {where_sql}
    """

    try:
        total_records = db.execute(
            text(count_sql),
            params
        ).scalar()

        rows = db.execute(
            text(data_sql),
            {**params, "limit": limit, "offset": offset}
        ).mappings().all()

        logger.info(
            "Fetched %s AI chats | filters=%s | user=%s",
            len(rows),
            active_filters,
            current_user,
        )

        return {
            "data": [AIChat(**row) for row in rows],
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "applied_filters": active_filters,
        }

    except Exception as e:
        logger.exception("Failed to fetch AI chats")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
        