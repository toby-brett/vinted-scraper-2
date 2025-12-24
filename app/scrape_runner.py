import logging
import pickle
import argparse
import json

from scraper.orchestrator import *
from storage.adapter import *
from storage.listings import *
from scraper.cleaner import *
from utils.utils import *
from vision.evaluater import *
from alerts.alert import *

parser = argparse.ArgumentParser()
parser.add_argument("--job", type=str)
args = parser.parse_args()
job = json.loads(args.job)

search, brand, item, task, id_path, data_path, price_threshold, model_path, model_type, num_classes, population_metrics, value_dict = parse_job(job)
url = f'https://www.vinted.co.uk/catalog?search_text={search}&order=newest_first&page=1'

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    with BrowserSession() as SESSION:
        storer = HDF5Storer(data_path)
        logging.debug(f"app/scrape_runner.py: initialized storer {datetime.now()}")
        seen_ids = load_ids(id_path)
        logging.debug(f"app/scrape_runner.py: loaded IDs {datetime.now()}")
        while True:
            tries = 0
            while tries < MAX_RETRIES:
                logging.info("New scraping session")
                try:
                    listings, tries = scrape_listings([url], SESSION, tries)
                    break
                except Exception as e:
                    tries += 1
                    logging.warning(f"scraping failed, retrying {tries} / {MAX_RETRIES}: {e}")
                    sleep_time = min(300 * tries, 1800)
                    time.sleep(sleep_time)
                    if tries == PAGE_RESET_TRY:
                        SESSION.reset_page()
            else:
                logging.error("Max tries exceeded")
                raise FatalScraperError("Page scraping blocked")
            logging.debug(f"app/scrape_runner.py: scraped listings {datetime.now()}")
            try:
                listings_filtered = filter_listings(listings, seen_ids, brand)
            except Exception as e:
                logging.warning(f"scrape_runner.py: Filtering Listings Failed: {e}")
            logging.debug(f"app/scrape_runner.py: filtered listings {datetime.now()}")

            new_ids = get_ids_from_listings(listings_filtered)
            add_ids(id_path, new_ids)            # adds ids to the id file

            seen_ids.update(new_ids)            # adds them to the id list in mem
            if len(listings_filtered) > 0:
                try:
                    print(task)
                    if task == "alert":
                        try:
                            if model_type == "classification":
                                model = load_model(path=model_path, model_type='classification')
                                listings_evaluated = evaluate_class(listings=listings_filtered, model=model, value_dict=value_dict)
                            # elif model_type == "regression":
                            #     listings_evaluated = evaluate_price(listings=listings_filtered, model_path=model_path, population_metrics=population_metrics)
                        except Exception as e:
                            logging.error(f"Scrape_runner.py: Failed to evaluate batches: {e}")
                        print(price_threshold)
                        try:
                            alert(listings_evaluated, price_threshold)
                        except Exception as e:
                            logging.error(f"Scrape_runner.py: Failed to alert: {e}")
                    image_batch, metadata_batch = listings_to_batches(listings_filtered)
                    logging.info(f"Created batches")
                except Exception as e:
                    logging.error(f"scrape_runner.py: Failed to create batches: {e}")
                    continue
                try:
                    storer.append_batch(image_batch, metadata_batch)
                    logging.info(f"Saved batches, added {len(image_batch)}, currently holding {len(storer)} files")
                except Exception as e:
                    logging.error(f"Failed to store data: {e}")
                    continue
            else:
                logging.info(f"No new items found: {datetime.now()}")
            time.sleep(120)