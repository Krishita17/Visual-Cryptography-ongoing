import numpy as np
from PIL import Image

def encrypt(input_image, share_size):
    image = np.asarray(input_image).astype(np.uint8)
    row, col, channels = image.shape
    shares = np.random.randint(0, 256, size=(row, col, channels, share_size - 1), dtype=np.uint8)
    
    final_share = image.copy()
    for i in range(share_size - 1):
        final_share = (final_share.astype(np.uint16) + shares[:, :, :, i].astype(np.uint16)) % 256
    final_share = final_share.astype(np.uint8)
    
    shares = np.concatenate((shares, final_share[:, :, :, np.newaxis]), axis=3)
    return shares, image
