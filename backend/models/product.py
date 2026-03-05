from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from core.database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    site = Column(String, index=True)
    product_name = Column(String)
    current_price = Column(Integer)
    currency = Column(String)
    rating = Column(String)
    availability = Column(String)
    url = Column(String, unique=True, index=True)
    image_url = Column(String)
    delivery_info = Column(String)
    colors = Column(String)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    price_history = relationship("PriceHistory", back_populates="product")
    alerts = relationship("PriceAlert", back_populates="product")

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Integer)
    timestamp = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    product = relationship("Product", back_populates="price_history")

class PriceSheet(Base):
    __tablename__ = "price_sheets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    rows = relationship("PriceSheetRow", back_populates="sheet", cascade="all, delete-orphan")
    pincodes = relationship("PriceSheetPincode", back_populates="sheet", cascade="all, delete-orphan")

class PriceSheetRow(Base):
    # ... existing code ...
    __tablename__ = "price_sheet_rows"
    id = Column(Integer, primary_key=True, index=True)
    sheet_id = Column(Integer, ForeignKey("price_sheets.id"))
    
    # Identification
    model_name = Column(String)
    retailer = Column(String) # e.g. Amazon, Flipkart, Vijay Sales, Jio Mart
    channel = Column(String) # e.g. APPLE
    
    # Offline
    mop_offline = Column(Integer, default=0)
    cif_offline = Column(Integer, default=0)
    
    # Online
    mop_online = Column(Integer, default=0)
    secure_packaging = Column(Integer, default=0)
    offer_handling = Column(Integer, default=0)
    corp_fees = Column(Integer, default=0)
    
    # Bank Offers (Debit/Credit discount)
    coupon = Column(Integer, default=0)
    bank_hdfc = Column(Integer, default=0)
    bank_icici = Column(Integer, default=0)
    
    # Calculated
    swipe_amount = Column(Integer, default=0)
    
    # Cashback
    cashback_hdfc = Column(Integer, default=0)
    cashback_icici = Column(Integer, default=0)
    cashback_emi = Column(Integer, default=0)
    
    # Final
    landing_price = Column(Integer, default=0)
    emi_landing = Column(Integer, default=0)
    cif_cost_today = Column(Integer, default=0)
    remark = Column(String) # e.g. OOS, delivery date
    product_url = Column(String) # URL to the product

    sheet = relationship("PriceSheet", back_populates="rows")

class PriceSheetPincode(Base):
    __tablename__ = "price_sheet_pincodes"
    id = Column(Integer, primary_key=True, index=True)
    sheet_id = Column(Integer, ForeignKey("price_sheets.id"))
    model_name = Column(String)
    pincode = Column(String)
    city_name = Column(String)
    availability = Column(String)
    delivery_date = Column(String)
    colors = Column(String) # Available colors

    sheet = relationship("PriceSheet", back_populates="pincodes")

