from scraper.browser import BrowserSession  # or wherever you saved your class
from scraper.parser import *

url = "https://www.vinted.co.uk/catalog?search_text=stussy+shirt&order=newest_first&page=1"

with BrowserSession() as session:
    soup = session.fetch_html(url)
    listings = Parser.parse_page(soup)
    for listing in listings:
        listing_object = Parser.parse_listing(listing)
        # print(listing_object.listing_id)