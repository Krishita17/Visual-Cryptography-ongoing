import numpy as np
import hashlib

def compute_hash(image_array):
    """Computes SHA-256 hash of a given image array."""
    return hashlib.sha256(image_array.astype(np.uint8).tobytes()).hexdigest()

def encrypt(input_image, share_size, seed=42):
    """
    Encrypts an image by dividing it into multiple shares using XOR operation.
    Each share is randomly generated and the last share stores the original image data.

    Args:
    - input_image: The image to be encrypted.
    - share_size: The number of shares to generate.
    - seed: The random seed to ensure reproducibility. Default is 42 for debugging purposes.
    
    Returns:
    - shares: The list of shares.
    - image: The original image matrix.
    """
    np.random.seed(seed)  # Set a fixed seed for reproducibility
    image = np.asarray(input_image, dtype=np.uint8)  # Convert image to numpy array
    (row, column) = image.shape  # Get the shape (rows and columns) of the image
    shares = np.random.randint(0, 256, size=(row, column, share_size), dtype=np.uint8)  # Random shares
    shares[:, :, -1] = image.copy()  # The last share stores the original image
    
    # XOR the original image with other random shares
    for i in range(share_size - 1):
        shares[:, :, -1] ^= shares[:, :, i]  # XOR last share with others
    
    return shares, image