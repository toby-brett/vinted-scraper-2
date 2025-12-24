from typing import List
import torch
import logging

from config.settings import ROOT_MODELS
from domain.models import *
from storage.listings import fetch_image_array
from vision.models import CLASSIFY, REGRESSOR
from vision.transforms import preprocess


def evaluate_class(listings: List[Listing], model: torch.nn.Module, value_dict: dict):
    evaluated_listings = []
    for listing in listings:
        try:
            image = fetch_image_array(listing.image_url)
        except Exception as e:
            logging.error(f"vision/evaluator.py: Failed to fetch image array: {e}")
            raise e

        try:
            tensor = preprocess(image)
        except Exception as e:
            logging.error(f"vision/evaluator.py: Failed to preprocess image: {e}")
            raise e

        try:
            pred = model(tensor)
            pred = pred.squeeze(0)
        except Exception as e:
            logging.error(f"vision/evaluator.py: Failed to preprocess image: {e}")
            raise e

        try:
            index = torch.argmax(pred).item()
            value = value_dict[str(index)]
        except Exception as e:
            logging.error(f"vision/evaluator.py: Failed to generate prediction: {e}")
            raise e

        logging.info(f"Evaluated Listing: {listing.url}, Price: {listing.price}, Value: {value}")

        evaluated_listings.append(
            EvaluatedListing(
                listing=listing,
                predicted_value=float(value),
                model_type="classification",
                evaluated_at=datetime.now(),
                confidence=pred[index].item()
            )
        )

    return evaluated_listings


def load_model(path, model_type, device="cpu"):
    """Loads a trained model for evaluation, handling DataParallel checkpoints."""
    path = ROOT_MODELS + path
    # Initialize model
    if model_type == 'regression':
        model = REGRESSOR()
    elif model_type == 'classification':
        model = CLASSIFY()

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

# def load_class_model(model_path: str, num_classes: int):
#
#     if num_classes is None:
#         raise ValueError("num_classes must be an integer, got None")
#
#     device = torch.device('cpu')
#
#     try:
#         model = CLASSIFY(num_classes)
#     except Exception as e:
#         logging.error(f"vision/evaluator.py: Failed to load empty model and move it to cpu: {e}")
#         raise e
#
#     try:
#         model_state_dict_path = ROOT_MODELS + model_path    # creates base path to model
#         model_state_dict = torch.load(model_state_dict_path, map_location=device)
#     except Exception as e:
#         logging.error(f"vision/evaluator.py: Failed to load models state dict: {e}")
#         raise e
#
#     try:
#         from collections import OrderedDict
#         new_state_dict = OrderedDict()
#         for k, v in model_state_dict.items():
#             name = k.replace("module.", "")
#             new_state_dict[name] = v
#     except Exception as e:
#         logging.error(f"vision/evaluator.py: Failed to created new dict: {e}")
#         raise e
#
#     try:
#         model.load_state_dict(new_state_dict)
#         model.to(device)
#         model.eval()
#     except Exception as e:
#         logging.error(f"vision/evaluator.py: Failed to load models state dict into model: {e}")
#
#     return model
