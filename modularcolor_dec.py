import numpy as np
from PIL import Image

def decrypt(shares):
    shares = shares.astype(np.uint16)
    final = shares[:, :, :, -1]
    for i in range(shares.shape[3] - 1):
        final = (final - shares[:, :, :, i] + 256) % 256
    final = final.astype(np.uint8)
    return Image.fromarray(final), final
