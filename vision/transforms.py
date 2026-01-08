import numpy as np
import torch
from torchvision import transforms
from PIL import Image
import logging

def preprocess(numpy_array: np.ndarray, size=256) -> torch.Tensor:
    """
    Takes an image and converts it to an ML ready tensor for eval
    """
    try:
        resnet_transform = transforms.Compose([
            transforms.ToPILImage(),  # Robust check to ensure it's PIL
            transforms.Resize((size, size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

        tensor = resnet_transform(numpy_array)

    except Exception as e:
        logging.exception(f"Failed to convert numpy array to tensor: {e}")
        raise e

    return tensor.unsqueeze(0)