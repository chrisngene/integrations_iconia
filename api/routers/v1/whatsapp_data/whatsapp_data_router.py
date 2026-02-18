from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date

# IMPORTANT: Ensure this import matches your database setup
from api.database import get_db 
from api.routers.v1.authentication.auth_outh2 import get_current_user
from api import service
from api.routers.v1.whatsapp_data import whatsapp_data_repository
# from api.service import WhatsAppChat

router = APIRouter(
    prefix="/api/v1/whatsapp/chats",
    tags=["WhatsApp Chats"]
)

ALLOWED_SORT_FIELDS = {
    "timestamp": "timestamp",
    "ratings": "ratings",
    "customer_support": "customer_support"
}
ALLOWED_SORT_DIR = {"asc", "desc"}


@router.get("/customer_service", status_code=status.HTTP_200_OK, summary="Get customer service chat messages")
def get_cs_messages(
    day_time_from: Optional[date] = Query(None),
    day_time_to: Optional[date] = Query(None),
    client_phone: Optional[str] = Query(
        None, description="Client phone number"
    ),
    client_id: Optional[int] = Query(
        None, description="Client ID"
    ),
    customer_support_id: Optional[int] = Query(
        None, description="Customer support ID"
    ),
    rating: Optional[int] = Query(
        None, description="Chat rating"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),

    db: Session = Depends(get_db),
    current_user: service.User = Depends(get_current_user),
):
    """
    Fetch WhatsApp chats with optional filtering and pagination.
    """

    return whatsapp_data_repository.get_cs_messages(
        client_phone=client_phone,
        client_id=client_id,
        customer_support_id=customer_support_id,
        rating=rating,
        page=page,
        page_size=page_size,
        day_time_from=day_time_from,
        day_time_to=day_time_to,
        db=db,
        current_user=current_user,
    )



@router.get("/ai", status_code=status.HTTP_200_OK, summary="Get all messages from WhatsApp AI chats")
def get_chat_ai_messages(
    day_time_from: Optional[date] = Query(None),
    day_time_to: Optional[date] = Query(None),
    client_phone: Optional[str] = Query(
        None, description="Client phone number"
    ),
    client_id: Optional[int] = Query(
        None, description="Client ID"
    ),
    customer_support_id: Optional[int] = Query(
        None, description="Customer support ID"
    ),
    rating: Optional[int] = Query(
        None, description="Chat rating"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),

    db: Session = Depends(get_db),
    current_user: service.User = Depends(get_current_user),
):
    """
    Fetch WhatsApp chats with optional filtering and pagination.
    """

    return whatsapp_data_repository.get_chat_ai_messages(
        client_phone=client_phone,
        # client_id=client_id,
        # customer_support_id=customer_support_id,
        # rating=rating,
        page=page,
        page_size=page_size,
        day_time_from=day_time_from,
        day_time_to=day_time_to,
        db=db,
        current_user=current_user,
    )