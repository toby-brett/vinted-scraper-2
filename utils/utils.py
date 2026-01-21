import json
import os

import random
import pickle
from pathlib import Path
import logging
from typing import List

import config.settings as settings
from domain.models import JobObject
from storage.storer import HDF5Storer
from vision.evaluator import load_model


def load_ids(url):
    """
    Loads the list of ids from a given url, and creates the file if it does not exist
    """
    path = Path(url)

    if not path.exists():
        logging.warning("ID file does not exist, creating new one: %s", path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pickle.dumps([]))
        return set()

    try:
        with path.open('rb') as f:
            return set(pickle.load(f))
    except (pickle.UnpicklingError, EOFError) as e:
        logging.exception("Failed to load ID file: %s", path, exc_info=e)
        return set()


def add_ids(url, new_ids):
    """
    Opens and adds to list of existing IDs
    :param url: location of ids
    :param new_ids: list of ids to add
    :return: None
    """

    path = Path(url)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if path.exists():
            with path.open('rb') as f:
                ids = set(pickle.load(f))
        else:
            ids = set()
    except pickle.UnpicklingError as e:
        logging.exception("Failed to load ID file: %s", path, exc_info=e)
        ids = set()

    ids.update(new_ids)

    with path.open("wb") as f:
        pickle.dump(list(ids), f)


def get_file_starter(brand, item):
    return brand[0:2] + '_' + item[0:2]

def parse_job(job):

    brand = job["brand"]
    item = job["item"]
    task = job["task"]
    model_path = job["current_model_path"]
    price_threshold = job["price_threshold"]
    population_metrics = job["population_metrics"]
    criteria = job["criteria"]
    threshold = job["threshold"]
    max_price = job["max_price"]
    min_condition = job["min_condition"]
    price_offset = job['price_offset']

    data_path = settings.ROOT_DATA / f"{get_file_starter(brand, item)}.h5"
    id_path = settings.ROOT_ID / f"{(brand, item)}.pkl"
    model_path = settings.ROOT_MODELS / model_path

    search = brand + '%20' + item

    if task == "silent":
        return search, brand, item, task, None, None, id_path, data_path, None, None, None, None, None, None

    elif task == "alert":
        return (search,
                brand,
                item,
                task,
                criteria,
                threshold,
                id_path,
                data_path,
                price_threshold,
                model_path,
                population_metrics,
                max_price,
                min_condition,
                price_offset)

class FatalScraperError(RuntimeError):
    """Unrecoverable error – scraper must stop."""
    pass

def load_job(job_file) -> JobObject:

    with open(job_file, "r") as f:
        job = json.load(f)

    (search,
     brand,
     item,
     task,
     criteria,
     threshold,
     id_path,
     data_path,
     price_threshold,
     model_path,
     population_metrics,
     max_price,
     min_condition,
     price_offset) = parse_job(job)

    if task == "alert" and criteria == "model":
        job_obj = JobObject(
            search=search,
            brand=brand,
            task=task,
            criteria=criteria,
            threshold=threshold,
            id_path=id_path,
            price_threshold=price_threshold,
            model=load_model(model_path, model_type="regression"),
            population_metrics=population_metrics,
            data_storer=HDF5Storer(data_path),
            max_price=max_price,
            min_condition=min_condition,
            price_offset=price_offset
        )

    elif task == "alert" and criteria == "price":
        job_obj = JobObject(
            search=search,
            brand=brand,
            task=task,
            criteria=criteria,
            threshold=threshold,
            id_path=id_path,
            price_threshold=price_threshold,
            model=None,
            population_metrics=None,
            data_storer=HDF5Storer(data_path),
            max_price=max_price,
            min_condition=min_condition,
            price_offset=price_offset
        )

    elif task == "silent":
        job_obj = JobObject(
            search=search,
            brand=brand,
            task=task,
            criteria=criteria,
            threshold=threshold,
            id_path=id_path,
            price_threshold=None,
            model=None,
            population_metrics=None,
            data_storer=HDF5Storer(data_path),
            max_price=None,
            min_condition = None,
            price_offset=None
        )

    return job_obj

def load_jobs(job_folder) -> List[JobObject]:

    jobs: List[JobObject] = []

    for filename in sorted(os.listdir(job_folder)):
        if filename[0] != "&":
            path = os.path.join(job_folder, filename)

            if filename.lower().endswith(".json"):
                job = load_job(path)
                jobs.append(job)

    if len(jobs) == 0:
        return

    return jobs