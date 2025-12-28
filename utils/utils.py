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
    pages = job["pages"]
    task = job["task"]
    model_type = job["model_type"]
    model_path = job["model_path"]
    price_threshold = job["price_threshold"]
    num_classes = job["num_classes"]
    population_metrics = job["population_metrics"]
    value_dict = job["value_dict"]

    data_path = settings.ROOT_DATA / f"{get_file_starter(brand, item)}.h5"
    id_path = settings.ROOT_ID / f"{get_file_starter(brand, item)}.pkl"
    model_path = settings.ROOT_MODELS / model_path

    search = brand + '%20' + item

    if task == "silent":
        return search, brand, item, task, id_path, data_path, None, None, None, None, None, None

    elif task == "alert":
        return search, brand, item, task, id_path, data_path, price_threshold, model_path, model_type, num_classes, population_metrics, value_dict

class FatalScraperError(RuntimeError):
    """Unrecoverable error – scraper must stop."""
    pass

def load_job(job_file) -> JobObject:

    with open(job_file, "r") as f:
        job = json.load(f)

    search, brand, item, task, id_path, data_path, price_threshold, model_path, model_type, num_classes, population_metrics, value_dict = parse_job(job)

    if task == "alert":
        job_obj = JobObject(
            search=search,
            brand=brand,
            task=task,
            model_type=model_type,
            id_path=id_path,
            price_threshold=price_threshold,
            model=load_model(model_path, model_type=model_type),
            population_metrics=population_metrics,
            value_dict=value_dict,
            data_storer=HDF5Storer(data_path)
        )
    elif task == "silent":
        job_obj = JobObject(
            search=search,
            brand=brand,
            task=task,
            model_type=None,
            id_path=id_path,
            price_threshold=None,
            model=None,
            population_metrics=None,
            value_dict=None,
            data_storer=HDF5Storer(data_path)
        )

    return job_obj

def load_jobs(job_folder) -> List[JobObject]:

    jobs: List[JobObject] = []

    for filename in sorted(os.listdir(job_folder)):
        path = os.path.join(job_folder, filename)

        if filename.lower().endswith(".json"):
            job = load_job(path)
            jobs.append(job)

    return jobs