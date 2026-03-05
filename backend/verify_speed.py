import asyncio
import sys
import os
import time

# Ensure we are in the backend directory for relative imports and sqlite path
# The script is expected to be run from 'backend' directory

from core.database import SessionLocal, Base, engine
from services.sheet_generator import generate_price_sheet
from models.user import User

async def test_gen():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Get or create a test user
        user = db.query(User).first()
        if not user:
            print("Creating a temporary test user...")
            from models.user import User
            user = User(email="test@example.com", hashed_password="...", role="pro")
            db.add(user)
            db.commit()
            db.refresh(user)
        
        print(f"Starting parallel sheet generation for user: {user.email}")
        start = time.time()
        
        # Test with a few models
        models = ["iPhone 15 128GB", "iPhone 15 256GB"]
        sheet = await generate_price_sheet(db, user.id, "TEST PARALLEL SHEET", models=models)
        
        end = time.time()
        print(f"Sheet generated in {end - start:.2f} seconds.")
        print(f"Sheet ID: {sheet.id}, Rows: {len(sheet.rows)}")
        for row in sheet.rows:
            print(f" - {row.model_name} at {row.retailer}: {row.mop_online} ({row.remark})")
        
    finally:
        db.close()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(test_gen())
