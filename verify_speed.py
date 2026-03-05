import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from core.database import SessionLocal
from services.sheet_generator import generate_price_sheet
from models.user import User

async def test_gen():
    db = SessionLocal()
    try:
        # Get a test user (assuming ID 1 exists)
        user = db.query(User).first()
        if not user:
            print("No user found in DB. Please register a user first.")
            return
        
        print(f"Starting parallel sheet generation for user: {user.email}")
        import time
        start = time.time()
        
        # Test with a few models
        models = ["iPhone 15 128GB", "iPhone 15 256GB"]
        sheet = await generate_price_sheet(db, user.id, "TEST PARALLEL SHEET", models=models)
        
        end = time.time()
        print(f"Sheet generated in {end - start:.2f} seconds.")
        print(f"Sheet ID: {sheet.id}, Rows: {len(sheet.rows)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(test_gen())
