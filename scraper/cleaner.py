import unicodedata

from typing import List
from domain.models import *

def check_id(id: str, ids):
    """
    Checks if id is in a list of ids
    :param id: the one to check
    :param ids: the list of all
    :return: Bool, False means didn't pass the check, i.e it is in the list of seen IDs
    """
    if id in ids:
        return False
    return True

def check_brand(brand_check: str, brand_target: str):
    """
    Checks if two brands are equal
    :param brand_check:
    :param brand_target:
    :return:
    """

    brand_check = brand_check.lower()
    brand_target = brand_target.lower()

    brand_check = unicodedata.normalize('NFKD', brand_check).encode('ascii', 'ignore').decode('utf-8')
    brand_target = unicodedata.normalize('NFKD', brand_target).encode('ascii', 'ignore').decode('utf-8')

    if brand_target in brand_check:
        return True
    return False



def filter_listings(listings: List[Listing], ids, brand):
    """
    Filters Listings to ensure they are the right brand, and have not been seen before
    :param listings: listing to check
    :param ids: list of seen ids
    :param brand: brand to check
    :return:
    """
    cleaned_listings = []
    for listing in listings:
        if listing.brand:           # checks brand field is filled
            if check_id(listing.listing_id, ids) and check_brand(listing.brand, brand):
                cleaned_listings.append(listing)
    return cleaned_listings

def get_ids_from_listings(listings):
    """
    Extracts the IDs from a group of listings
    :param listings:
    :return:
    """
    ids = []
    for listing in listings:
        ids.append(listing.listing_id)
    return ids