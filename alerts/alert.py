import logging
import requests
from typing import List

import domain.models as models
import config.settings as settings

def send_telegram(price: float, title: str, link: str, value: float) -> None:
    """
    Sends a telegram message when an item deemed profitable is found
    :param price: float, the price that the listing is set for
    :param title: string, the name of the listing
    :param link: string, the url to the listing, so it can be sent in the notification
    :param value: float, the price evaluated by the ML model
    :return: None
    """

    logging.info("DEAL FOUND - DEAL FOUND - DEAL FOUND")
    message = f"Deal found \n {title} \n Price: £{price} \n Value: £{round(value, 2)} \n {link}"

    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    payload = {"chat_id": settings.CHAT_ID, "text": message}

    try:
        requests.post(url, data=payload)
        logging.info("Sent telegram alert successfully")
    except Exception as e:
        logging.exception(f"Failed to send alert to telegram: {e}")

def alert(listings_evaluated: List[models.EvaluatedListing], price_threshold: float) -> None:
    """
    Takes a list of evaluated listings, and filters them to alert based on business logic
    :param listings_evaluated: a list of listings, of the structure model.EvaluatedListing
    :param price_threshold: float, the predetermined threshold of profit at which an alert should be sent
    :return: None
    """
    for listing in listings_evaluated:

        value = listing.predicted_value
        price = listing.listing.price
        profit = float(value - (price + settings.EXPENSES))
        logging.info(f"Listing: {listing.listing.url} evaluated. Price: {price}, Value: {value}, Profit: {profit}")

        logging.info(f"IMPORTANT: {price}, {price_threshold}, {price * float(price_threshold)}, {profit}")
        if profit > price * float(price_threshold):
            send_telegram(price, listing.listing.title, listing.listing.url, value)
