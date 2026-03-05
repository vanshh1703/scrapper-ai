from scrapers.base import BaseScraper
from playwright.async_api import async_playwright
import urllib.parse
import re

class FlipkartScraper(BaseScraper):
    def __init__(self, use_proxy=False):
        super().__init__("Flipkart", use_proxy)

    async def scrape(self, query: str):
        query_encoded = urllib.parse.quote_plus(query)
        search_url = f"https://www.flipkart.com/search?q={query_encoded}"
        results = []

        async with async_playwright() as p:
            browser, context = await self.get_browser_context(p)
            try:
                page = await context.new_page()
                await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                await self.human_delay(2000, 4000)
                
                # Different card layouts on Flipkart
                # Layout 1: horizontal cards (e.g. phones), Layout 2: grid cards (e.g. clothing)
                page_title = await page.title()
                print(f"[{self.site_name}] Page Title: {page_title}")
                
                items = page.locator('div[data-id], div.cPHDOP, div._75nlfW')
                count = await items.count()
                print(f"[{self.site_name}] Found {count} items")
                
                for i in range(min(5, count)):
                    item = items.nth(i)
                    if i == 0:
                        with open("flipkart_item_0.html", "w", encoding="utf-8") as f:
                            f.write(await item.inner_html())
                    try:
                        # Extract Name
                        name_elem = item.locator('div.RG5Slk, div.KzDlHZ, a.IRpwTa, a.WKTcLC, div._4rR01T, .s1Q9rs').first
                        if await name_elem.count() == 0:
                            # fallback: find any image and get alt text
                            img_elem = item.locator('img').first
                            product_name = await img_elem.get_attribute('alt') if await img_elem.count() else ""
                        else:
                            product_name = await name_elem.inner_text()
                        
                        if not product_name or len(product_name.strip()) < 3 or "Unknown" in product_name:
                            continue
                        
                        # Extract price (has rupee symbol)
                        # Extract price (has rupee symbol)
                        price = 0
                        price_selectors = ['div.hZ3P6w', 'div.Nx9bqj', 'div._30jeq3', 'div._25b18c div:first-child']
                        for sel in price_selectors:
                            price_elem = item.locator(sel).first
                            if await price_elem.count() > 0:
                                price_str = await price_elem.inner_text()
                                if price_str:
                                    price = int(re.sub(r"[^\d]", "", price_str))
                                    if price > 0: break
                            
                        # Link
                        link_elem = item.locator('a.k7wcnx, a.CGtC98, a[target="_blank"]').first
                        if await link_elem.count() > 0:
                            href = await link_elem.get_attribute('href')
                            product_url = f"https://www.flipkart.com{href}"
                        else:
                            product_url = ""

                        # Image
                        img_elem = item.locator('img').first
                        image_url = await img_elem.get_attribute('src') if await img_elem.count() > 0 else ""

                        # Rating
                        rating_elem = item.locator('div.MKiFS6, div.XQDdHH, div._3LWZlK')
                        rating = await rating_elem.first.inner_text() if await rating_elem.count() > 0 else None

                        # Delivery / Remark
                        delivery_elem = item.locator('div.y4H96k, div._2nMSwX, div.col-5-12 div:nth-child(2)').first
                        delivery_text = await delivery_elem.inner_text() if await delivery_elem.count() > 0 else ""
                        
                        # Color extraction from title
                        colors = ["Black", "White", "Blue", "Natural Titanium", "Desert Titanium", "Pink", "Silver", "Gold", "Starlight", "Midnight"]
                        found_colors = [c for c in colors if c.lower() in product_name.lower()]
                        color_str = ", ".join(found_colors) if found_colors else ""

                        availability = "In Stock" if price > 0 else "Out of stock"
                        if "out of stock" in delivery_text.lower():
                            availability = "Out of stock"

                        results.append({
                            "site": self.site_name,
                            "product_name": product_name.strip(),
                            "current_price": price,
                            "currency": "INR",
                            "rating": rating,
                            "availability": availability,
                            "delivery_info": delivery_text.strip(),
                            "colors": color_str,
                            "url": product_url.split("?")[0], # clean query params
                            "image_url": image_url
                        })
                    except Exception as e:
                        print(f"Error parsing Flipkart item: {e}")
            finally:
                await browser.close()
                
        return [r for r in results if r["current_price"] > 0]
