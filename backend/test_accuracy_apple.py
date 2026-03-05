import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from core.database import SessionLocal
from services.comparison import search_and_compare

async def test_accuracy():
    db = SessionLocal()
    try:
        query = "AirPods Pro 2"
        print(f"Testing accuracy for query: {query}")
        
        # We need a user ID for SearchHistory
        from models.user import User
        user = db.query(User).first()
        if not user:
            print("No user found.")
            return

        results = await search_and_compare(db, query, user.id)
        
        print(f"\nResults for {query}:")
        for r in results.get('results', []):
            print(f" - [{r['site']}] {r['product_name']}: {r['current_price']} INR")
            # Check if any should have been filtered but weren't
            EXCLUSION_KEYWORDS = ['for', 'compatible', 'replacement', 'clone', 'fake', 'copy', 'dummy', 'cover', 'case', 'protector']
            if any(k in r['product_name'].lower() for k in EXCLUSION_KEYWORDS):
                print(f"   WARNING: Found exclusion keyword in results: {r['product_name']}")

    finally:
        db.close()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(test_accuracy())
