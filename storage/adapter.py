import numpy as np
from datetime import datetime

from domain.models import Listing
from storage.listings import fetch_image_array
from storage.schema import metadata_dtype

def listing_to_record(listing: Listing):
    """
    Converts a listing into (image_array, metadata_record)
    """
    image = fetch_image_array(listing.image_url)

    metadata = np.array(
        (
            listing.listing_id.encode(),
            listing.title.encode(),
            listing.price,
            (listing.brand or "").encode(),
            (listing.condition or "").encode(),
            (listing.size or "").encode(),
            listing.url.encode(),
            listing.discovered_at.isoformat().encode()
        ),
        dtype=metadata_dtype
    )

    return image, metadata

def listings_to_batches(listings):
    images = []
    metadata = []

    for listing in listings:
        try:
            img, meta = listing_to_record(listing)
            images.append(img)
            metadata.append(meta)
        except Exception:
            # drop bad records do not poison batch
            continue


    return (
        np.stack(images, axis=0),
        np.array(metadata, dtype=metadata_dtype)
    )