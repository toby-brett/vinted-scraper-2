from typing import List, Tuple
import torch

from domain.models import *
from storage.listings import fetch_image_array
from vision.transforms import *
from vision.models import *

def evaluate_listing(listing, model_type, model_path, num_classes, population_metrics, value_dict):

    image = fetch_image_array(listing.image_url)
    tensor = preprocess(image, 256)

    if model_type == 'classification':
        model = CLASSIFY(num_classes)
        pred = torch.argmax(model(image)).item()
        value = value_dict[pred]

    elif model_type == 'regression':
        MU, STD = population_metrics
        model = REGRESSOR()
        pred = model.forward(tensor)
        value = (pred + MU) * STD

    return value

def evaluate(listings: List[Listing], model_type: str, model_path: str, population_metrics: Tuple[float, float], value_dict: dict) -> List[EvaluatedListing]:
    evaluated_listings = []
    for listing in listings:

        value = evaluate_listing(listing, model_type, model_path, population_metrics, value_dict)
        evaluated_at = datetime.now()

        evaluated_listing = EvaluatedListing(
            listing=listing,
            predicted_value=value,
            model_type=model_type,
            evaluated_at=evaluated_at
        )

        evaluated_listings.append(evaluated_listing)

    return evaluated_listings