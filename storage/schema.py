import numpy as np

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