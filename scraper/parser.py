import time

from typing import List
import logging

from domain.models import *

class Parser:
    @staticmethod
    def parse_page(page_soup) -> List[str]:
        """Parses the webpage for all the vinted listings, avoiding advertisements"""
        listings = page_soup.find_all("div", {"class": "feed-grid__item"})
        # filter out non-product items
        product_listings = [
            listing for listing in listings
            if listing.find("div", {"class": "new-item-box__container"})
        ]
        return product_listings                   # list of html listings

    @staticmethod
    def parse_listing(listing_soup) -> Listing:
        """Parses each listing, returning item_id, title, price, image_src, size, brand, condition, url and time"""
        try:
            brand = condition = size = None

            img_tag = listing_soup.find("img")
            title_tag = listing_soup.find("a", {"class": "new-item-box__overlay new-item-box__overlay--clickable"})
            price_tag = listing_soup.find("p", {"data-testid": lambda x: x and "price-text" in x})
            link_tag = listing_soup.find("a", {"data-testid": lambda x: x and "--overlay-link" in x})

            image_src = img_tag.get("src") or img_tag.get("data-src")

            title_text = title_tag.get("title", "").strip()
            deconstructed_title = [part.strip() for part in title_text.split(",")]

            title = deconstructed_title[0].strip()
            for field in deconstructed_title:
                field_lower = field.lower()
                if field_lower.startswith("brand:"):
                    brand = field.split(":", 1)[1].strip()
                elif field_lower.startswith("condition:"):
                    condition = field.split(":", 1)[1].strip()
                elif field_lower.startswith("size:"):
                    size = field.split(":", 1)[1].strip()

            price = float(price_tag.text.strip().replace("£", ""))
            url = link_tag.get("href")
            item_id = link_tag.get("href").split("/")[4][:10]

            return Listing(item_id, title, price, image_src, size, brand, condition, url, datetime.utcnow())

        except Exception as e:
            logging.log(f"Failed to generate listing due to exception {e}")
            return None