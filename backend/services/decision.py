from sqlalchemy.orm import Session
from models.product import PriceHistory
from datetime import datetime, timedelta, timezone

def get_purchase_decision(db: Session, product_id: int):
    last_30_days = datetime.now(timezone.utc) - timedelta(days=30)
    history = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id,
        PriceHistory.timestamp >= last_30_days
    ).order_by(PriceHistory.timestamp.asc()).all()
    
    if not history:
        return "UNKNOWN"
        
    prices = [h.price for h in history if h.price > 0]
    if not prices:
        return "UNKNOWN"
        
    current_price = prices[-1]
    lowest_price = min(prices)
    avg_price = sum(prices) / len(prices)
    
    if current_price <= lowest_price:
        return "BUY NOW"
    if current_price > avg_price:
        return "WAIT"
    return "GOOD PRICE"
