import logging
import requests
from typing import List

import domain.models as models
import config.settings as settings
from domain.models import EvaluatedListing


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

def alert(listings_evaluated: List[models.EvaluatedListing], price_threshold: float, max_price: float, min_condition: str) -> None:
    """
    Takes a list of evaluated listings, and filters them to alert based on business logic
    :param min_condition: worst condition allowed
    :param max_price: the maximum price a listing can be and still trigger an alert
    :param listings_evaluated: a list of listings, of the structure model.EvaluatedListing
    :param price_threshold: float, the predetermined threshold of profit at which an alert should be sent
    :return: None
    """
    for listing in listings_evaluated:

        price = listing.listing.price
        value = listing.predicted_value

        logging.info("Checking listing meets requirements")
        if requirements(price_threshold, min_condition, max_price, listing):
            send_telegram(price, listing.listing.title, listing.listing.url, value)

def requirements(min_returns: float, min_condition: str, max_price: float, evaluated_listing: EvaluatedListing):
    """
    Checks that some base requirements are met
    :param evaluated_listing: the listing
    :param min_returns: least return acceptable to trigger an alert
    :param min_condition: worst condition to trigger alert
    :param max_price: highest price to trigger alert
    :return: bool - good or not
    """
    price = evaluated_listing.listing.price
    value = evaluated_listing.predicted_value
    condition = evaluated_listing.listing.condition.lower()
    min_condition = min_condition.lower()

    profit_threshold = price * float(min_returns)
    profit = float(value - (price + settings.EXPENSES))

    logging.info(f"Listing: {evaluated_listing.listing.url} evaluated. Price: {price}, Value: {value}, Profit: {profit}, Condition: {condition}")

    if profit > profit_threshold and float(price) <= float(max_price) and settings.CONDITION_DICT[condition] >= settings.CONDITION_DICT[min_condition]:
        return True

    logging.info(f"Returns good: {profit > profit_threshold}, Price good: {float(price) <= float(max_price)}, Condition good: {settings.CONDITION_DICT[condition] >= settings.CONDITION_DICT[min_condition]}")
    return False


def alert_threshold(listings_evaluated: List[models.EvaluatedListing], price_threshold, max_price, min_condition):
    for listing in listings_evaluated:
        logging.info(
        f"Listing: {listing.listing.url} evaluated. Price: {listing.listing.price}, Threshold: {price_threshold}")
        if listing.listing.price < price_threshold:
            send_telegram(listing.listing.price, listing.listing.title, listing.listing.url, 0)

    return None