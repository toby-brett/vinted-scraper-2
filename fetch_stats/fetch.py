
import argparse
import re

import scraper.orchestrator as orchestrator
from scraper import browser
from flask import Flask, request, jsonify

app = Flask(__name__)

CRITERIA_MET_TO_DEAL = 0.4
AVERAGE_SALE_SCALER = 0.8
SCALER = 0.2


@app.get("/api/health")
def health():
    return {"ok": True}


def get_listings(brand, item):
    url = f"https://www.vinted.co.uk/catalog?search_text={brand}%{item}&order=newest_first&page=1"
    with browser.BrowserSession() as session:
        listings, _ = orchestrator.scrape_listings([url], session, 0)
        return listings


def compute_volume(brand: str, item: str) -> float:
    """
    Pure function: can be used by CLI and by Flask route.
    No Flask request context here.
    """
    url = f"https://www.vinted.co.uk/catalog?search_text={brand}%{item}&order=newest_first&page=1"

    with browser.BrowserSession() as session:
        listings, _ = orchestrator.scrape_listings([url], session, 0)

        if not listings:
            return 0

        for i in range(len(listings)):
            last_listing = listings[-(i + 1)]

            listing_url = f"https://www.vinted.co.uk/items/{last_listing.listing_id}"
            listing_soup = session.fetch_listing_html(listing_url)

            container = listing_soup.find("div", attrs={"data-testid": "item-attributes-upload_date"})
            uploaded_span = container.select_one("span.web_ui__Text__bold") if container else None
            time_text = uploaded_span.get_text(strip=True).lower() if uploaded_span else None

            print("oldest:", time_text)

            if not time_text:
                continue

            if time_text == "just now":
                return len(listings) * 1440

            if "min" in time_text:
                num = re.search(r"\d+", time_text)
                minutes = int(num.group()) if num else 1
                return len(listings) * (1440 / minutes)

            if "hour" in time_text:
                if "an" in time_text:
                    return len(listings) * 12
                num = re.search(r"\d+", time_text)
                hours = int(num.group()) if num else 1
                return len(listings) * (12 / hours)

            return len(listings)

        # If all timestamps were None and we never returned:
        return len(listings)


@app.get("/api/volume_vinted")
def api_volume():
    brand = (request.args.get("brand") or "").strip()
    item = (request.args.get("item") or "").strip()

    if not brand:
        return jsonify(error="brand is required"), 400

    vol = compute_volume(brand, item)
    return jsonify(brand=brand, item=item, volume=vol)


def get_deals_volume(listings, daily_vol, price):
    deals = 0
    vol = 0

    for listing in listings:
        vol += 1
        if listing.price <= price:
            deals += 1

    proportion = (deals / vol) if vol else 0
    daily_deals = proportion * daily_vol
    daily_deals *= 2  # assuming twice have gone

    return daily_deals * CRITERIA_MET_TO_DEAL


def get_deal_listings(listings, price):
    return [l for l in listings if l.price < price]


def get_average_price(listings):
    if not listings:
        return 0
    return sum(l.price for l in listings) / len(listings)


def get_average_profit(listings, deal_listings, threshold):
    average_price = get_average_price(listings)
    return (average_price * AVERAGE_SALE_SCALER) - (threshold + 2.99 + 0.99)


def get_daily_profit(average_profit, vol_deals):
    return average_profit * vol_deals


def main(brand, item, price):
    listings = get_listings(brand, item)
    deal_listings = get_deal_listings(listings, price)

    daily_vol = compute_volume(brand, item)  # IMPORTANT: use pure function
    deals_vol = get_deals_volume(listings, daily_vol, price)

    average_price = get_average_price(listings)
    average_profit = get_average_profit(listings, deal_listings, price)

    daily_profit = get_daily_profit(average_profit, deals_vol) * SCALER

    print(
        f"Daily volume: {daily_vol}, Daily deals volume: {deals_vol}, "
        f"Monthly profit: {daily_profit * 31}, Average profit: {average_profit}, "
        f"Average price: {average_price}"
    )


if __name__ == "__main__":
    # Choose ONE of these modes at a time.

    # 1) Run as an API server:
    app.run(host="127.0.0.1", port=5000, debug=True)

    # 2) Run as CLI/script:
    # main("Stussy", "", 15)