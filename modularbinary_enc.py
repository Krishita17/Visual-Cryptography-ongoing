import numpy as np
from PIL import Image

def encrypt(input_image, num_shares):
    image = np.array(input_image.convert("1"), dtype=np.uint8) // 255  # Binary (0/1)
    h, w = image.shape

    shares = np.random.randint(0, 2, size=(h, w, num_shares - 1), dtype=np.uint8)
    final_share = image.copy()

    for i in range(num_shares - 1):
        final_share = (final_share + shares[:, :, i]) % 2

    shares = np.concatenate((shares, final_share[:, :, None]), axis=2)
    return shares, image
