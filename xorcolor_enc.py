# xorcolor_enc.py
import numpy as np
from PIL import Image

def encrypt(input_image, share_size):
    image = np.asarray(input_image)
    row, col, depth = image.shape
    shares = np.random.randint(0, 256, size=(row, col, depth, share_size), dtype=np.uint8)
    shares[:, :, :, -1] = image.copy()
    
    for i in range(share_size - 1):
        shares[:, :, :, -1] ^= shares[:, :, :, i]
    
    return shares, image
