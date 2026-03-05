from scrapers.base import BaseScraper
from playwright.async_api import async_playwright
import urllib.parse
import re

class VijaySalesScraper(BaseScraper):
    def __init__(self, use_proxy=False):
        super().__init__("Vijay Sales", use_proxy)

    async def scrape(self, query: str):
        query_encoded = urllib.parse.quote_plus(query)
        search_url = f"https://www.vijaysales.com/search/{query_encoded}"
        results = []

        async with async_playwright() as p:
            browser, context = await self.get_browser_context(p)
            try:
                page = await context.new_page()
                await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                await self.human_delay(2000, 4000)
                
                # Check for item containers
                items = page.locator('.vsprcd-row')
                count = await items.count()
                
                for i in range(min(5, count)):
                    item = items.nth(i)
                    try:
                        title_el = item.locator(".vsprcd-nm")
                        product_name = await title_el.inner_text() if await title_el.count() else ""
                        
                        if not product_name or len(product_name.strip()) < 3 or "Unknown" in product_name:
                            continue

                        price_el = item.locator(".vsprcd-prce, .vsp-price").first
                        price_str = await price_el.inner_text() if await price_el.count() else "0"
                        price = int(re.sub(r"[^\d]", "", price_str)) if price_str else 0
                        
                        link_el = item.locator("a").first
                        product_url = await link_el.get_attribute("href") if await link_el.count() else ""
                        if product_url and not product_url.startswith("http"):
                            product_url = "https://www.vijaysales.com" + product_url
                            
                        img_el = item.locator("img.vsprcd-img")
                        image_url = await img_el.get_attribute("src") if await img_el.count() else ""
                        
                        # Availability
                        availability = "In Stock"
                        if price == 0:
                            availability = "Out of Stock"

                        results.append({
                            "site": self.site_name,
                            "product_name": product_name.strip(),
                            "current_price": price,
                            "currency": "INR",
                            "rating": "No rating",
                            "availability": availability,
                            "delivery_info": "Standard Delivery",
                            "colors": "",
                            "url": product_url.split("?")[0],
                            "image_url": image_url
                        })
                    except Exception as e:
                        print(f"Error parsing Vijay Sales item: {e}")
            finally:
                await browser.close()
                
        return results
