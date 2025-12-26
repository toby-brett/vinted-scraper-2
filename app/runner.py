import time

import torch.nn
import logging

import scraper.orchestrator as orchestrator
import storage.adapter as adapter
import scraper.cleaner as cleaner
import utils.utils as utils
import vision.evaluator as evaluator
import alerts.alert as alert
from domain.models import TickResult, JobObject, JobRuntime
from scraper.browser import BlockedError


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
    except BlockedError as e:
        logging.exception(f"Cloudflare blocked: {e}")
        return TickResult(new=0, stored=0, return_status="blocked", error=str(e), warnings=warnings)
    except Exception as e:
        logging.exception(f"Error when scraping listings: {e}")
        return TickResult(new=0, stored=0, return_status="error", error=str(e), warnings=warnings)

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
        logging.exception(f"Failed to load IDs from new listings: {e}")
        return TickResult(new=len(listings_filtered), stored=0, return_status="error", error="Failed to get ids", warnings=warnings)

    if len(listings_filtered) > 0:
        if job.task == "alert":
            try:
                if job.model_type == "classification":
                    listings_evaluated = evaluator.evaluate_class(listings=listings_filtered, model=job.model, value_dict=job.value_dict)
                    logging.info(f"Evaluated listings")
                elif job.model_type == "regression":
                    listings_evaluated = evaluator.evaluate_price(listings=listings_filtered, model=job.model, population_metrics=job.population_metrics)
                    logging.info(f"Evaluated listings")
                else:
                    logging.exception("Model_type was neither classification or regression")
                    return TickResult(new=len(listings_filtered), stored=0, return_status="error", error="Model_type was neither classification or regression", warnings=warnings)

            except Exception as e:
                logging.exception(f"Failed to evaluate batches: {e}")
                return TickResult(new=len(listings_filtered), stored=0, return_status="error", error=str(e), warnings=warnings)

            try:
                alert.alert(listings_evaluated, job.price_threshold)
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
            logging.info(f"Saved batches, added {len(image_batch)}, currently holding {len(runtime.data_storer)} files")
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