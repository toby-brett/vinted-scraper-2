import time
import datetime

from typing import List
import logging

import domain.models as models

class Parser:
    @staticmethod
    def parse_page(page_soup) -> List[str]:
        """Parses the webpage for all the vinted listings, avoiding advertisements"""

        if page_soup is None:
            raise ValueError("parse_page received None (fetch likely failed or was blocked).")

        listings = page_soup.find_all("div", {"class": "feed-grid__item"})
        product_listings = [
            listing for listing in listings
            if listing.find("div", {"class": "new-item-box__container"})
        ]
        return product_listings

    @staticmethod
    def parse_inside_listing(listing_soup):
        print("LISTING")
        print(listing_soup)

    @staticmethod
    def parse_listing(listing_soup) -> models.Listing:
        """Parses each listing, returning item_id, title, price, image_src, size, brand, condition, url and time"""
        try:
            brand = condition = size = None

            img_tag = listing_soup.find("img")
            title_tag = (
                    listing_soup.find("a", class_="new-item-box__overlay new-item-box__overlay--clickable")
                    or listing_soup.select_one("img[alt]")
            )
            price_tag = listing_soup.find("p", {"data-testid": lambda x: x and "price-text" in x})
            link_tag = listing_soup.find("a", {"data-testid": lambda x: x and "--overlay-link" in x})

            image_src = img_tag.get("src") or img_tag.get("data-src")

            if title_tag is None:
                html_preview = (str(listing_soup)[:2000] if listing_soup else "NO SOUP")
                logging.error(f"Parse_listings: Title tag missing: {html_preview}")
                return None

            if title_tag.name == "img": # from img alt
                title_text = title_tag.get("alt", "").strip()
            else:
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

            return models.Listing(item_id, title, price, image_src, size, brand, condition, url, datetime.datetime.now())

        except Exception as e:
            logging.exception(f"Failed to generate listing due to exception {e}")
            return None