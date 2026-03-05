from scrapers.base import BaseScraper
from playwright.async_api import async_playwright
import urllib.parse
import re

class JioMartScraper(BaseScraper):
    def __init__(self, use_proxy=False):
        super().__init__("Jio Mart", use_proxy)

    async def scrape(self, query: str):
        query_encoded = urllib.parse.quote_plus(query)
        search_url = f"https://www.jiomart.com/search/{query_encoded}"
        results = []

        async with async_playwright() as p:
            browser, context = await self.get_browser_context(p)
            try:
                page = await context.new_page()
                await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                await self.human_delay(2000, 4000)
                
                # Check for item containers
                items = page.locator('.jm-col-4, .plp-card-container')
                count = await items.count()
                
                for i in range(min(5, count)):
                    item = items.nth(i)
                    try:
                        title_el = item.locator(".plp-card-details-name").first
                        if await title_el.count() == 0:
                            title_el = item.locator(".jm-body-m-bold").first
                            
                        product_name = await title_el.inner_text() if await title_el.count() else ""
                        
                        if not product_name or len(product_name.strip()) < 3 or "Unknown" in product_name:
                            continue

                        price_selectors = [".jm-heading-xxs", ".final-price", ".jm-body-m-bold.text-black", ".price-box"]
                        price = 0
                        for sel in price_selectors:
                            price_el = item.locator(sel).first
                            if await price_el.count():
                                price_str = await price_el.inner_text()
                                if price_str:
                                    price = int(re.sub(r"[^\d]", "", price_str))
                                    if price > 0: break
                        
                        link_el = item.locator("a").first
                        product_url = await link_el.get_attribute("href") if await link_el.count() else ""
                        if product_url and not product_url.startswith("http"):
                            product_url = "https://www.jiomart.com" + product_url
                            
                        img_el = item.locator("img").first
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
                        print(f"Error parsing Jio Mart item: {e}")
            finally:
                await browser.close()
                
        return results
