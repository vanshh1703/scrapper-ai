from scrapers.base import BaseScraper
from playwright.async_api import async_playwright
import urllib.parse
import re

class AmazonScraper(BaseScraper):
    def __init__(self, use_proxy=False):
        super().__init__("Amazon India", use_proxy)

    async def scrape(self, query: str):
        query_encoded = urllib.parse.quote_plus(query)
        search_url = f"https://www.amazon.in/s?k={query_encoded}"
        results = []

        async with async_playwright() as p:
            browser, context = await self.get_browser_context(p)
            try:
                page = await context.new_page()
                await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                await self.human_delay(2000, 4000)
                
                # Check for CAPTCHA
                if await page.locator("form[action='/errors/validateCaptcha']").count() > 0:
                    print(f"[{self.site_name}] CAPTCHA detected.")
                    return results

                items = page.locator('div[data-component-type="s-search-result"], .s-result-item[data-asin]:not([data-asin=""]), .s-result-item')
                count = await items.count()
                
                # Limit to top 5 results per site
                for i in range(min(5, count)):
                    item = items.nth(i)
                    
                    try:
                        # Title extraction - multiple fallbacks
                        product_name = ""
                        title_selectors = ["h2 a span", "h2 a", "span.a-size-medium.a-color-base.a-text-normal", ".s-line-clamp-2"]
                        for sel in title_selectors:
                            title_el = item.locator(sel).first
                            if await title_el.count():
                                product_name = await title_el.inner_text()
                                if product_name and len(product_name) > 5: break
                        
                        if not product_name or len(product_name) < 3:
                            continue

                        # Price extraction
                        price = 0
                        price_el = item.locator(".a-price-whole").first
                        if await price_el.count():
                            price_str = await price_el.inner_text()
                            price = int(re.sub(r"[^\d]", "", price_str))
                        else:
                            # Fallback for some layouts
                            price_el = item.locator(".a-offscreen").first
                            if await price_el.count():
                                price_str = await price_el.inner_text()
                                price = int(re.sub(r"[^\d]", "", price_str))
                        
                        link_el = item.locator("h2 a")
                        product_url = "https://www.amazon.in" + await link_el.get_attribute("href") if await link_el.count() else ""
                        
                        img_el = item.locator("img.s-image")
                        image_url = await img_el.get_attribute("src") if await img_el.count() else ""
                        
                        # Delivery info - more robust selectors
                        delivery_info = ""
                        del_selectors = [
                            ".a-color-base.a-text-bold",
                            "span[aria-label*='Get it by']",
                            ".s-delivery-instructions",
                            "span.a-text-bold:has-text('delivery')"
                        ]
                        for selector in del_selectors:
                            el = item.locator(selector).first
                            if await el.count():
                                if selector == "span[aria-label*='Get it by']":
                                    delivery_info = await el.get_attribute("aria-label")
                                else:
                                    delivery_info = await el.inner_text()
                                if delivery_info: break

                        # Basic color extraction from title
                        colors_list = ["Black", "White", "Blue", "Natural Titanium", "Desert Titanium", "Pink", "Silver", "Gold", "Starlight", "Midnight"]
                        found_colors = [c for c in colors_list if c.lower() in product_name.lower()]
                        color_str = ", ".join(found_colors) if found_colors else ""

                        # Availability check
                        availability = "In Stock"
                        oos_locator = item.locator("span[aria-label='Currently unavailable.'], .a-color-price:has-text('Currently unavailable')")
                        if await oos_locator.count() > 0 or price == 0:
                            availability = "Out of Stock"

                        # Rating fallback
                        rating_el = item.locator("span.a-icon-alt").first
                        rating = await rating_el.inner_text() if await rating_el.count() else "No rating"

                        results.append({
                            "site": self.site_name,
                            "product_name": product_name.strip(),
                            "current_price": price,
                            "currency": "INR",
                            "rating": rating,
                            "availability": availability,
                            "delivery_info": delivery_info.strip(),
                            "colors": color_str,
                            "url": product_url.split("?")[0], # clean tracker
                            "image_url": image_url
                        })
                    except Exception as e:
                        print(f"Error parsing Amazon item: {e}")
                        continue
            finally:
                await browser.close()
                
        return results
