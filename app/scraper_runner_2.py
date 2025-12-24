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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--job", type=str)
args = parser.parse_args()
job = json.loads(args.job)

search, brand, item, task, id_path, data_path, price_threshold, model_path, model_type, num_classes, population_metrics, value_dict = parse_job(job)
url = [f'https://www.vinted.co.uk/catalog?search_text={search}&order=newest_first&page=1'

storer = HDF5Storer(data_path)
logging.debug(f"app/scrape_runner.py: initialized storer {datetime.now()}")
seen_ids = load_ids(id_path)
logging.debug(f"app/scrape_runner.py: loaded IDs {datetime.now()}")

with BrowserSession() as session:
    while True:
        listings = scrape_listings_session(url, session)