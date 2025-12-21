import pickle
import argparse
import json

from scraper.orchestrator import *
from storage.adapter import *
from storage.listings import *
from scraper.cleaner import *
from utils.utils import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--job", type=str)
args = parser.parse_args()
job = json.loads(args.job)

search, brand, item, task, model, model_type, id_path, data_path = parse_job(job)
url = f'https://www.vinted.co.uk/catalog?search_text={search}&order=newest_first&page=1'

if __name__ == "__main__":

    storer = HDF5Storer(data_path)
    logging.debug(f"app/scrape_runner.py: initialized storer {datetime.now()}")
    seen_ids = load_ids(id_path)
    logging.debug(f"app/scrape_runner.py: loaded IDs {datetime.now()}")

    while True:

        logging.info("New scraping session")
        listings = scrape_listings([url])
        logging.debug(f"app/scrape_runner.py: scraped listings {datetime.now()}")
        listings_filtered = filter_listings(listings, seen_ids, brand)
        logging.debug(f"app/scrape_runner.py: filtered listings {datetime.now()}")
        new_ids = get_ids_from_listings(listings_filtered)

        add_ids(id_path, new_ids)            # adds ids to the id file
        seen_ids.update(new_ids)            # adds them to the id list in mem

        if len(listings_filtered) > 0:
            try:
                image_batch, metadata_batch = listings_to_batches(listings_filtered)
                logging.info(f"Created batches")
            except Exception as e:
                logging.error(f"Failed to create batches: {e}")
                continue

            try:
                storer.append_batch(image_batch, metadata_batch)
                logging.info(f"Saved batches, added {len(image_batch)}, currently holding {len(storer)} files")
            except Exception as e:
                logging.error(f"Failed to store data: {e}")
                continue

        else:
            logging.info(f"No new items found: {datetime.now()}")

        time.sleep(5)
