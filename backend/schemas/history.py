from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SearchHistoryRead(BaseModel):
    id: int
    user_id: int
    query: str
    timestamp: datetime

    class Config:
        from_attributes = True

class PriceAlertBase(BaseModel):
    product_id: int
    target_price: int

class PriceAlertCreate(PriceAlertBase):
    pass

class PriceAlertRead(PriceAlertBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
