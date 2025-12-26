from typing import List
import logging

import domain.models as models
import scraper.parser as parser
import scraper.browser as browser

def scrape_listings(urls: List[str], SESSION: browser.BrowserSession, tries: int) -> (List[models.Listing], int):
    """Takes a list of search URLs, and returns a list of
    all the listing objects found on that page"""
    listings = []

    try:
        for url in urls:
            try:
                page_soup = SESSION.fetch_html(url)
            except Exception as e:
                logging.exception(f"Failed to fetch {url}: {e}")
                continue            # skips to next page
            try:
                page_listings = parser.Parser.parse_page(page_soup)
            except Exception as e:
                logging.exception(f"Failed to parse {url}: {e}")
                continue            # skips to next page
            for listing_soup in page_listings:
                try:
                    listing = parser.Parser.parse_listing(listing_soup)
                    if listing:     # final check for None
                        listings.append(listing)
                except Exception as e:
                    logging.exception(f"Failed to parse {url}: {e}")
                    continue        # skips to next listing

    except Exception as e:
        logging.exception(f"Scraping page failed, starting new session and retrying {e}")
        return None, tries + 1

    return listings, tries

