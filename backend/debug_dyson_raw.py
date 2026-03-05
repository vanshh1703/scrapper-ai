import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from scrapers.amazon import AmazonScraper
from scrapers.flipkart import FlipkartScraper

async def test_raw_dyson():
    amazon = AmazonScraper()
    flipkart = FlipkartScraper()
    
    print("Searching Amazon for Dyson...")
    amz_res = await amazon.scrape("Dyson")
    print(f"Amazon found {len(amz_res)} items")
    for r in amz_res[:3]:
        print(f" - {r['product_name']}")

    print("\nSearching Flipkart for Dyson...")
    fk_res = await flipkart.scrape("Dyson")
    print(f"Flipkart found {len(fk_res)} items")
    for r in fk_res[:3]:
        print(f" - {r['product_name']}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(test_raw_dyson())
