import h5py
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import logging

metadata_dtype = np.dtype([
    ('item_id', 'S20'),
    ('title', 'S100'),
    ('price', 'f4'),
    ('brand', 'S50'),
    ('condition', 'S20'),
    ('size', 'S10'),
    ('url', 'S200'),
    ('timestamp', 'S30')
])

class HDF5Storer:
    def __init__(self, filepath):
        self.filepath = filepath

    def _ensure_datasets(self, h5file, images_shape, metadata_dtype):
        """
        Create datasets if they don't exist, or fetches existing ones
        """
        if 'images' not in h5file:
            # create resizable dataset for images
            h5file.create_dataset(
                'images',
                shape=(0, *images_shape),
                maxshape=(None, *images_shape),
                chunks=(1, *images_shape),
                dtype='uint8',
                compression='gzip'
            )
        if 'metadata' not in h5file:
            h5file.create_dataset(
                'metadata',
                shape=(0,),
                maxshape=(None,),
                dtype=metadata_dtype,
                chunks=True,
                compression="gzip"
            )

    def __len__(self):
        with h5py.File(self.filepath, 'r') as f:
            img_ds = f['images']
            return img_ds.shape[0]


    def len_images(self):
        with h5py.File(self.filepath, 'r') as f:
            img_ds = f['images']
            return img_ds.shape[0]

    def len_meta(self):
        with h5py.File(self.filepath, 'r') as f:
            img_ds = f['metadata']
            return img_ds.shape[0]
    def append_batch(self, image_batch, metadata_batch):
        """
        Append a batch of images and corresponding metadata
        """
        with h5py.File(self.filepath, 'a') as f:

            self._ensure_datasets(f, images_shape=image_batch.shape[1:], metadata_dtype=metadata_batch.dtype)

            try:
                img_ds = f['images']
                old_size = img_ds.shape[0]
                new_size = old_size + image_batch.shape[0]

                meta_ds = f['metadata']
                old_size_meta = meta_ds.shape[0]
                new_size_meta = old_size_meta + metadata_batch.shape[0]

                if new_size == new_size_meta:
                    img_ds.resize(new_size, axis=0)
                    img_ds[old_size:new_size] = image_batch
                    meta_ds.resize(new_size_meta, axis=0)
                    meta_ds[old_size_meta:new_size_meta] = metadata_batch
                else:
                    logging.exception(f"Metadata and image sizes DO NOT MATCH, threw batch")

            except Exception as e:
                logging.exception(f"Cannot merge data: {e}")

            for meta in metadata_batch:
                logging.info(f"New item found: {meta[6]}")

            f.flush()




def fetch_image_array(url: str, size=(500, 500)) -> np.ndarray:
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    img = Image.open(BytesIO(response.content)).convert('RGB')
    img = img.resize(size)

    array = np.asarray(img, dtype=np.uint8)

    if array.shape != (size[0], size[1], 3):
        raise ValueError(f"Image from {url} has wrong shape {array.shape}")

    return array

