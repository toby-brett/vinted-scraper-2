import time

import torch.nn
import logging
import signal
import threading

import scraper.orchestrator as orchestrator
import storage.adapter as adapter
import scraper.cleaner as cleaner
import utils.utils as utils
import vision.evaluator as evaluator
import alerts.alert as alert
from domain.models import TickResult, JobObject, JobRuntime
from scraper.browser import BlockedError
import config.settings as settings

shutdown_event = threading.Event()

def _handle_shutdown(signum, frame):
    logging.info(f"Received signal {signum}. Initiating shutdown.")
    shutdown_event.set()

signal.signal(signal.SIGTERM, _handle_shutdown)
signal.signal(signal.SIGINT, _handle_shutdown)

def tick(runtime: JobRuntime) -> TickResult:
    """
    Performs one tick of run process, covering every step
    :job: job containing all the info needed
    :return: TickResult
    """

    warnings = []
    job = runtime.job

    url = f'https://www.vinted.co.uk/catalog?search_text={job.search}&order=newest_first&page=1'
    logging.info("New scraping session initialized.")

    try:
        listings, tries = orchestrator.scrape_listings([url], runtime.session, 0)
        logging.info(f"Scraped listings")
    except TimeoutError as e:
        logging.exception(f"Timeout: {e}")
        raise SystemExit(settings.TIMEOUT_EXIT_CODE)
    except BlockedError as e:
        logging.exception(f"Blocked: {e}")
        logging.info("Waiting an hour and a half, and then retrying")
        wait_seconds = int(60 * 60 * 1.5)
        for _ in range(wait_seconds):
            if shutdown_event.is_set():
                logging.info("Shutdown requested during backoff sleep.")
                raise SystemExit(settings.BLOCKED_EXIT_CODE)
            time.sleep(1)
        logging.info("wait over")
        raise SystemExit(settings.BLOCKED_EXIT_CODE)

    try:
        listings_filtered = cleaner.filter_listings(listings, runtime.seen_ids, job.brand)
        logging.info(f"filtered listings")
    except Exception as e:
        logging.exception(f"Filtering Listings Failed: {e}")
        return TickResult(new=0, stored=0, return_status="error", error=str(e), warnings=warnings)

    try:
        new_ids = cleaner.get_ids_from_listings(listings_filtered)
        logging.info("ID's found")
    except Exception as e:
        return TickResult(new=len(listings_filtered), stored=0, return_status="error", error=f"Failed to get ids: {e}", warnings=warnings)

    if len(listings_filtered) > 0:
        if job.task == "alert":
            try:
                listings_evaluated = evaluator.evaluate_price(listings=listings_filtered, model=job.model, population_metrics=job.population_metrics, price_offset=job.price_offset)
                logging.info(f"Evaluated listings")
            except Exception as e:
                logging.exception(f"Failed to evaluate batches: {e}")
                return TickResult(new=len(listings_filtered), stored=0, return_status="error", error=str(e), warnings=warnings)

            try:
                alert.alert(listings_evaluated, job.price_threshold, job.max_price, job.min_condition)
                logging.info(f"Sent alert")
            except Exception as e:
                logging.exception(f"Failed to send alert: {e}")
                warnings.append(f"sending alert failed:{type(e).__name__}:{e}")

        try:
            image_batch, metadata_batch = adapter.listings_to_batches(listings_filtered)
            logging.info(f"Created batches")
        except Exception as e:
            logging.exception(f"Failed to create batches: {e}")
            return TickResult(new=len(listings_filtered), stored=0, return_status="error", error=str(e), warnings=warnings)

        try:
            runtime.data_storer.append_batch(image_batch, metadata_batch)
            logging.info(f"Saved batches, added {len(image_batch)}, currently holding {runtime.data_storer.len_images()} images, {runtime.data_storer.len_meta()} labels")
        except Exception as e:
            logging.exception(f"Failed to save batched: {e}")
            return TickResult(new=len(listings_filtered), stored=0, return_status="error", error=str(e), warnings=warnings)

        try:
            utils.add_ids(job.id_path, new_ids)
            runtime.seen_ids.update(new_ids)
        except Exception as e:
            logging.exception(f"Failed to load seen IDs from disk: {e}")
            return TickResult(new=len(listings_filtered), stored=0, return_status="error", error="Failed to get ids", warnings=warnings)

    else:
        image_batch = [] # so len = 0
        logging.info(f"No new items found")

    return TickResult(new=len(listings_filtered), stored=len(image_batch), return_status="ok", error=None, warnings=warnings)