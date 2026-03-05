import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from core.database import SessionLocal, Base, engine
from services.sheet_generator import generate_price_sheet

async def test_dyson():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        from models.user import User
        user = db.query(User).first()
        if not user:
            print("No user found.")
            return

        query = "Dyson"
        print(f"Testing brand discovery for: {query}")
        
        sheet = await generate_price_sheet(db, user.id, "DYSON TEST SHEET", brand_search=True, query=query)
        
        print(f"\nSheet generated for {query}: {sheet.id}")
        print(f"Discovered models: {[r.model_name for r in sheet.rows[:5]]}") # Show first 5
        
        for row in sheet.rows[:10]:
            print(f" - [{row.channel}] {row.model_name}: {row.mop_online} ({row.remark})")

    finally:
        db.close()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(test_dyson())
