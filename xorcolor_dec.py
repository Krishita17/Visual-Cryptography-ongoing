# xorcolor_dec.py
import numpy as np
from PIL import Image

def decrypt(shares):
    shares_image = shares.copy()
    share_size = shares.shape[-1]

    for i in range(share_size - 1):
        shares_image[:, :, :, -1] ^= shares_image[:, :, :, i]
    
    final = shares_image[:, :, :, -1]
    return Image.fromarray(final.astype(np.uint8)), final
