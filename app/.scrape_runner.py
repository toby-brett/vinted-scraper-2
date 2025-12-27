from datetime import datetime
import time

import logging
import pickle
import argparse
import json
import random

import scraper.browser as browser
import scraper.orchestrator as orchestrator
import storage.adapter as adapter
import storage.storer as storer
import scraper.cleaner as cleaner
import utils.utils as utils
import vision.evaluator as evaluator
import alerts.alert as alert
import config.settings as settings
from scraper.browser import BlockedError

parser = argparse.ArgumentParser()
parser.add_argument("--job", type=str)
parser.add_argument("--job-file", type=str, help="Path to job JSON file")
args = parser.parse_args()

if args.job_file:
    with open(args.job_file, "r") as f:
        job = json.load(f)
elif args.job:
    job = json.loads(args.job)
else:
    raise SystemExit("Must provid --job or --job-file")

search, brand, item, task, id_path, data_path, price_threshold, model_path, model_type, num_classes, population_metrics, value_dict = utils.parse_job(job)
url = f'https://www.vinted.co.uk/catalog?search_text={search}&order=newest_first&page=1'

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger(__name__)
    while True:
        scrapes = 0
        hour = datetime.now().hour
        if not (0 <= hour < 7):
            with browser.BrowserSession() as SESSION:
                data_storer = storer.HDF5Storer(data_path)
                logging.debug(f"Initialized storer")
                seen_ids = utils.load_ids(id_path)
                logging.debug(f"Loaded IDs")
                while True:
                    scrapes += 1
                    tries = 0
                    while tries < settings.MAX_RETRIES:
                        logging.info("New scraping session")
                        try:
                            listings, tries = orchestrator.scrape_listings([url], SESSION, tries)
                            logging.info(f"Scraped listings")
                            break
                        except Exception as e:
                            logging.exception("Cloudflare detected: pausing for one hour")
                            time.sleep(60 * 60)
                            break
                    else:
                        logging.error("Max tries exceeded")
                        raise utils.FatalScraperError("Page scraping blocked")

                    try:
                        listings_filtered = cleaner.filter_listings(listings, seen_ids, brand)
                        logging.info(f"filtered listings")
                    except Exception as e:
                        logging.exception(f"Filtering Listings Failed: {e}")

                    new_ids = cleaner.get_ids_from_listings(listings_filtered)
                    utils.add_ids(id_path, new_ids)            # adds ids to the id file

                    seen_ids.update(new_ids)            # adds them to the id list in mem
                    if len(listings_filtered) > 0:
                        try:
                            if task == "alert":
                                try:
                                    if model_type == "classification":
                                        model = evaluator.load_model(path=model_path, model_type='classification')
                                        logging.info(f"Loaded model")
                                        listings_evaluated = evaluator.evaluate_class(listings=listings_filtered, model=model, value_dict=value_dict)
                                        logging.info(f"Evaluated listings")
                                    elif model_type == "regression":
                                        model = evaluator.load_model(path=model_path, model_type='regression')
                                        logging.info(f"Loaded model")
                                        listings_evaluated = evaluator.evaluate_price(listings=listings_filtered, model=model, population_metrics=population_metrics)
                                        logging.info(f"Evaluated listings")
                                except Exception as e:
                                    logging.exception(f"Failed to evaluate batches: {e}")
                                try:
                                    alert.alert(listings_evaluated, price_threshold)
                                    logging.info(f"Sent alert")
                                except Exception as e:
                                    logging.exception(f"Scrape_runner.py: Failed to alert: {e}")
                            image_batch, metadata_batch = adapter.listings_to_batches(listings_filtered)
                            logging.info(f"Created batches")
                        except Exception as e:
                            logging.exception(f"scrape_runner.py: Failed to create batches: {e}")
                            continue
                        try:
                            data_storer.append_batch(image_batch, metadata_batch)
                            logging.info(f"Saved batches, added {len(image_batch)}, currently holding {len(data_storer)} files")
                        except Exception as e:
                            logging.exception(f"Failed to store data: {e}")
                            continue
                    else:
                        logging.info(f"No new items found")

                    sleep = random.randint(settings.INTERVAL, 2*settings.INTERVAL)
                    time.sleep(sleep)
                    logging.info(f"Waiting {sleep} second")

                    if 0 < datetime.now().hour < 7:
                        break

                    if scrapes > settings.SCRAPES_TILL_RESET:
                        logging.info(f"Scraped {settings.SCRAPES_TILL_RESET} times, resetting browser")
                        break
        else:
            logging.info("Outside working hours, sleeping ...")
            time.sleep(60 * 30)