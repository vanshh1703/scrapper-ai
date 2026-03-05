import asyncio
import random
from playwright.async_api import async_playwright, Playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
]

class BaseScraper:
    def __init__(self, site_name: str, use_proxy: bool = False):
        self.site_name = site_name
        self.use_proxy = use_proxy
        
    async def get_browser_context(self, p: Playwright):
        # Setup Proxy if required
        # proxy = {"server": "http://user:pass@host:port"} if self.use_proxy else None
        
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
        )
        return browser, context

    async def human_delay(self, min_ms: int = 1000, max_ms: int = 3000):
        delay = random.uniform(min_ms, max_ms) / 1000.0
        await asyncio.sleep(delay)

    async def scrape(self, query: str):
        # Must return list of ProductCreate dicts:
        # {site, product_name, price, currency, rating, availability, url, image_url}
        raise NotImplementedError("Subclasses must implement scrape()")
