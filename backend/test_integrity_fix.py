import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from core.database import SessionLocal, Base, engine
from services.sheet_generator import generate_price_sheet

async def test_duplicate_url():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        from models.user import User
        user = db.query(User).first()
        if not user:
            print("No user found.")
            return

        # Use models that are very likely to return overlapping products
        models = ["Samsung M06 128GB", "Samsung Galaxy M06"]
        print(f"Testing parallel generation with overlapping models for user: {user.email}")
        
        # This used to crash with IntegrityError
        sheet = await generate_price_sheet(db, user.id, "TEST DUPLICATE URL", models=models)
        
        print(f"Sheet generated successfully: {sheet.id}")
        print(f"Rows: {len(sheet.rows)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(test_duplicate_url())
