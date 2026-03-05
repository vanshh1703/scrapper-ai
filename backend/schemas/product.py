from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PriceHistoryRead(BaseModel):
    id: int
    price: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    site: str
    product_name: str
    current_price: int
    currency: str
    rating: Optional[str] = None
    availability: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    delivery_info: Optional[str] = None
    colors: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int
    updated_at: datetime
    price_history: List[PriceHistoryRead] = []

    class Config:
        from_attributes = True

class PriceSheetRowBase(BaseModel):
    model_name: str
    retailer: Optional[str] = None
    channel: Optional[str] = "APPLE"
    mop_offline: Optional[int] = 0
    cif_offline: Optional[int] = 0
    mop_online: Optional[int] = 0
    secure_packaging: Optional[int] = 0
    offer_handling: Optional[int] = 0
    corp_fees: Optional[int] = 0
    coupon: Optional[int] = 0
    bank_hdfc: Optional[int] = 0
    bank_icici: Optional[int] = 0
    swipe_amount: Optional[int] = 0
    cashback_hdfc: Optional[int] = 0
    cashback_icici: Optional[int] = 0
    cashback_emi: Optional[int] = 0
    landing_price: Optional[int] = 0
    emi_landing: Optional[int] = 0
    cif_cost_today: Optional[int] = 0
    remark: Optional[str] = None
    product_url: Optional[str] = None

class PriceSheetRowRead(PriceSheetRowBase):
    id: int
    sheet_id: int

    class Config:
        from_attributes = True

class PriceSheetBase(BaseModel):
    name: str

class PriceSheetCreate(PriceSheetBase):
    models: Optional[List[str]] = [] # List of model names to search for
    brand_search: Optional[bool] = False
    query: Optional[str] = None

class PriceSheetPincodeRead(BaseModel):
    id: int
    sheet_id: int
    model_name: str
    pincode: str
    city_name: str
    availability: str
    delivery_date: str
    colors: Optional[str] = None

    class Config:
        from_attributes = True

class PriceSheetRead(PriceSheetBase):
    id: int
    user_id: int
    created_at: datetime
    rows: List[PriceSheetRowRead]
    pincodes: List[PriceSheetPincodeRead] = []

    class Config:
        from_attributes = True
