from scraper.orchestrator import *
from storage.adapter import *
from storage.storer import *
from scraper.cleaner import *
from utils.utils import *
from vision.evaluator import *
from alerts.alert import *

with open("tests/page_1.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

page_listings = Parser.parse_page(soup)
listings = []
for listing_soup in page_listings:
    try:
        listing = Parser.parse_listing(listing_soup)
        if listing:  # final check for None
            listings.append(listing)
    except Exception as e:
        logging.warning(f"Failed to parse {listing_soup}: {e}")
        continue  # skips to next listing

task = "alert"

if len(listings) > 0:
    try:
        if task == "alert":
            try:
                listings_evaluated = evaluate(listings=listings, model_type="classification", model_path="classification/stussy_tshirt.pth",
                                              population_metrics=(19, 8), num_classes=18,
                                              value_dict={
                                                          "0": 17,
                                                          "1": 17,
                                                          "2": 14,
                                                          "3": 17,
                                                          "4": 19,
                                                          "5": 0,
                                                          "6": 16,
                                                          "7": 18,
                                                          "8": 20,
                                                          "9": 0,
                                                          "10": 17,
                                                          "11": 18,
                                                          "12": 0,
                                                          "13": 19,
                                                          "14": 18,
                                                          "15": 15,
                                                          "16": 0,
                                                          "17": 18})
            except Exception as e:
                logging.error(f"Scrape_runner.py: Failed to evaluate batches: {e}")
            try:
                alert(listings_evaluated, price_threshold=5)
            except Exception as e:
                logging.error(f"Scrape_runner.py: Failed to alert: {e}")
        image_batch, metadata_batch = listings_to_batches(listings)
        logging.info(f"Created batches")
    except Exception as e:
        logging.error(f"scrape_runner.py: Failed to create batches: {e}")

else:
    logging.info(f"No new items found: {datetime.now()}")
