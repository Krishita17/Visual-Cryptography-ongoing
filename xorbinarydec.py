import numpy as np
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio, structural_similarity, normalized_root_mse

def decrypt(shares):
    result = shares[:, :, 0].copy()
    for i in range(1, shares.shape[2]):
        result = np.bitwise_xor(result, shares[:, :, i])
    return Image.fromarray(result.astype(np.uint8)), result

def evaluate_metrics(original, output):
    psnr = peak_signal_noise_ratio(original, output)
    ssim = structural_similarity(original, output)
    ncorr = 1 - normalized_root_mse(original, output)
    return {'PSNR': psnr, 'SSIM': ssim, 'NCORR': ncorr}
