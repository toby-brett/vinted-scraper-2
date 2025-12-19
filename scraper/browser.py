from playwright.sync_api import sync_playwright

def start_browser():
    """Starts the browser session, loads context and page"""

    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)