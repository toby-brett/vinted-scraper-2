import time

import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import logging
from zenrows import ZenRowsClient

from config.settings import zr_client_id


def random_user_agent():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
    ]
    return random.choice(agents)

class BrowserSession:
    def __init__(self):
        """Starts the browser session, loads context and page"""

        self.client = ZenRowsClient(zr_client_id)

        self.instance = sync_playwright().start()                               # playwright instance, manages playwright session
        self.browser = self.instance.chromium.launch(
            headless=False,  # HEADLESS = HIGH DETECTION on Vinted; keep it visible
            slow_mo=50,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--ignore-certificate-errors",
            ],
        )
        self.context = self.browser.new_context(                                # separate browser profile
            user_agent=random_user_agent(),
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
            response = self.client.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            return soup
            # self.page.goto(url, timeout=30000)
            # self.page.wait_for_selector("div.feed-grid__item", timeout=10000) # waits for js to load content
            # soup = BeautifulSoup(self.page.content(), "lxml")
            # return soup
        except Exception as e:
            logging.error(f"Unhandled exception when fetching html {e}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.page.close()
        self.context.close()
        self.browser.close()
        self.instance.stop()
