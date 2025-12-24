import logging

from scraper.browser import BrowserSession

def fetch_page(session, url):
    try:
        soup = session.fetch_html(url)
        return soup
    except Exception as e:
        logging.error(f"Failed to fetch page: {url}, unhandled exception: {e}")
        raise

