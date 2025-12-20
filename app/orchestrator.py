from scraper.orchestrator import *
from storage.adapter import listings_to_batches
from storage.listings import *

def collect_listings(urls: List[str], data_path: str):

    listings = scrape_listings(urls)        # a list of Listing objects
    images, metadata = listings_to_batches(listings)
    storer = HDF5Storer(data_path)
    storer.append_batch(images, metadata)

    return listings

# def evaluate_listings(listings):
#     for listing in listings:
#         try:
#             evaluation = evaluate_listing(listing) # EvaluatedListing data structure
#             decision = decide_listing(evaluation) # Descicion data structure
#             if decision.action == 'ALERT':
#                 alert(listing, evaluation, decision)
#         except Exception as e:
#             logging.warning(f"Failed to evaluate listing {listing.item_id}: {e}")