import time

import torch.nn
import logging

import scraper.browser as browser
import scraper.orchestrator as orchestrator
import storage.adapter as adapter
import storage.storer as storer
import scraper.cleaner as cleaner
import utils.utils as utils
import vision.evaluator as evaluator
import alerts.alert as alert
import config.settings as settings

def tick(search: str, brand: str, item: str, task: str, id_path: str, data_path: str, price_threshold: float, model: torch.nn.Module, num_classes: float, population_metrics: str, value_dict: dict, storer: h5Storer.HDF5Storer, seen_ids: set):
    """
    Performs one tick of run process, covering every step
    :param seen_ids:
    :param storer:
    :param model:
    :param search:
    :param brand:
    :param item:
    :param task:
    :param id_path:
    :param data_path:
    :param price_threshold:
    :param num_classes:
    :param population_metrics:
    :param value_dict:
    :return:
    """
    with browser.BrowserSession() as SESSION:
        logging.info("New scraping session initialized.")
        try:
            listings, tries = orchestrator.scrape_listings([url], SESSION, tries)
            logging.info(f"Scraped listings")

        except Exception as e:
            logging.exception("Cloudflare detected: pausing for one hour")
            time.sleep(60 * 60)
