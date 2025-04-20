# MA.py

import numpy as np
import hashlib

def compute_hash(image_array):
    """Computes SHA-256 hash of a given image array."""
    return hashlib.sha256(image_array.astype(np.uint8).tobytes()).hexdigest()

def encrypt(input_image, share_size):
    """Encrypts an image using modular addition with random shares."""
    
    image = np.asarray(input_image)  # Convert image to a numpy array
    (row, column) = image.shape

    # Generate random shares and set the last one as the image
    shares = np.random.randint(0, 256, size=(row, column, share_size))
    shares[:, :, -1] = image.copy()

    # Modular addition to form encrypted share
    for i in range(share_size - 1):
        shares[:, :, -1] = (shares[:, :, -1] + shares[:, :, i]) % 256

    return shares, image
