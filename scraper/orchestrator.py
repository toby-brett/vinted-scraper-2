from typing import List
import logging

from domain.models import *
from scraper.parser import Parser
from scraper.browser import *

def scrape_listings(urls: List[str]) -> List[Listing]:
    """Takes a list of search URLs, and returns a list of
    all the listing objects found on that page"""
    listings = []
    with BrowserSession() as session:
        for url in urls:
            try:
                page_soup = session.fetch_html(url)
            except Exception as e:
                logging.error(f"Failed to fetch {url}: {e}")
                continue            # skips to next page
            try:
                page_listings = Parser.parse_page(page_soup)
            except Exception as e:
                logging.error(f"Failed to parse {url}: {e}")
                continue            # skips to next page
            for listing_soup in page_listings:
                try:
                    listing = Parser.parse_listing(listing_soup)
                    if listing:     # final check for None
                        listings.append(listing)
                except Exception as e:
                    logging.warning(f"Failed to parse {listing}: {e}")
                    continue        # skips to next listing
    return listings

