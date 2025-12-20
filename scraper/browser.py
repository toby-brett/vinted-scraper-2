import time

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserSession:
    def __init__(self):
        """Starts the browser session, loads context and page"""

        self.instance = sync_playwright().start()                               # playwright instance, manages playwright session
        self.browser = self.instance.chromium.launch(headless=True)             # actual browser used
        self.context = self.browser.new_context(                                # separate browser profile
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            locale="en-GB",
            timezone_id="Europe/London",
            viewport={"width": 1366, "height": 768},
            device_scale_factor=1,
            java_script_enabled=True,
        )
        self.page = self.context.new_page()                                     # single browser tab
        stealth_sync(self.page)

    def __enter__(self):
        """So can us with BrowserSession() as session"""
        return self

    def fetch_html(self, url):
        try:
            self.page.goto(url, timeout=30000)
            self.page.wait_for_selector("div.feed-grid__item", timeout=5000) # waits for js to load content
            soup = BeautifulSoup(self.page.content(), "lxml")
            return soup
        except Exception as e:
            logging.error(f"Unhandled exception when fetching html {e}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.page.close()
        self.context.close()
        self.browser.close()
        self.instance.stop()
