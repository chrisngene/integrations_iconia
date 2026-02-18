from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class WhatsAppChat(BaseModel):
    chat_id: int
    customer_support_id: Optional[int]
    customer_support: Optional[str]
    client_id: Optional[int]
    client_name: Optional[str]
    client_phone: Optional[str]
    chat_originator: str
    chat_message: str
    timestamp: datetime
    day_time: date  # Change from str to date
    first_day_of_month: date # Match the db output
    ratings: Optional[str]


class AIChat(BaseModel):
    id: int
    msg_classification: Optional[str]
    sentiment: Optional[int]
    sentiment_meaning: Optional[str]
    timestamp: datetime
    day_time: date  # Change from str to date
    first_day_of_month: date # Match the db output
    product: Optional[str]
    client_phone: Optional[str]
    client_name: Optional[str]
    town: Optional[str]
    two_word_summary: Optional[str]
    human: Optional[str]
    ai: Optional[str]
    
    