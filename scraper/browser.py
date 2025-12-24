import time

import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import asyncio
import logging

from utils.utils import *

def random_user_agent():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
    ]
    return random.choice(agents)

class BrowserSession:
    def __init__(self):
        self.instance = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        """So can us with BrowserSession() as session
        Starts the browser session, loads context and page"""

        logging.info("Checking for asyncio loop...")
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                logging.warning("A loop is already running")
            else:
                logging.warning("A loop exists but is not running")
        except Exception as e:
            logging.info(f"No loop detected: {e}")

        self.instance = sync_playwright().start()  # playwright instance, manages playwright session
        self.browser = self.instance.chromium.launch(
            headless=True,  # HEADLESS = HIGH DETECTION on Vinted; keep it visible
            slow_mo=50,
            # proxy={"server": proxy_str},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--ignore-certificate-errors",
            ],
        )
        self.context = self.browser.new_context(  # separate browser profile
            user_agent=random_user_agent(),
            locale="en-GB",
            timezone_id="Europe/London",
            viewport={"width": 1366, "height": 768},
            device_scale_factor=1,
            java_script_enabled=True,
        )

        self.page = self.context.new_page()  # single browser tab
        stealth_sync(self.page)

        return self

    def fetch_html(self, url):
        try:
            self.page.goto(url, timeout=60000, wait_until="load")

            # If Cloudflare challenge appears, wait it out
            if "Just a moment" in self.page.title():
                logging.info("Cloudflare challenge detected, waiting...")

                # Wait until challenge iframe disappears OR URL changes
                self.page.wait_for_function(
                    "() => !document.querySelector('iframe[src*=\"challenges.cloudflare.com\"]')",
                    timeout=60000
                )

            # Wait for actual Vinted content
            self.page.wait_for_selector(
                "div.feed-grid__item",
                timeout=30000
            )

            html = self.page.content()
            return BeautifulSoup(html, "lxml")

        except Exception as e:
            logging.error(f"Unhandled exception when fetching html {e}")
            return None

    def reset_page(self):
        if self.page:
            self.page.close()
        self.page = self.browser.new_page()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.page.close()
        self.context.close()
        self.browser.close()
        self.instance.stop()

    def close(self):
        self.page.close()
        self.context.close()
        self.browser.close()
        self.instance.stop()
