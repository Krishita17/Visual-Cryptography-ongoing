import numpy as np
import hashlib
from PIL import Image

def compute_hash(image):
    return hashlib.sha256(image.tobytes()).hexdigest()

def encrypt(input_image, share_size):
    image = np.asarray(input_image.convert("L"))  # Grayscale
    (row, col) = image.shape
    shares = np.random.randint(0, 256, size=(row, col, share_size - 1), dtype=np.uint8)
    
    last_share = image.copy()
    for i in range(share_size - 1):
        last_share = np.bitwise_xor(last_share, shares[:, :, i])
    
    shares = np.concatenate((shares, last_share[..., np.newaxis]), axis=2)
    return shares, image
