from typing import List, Tuple
import torch
import logging
import datetime

import config.settings as settings
import domain.models as models
import storage.storer as storer
import vision.models as ML_models
import vision.transforms as transforms

def evaluate_price(listings: List[models.Listing], model: torch.nn.Module, population_metrics: str, price_offset: float):

    mean, std = population_metrics.split(' ')
    mean = float(mean)
    std = float(std)

    evaluated_listings = []
    for listing in listings:
        try:
            image = storer.fetch_image_array(listing.image_url)
        except Exception as e:
            logging.exception(f"vision/evaluator.py: Failed to fetch image array: {e}")
            raise e

        try:
            tensor = transforms.preprocess(image)
        except Exception as e:
            logging.exception(f"vision/evaluator.py: Failed to preprocess image: {e}")
            raise e

        try:
            pred = model(tensor)
            pred = pred.squeeze(0)
        except Exception as e:
            logging.exception(f"vision/evaluator.py: Failed to preprocess image: {e}")
            raise e

        try:
            value = pred * std + mean
        except Exception as e:
            logging.exception(f"vision/evaluator.py: Failed to un-normalize prediction: {e}")
            raise e

        logging.info(f"Evaluated Listing: {listing.url}, Price: {listing.price}, Value: {value}, Value after offset: {value - price_offset}, (offset: {price_offset})")

        evaluated_listings.append(
            models.EvaluatedListing(
                listing=listing,
                predicted_value=float(value) - price_offset,
                model_type="regression",
                evaluated_at=datetime.datetime.now(),
                confidence=None
            )
        )

    return evaluated_listings

def evaluate_class(listings: List[models.Listing], model: torch.nn.Module, value_dict: dict):
    evaluated_listings = []
    for listing in listings:
        try:
            image = storer.fetch_image_array(listing.image_url)
        except Exception as e:
            logging.exception(f"vision/evaluator.py: Failed to fetch image array: {e}")
            raise e

        try:
            tensor = transforms.preprocess(image)
        except Exception as e:
            logging.exception(f"vision/evaluator.py: Failed to preprocess image: {e}")
            raise e

        try:
            pred = model(tensor)
            pred = pred.squeeze(0)
        except Exception as e:
            logging.exception(f"vision/evaluator.py: Failed to preprocess image: {e}")
            raise e

        try:
            index = torch.argmax(pred).item()
            value = value_dict[str(index)]
        except Exception as e:
            logging.exception(f"vision/evaluator.py: Failed to generate prediction: {e}")
            raise e

        logging.info(f"Evaluated Listing: {listing.url}, Price: {listing.price}, Value: {value}")

        evaluated_listings.append(
            models.EvaluatedListing(
                listing=listing,
                predicted_value=float(value),
                model_type="classification",
                evaluated_at=datetime.datetime.now(),
                confidence=pred[index].item()
            )
        )

    return evaluated_listings


def load_model(path, model_type, device="cpu"):
    """Loads a trained model for evaluation, handling DataParallel checkpoints."""

    # Initialize model
    if model_type == 'regression':
        model = ML_models.REGRESSOR()
    elif model_type == 'classification':
        model = ML_models.CLASSIFY()

    # Load checkpoint
    checkpoint = torch.load(path, map_location=device)

    # Fix 'module.' prefix if present
    from collections import OrderedDict
    new_state_dict = OrderedDict()
    for k, v in checkpoint.items():
        name = k.replace("module.", "")  # remove 'module.' if present
        new_state_dict[name] = v

    # Load state dict
    model.load_state_dict(new_state_dict)

    # Set model to eval mode and move to device
    model.to(device)
    model.eval()

    return model

