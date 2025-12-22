import os

import random
import pickle
from pathlib import Path
import logging

from config.settings import *

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
        logging.error("Failed to load ID file: %s", path, exc_info=e)
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
        logging.error("Failed to load ID file: %s", path, exc_info=e)
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

    data_path = ROOT_DATA + get_file_starter(brand, item) + '.h5'
    id_path = ROOT_ID + get_file_starter(brand, item) + '.pkl'

    search = brand + '%20' + item

    if task == "silent":
        return search, brand, item, task, None, None, id_path, data_path