import numpy as np
from PIL import Image

def decrypt(shares):
    shares = shares.astype(np.uint8)
    recon = shares[:, :, -1].copy()
    for i in range(shares.shape[2] - 1):
        recon = (recon - shares[:, :, i] + 2) % 2

    recon_img = Image.fromarray((recon * 255).astype(np.uint8))
    return recon_img, recon
