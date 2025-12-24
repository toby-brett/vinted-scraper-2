import logging
import requests
from typing import List

from domain.models import *
from config.settings import *

def send_telegram(price, title, link, value):
    """Sends a telegram message to a specific bot on telegram"""

    logging.info("DEAL FOUND - DEAL FOUND - DEAL FOUND")
    message = f"Deal found \n {title} \n Price: £{price} \n Value: £{round(value, 2)} \n {link}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}

    requests.post(url, data=payload)

def alert(listings_evaluated: List[EvaluatedListing], price_threshold: float):
    for listing in listings_evaluated:

        value = listing.predicted_value
        price = listing.listing.price
        profit = float(value - (price + EXPENSES))

        if profit > float(price_threshold):
            send_telegram(price, listing.listing.title, listing.listing.url, value)
