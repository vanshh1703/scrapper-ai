from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from core.database import Base

class RoleEnum(str, enum.Enum):
    free = "free"
    pro = "pro"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.free)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    searches_today = Column(Integer, default=0)
    last_search_date = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    search_history = relationship("SearchHistory", back_populates="user")
    price_alerts = relationship("PriceAlert", back_populates="user")
