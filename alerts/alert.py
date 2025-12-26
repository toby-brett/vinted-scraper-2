import logging
import requests
from typing import List

import domain.models as models
import config.settings as settings

def send_telegram(price, title, link, value):
    """Sends a telegram message to a specific bot on telegram"""

    logging.info("DEAL FOUND - DEAL FOUND - DEAL FOUND")
    message = f"Deal found \n {title} \n Price: £{price} \n Value: £{round(value, 2)} \n {link}"

    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    payload = {"chat_id": settings.CHAT_ID, "text": message}

    try:
        requests.post(url, data=payload)
        logging.info("Sent telegram alert successfully")
    except Exception as e:
        logging.exception(f"Failed to send alert on telegram: {e}")

def alert(listings_evaluated: List[models.EvaluatedListing], price_threshold: float):
    for listing in listings_evaluated:

        value = listing.predicted_value
        price = listing.listing.price
        profit = float(value - (price + settings.EXPENSES))

        if profit > float(price_threshold):
            send_telegram(price, listing.listing.title, listing.listing.url, value)
