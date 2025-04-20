import numpy as np
from skimage.metrics import peak_signal_noise_ratio

def psnr(original, output):
    return peak_signal_noise_ratio(original, output, data_range=255)

def normxcorr2D(image1, image2):
    image1 = image1.astype(np.float64)
    image2 = image2.astype(np.float64)
    
    image1_mean = np.mean(image1)
    image2_mean = np.mean(image2)
    
    image1_std = np.std(image1)
    image2_std = np.std(image2)
    
    if image1_std == 0 or image2_std == 0:
        return float('nan')
    
    numerator = np.mean((image1 - image1_mean) * (image2 - image2_mean))
    denominator = image1_std * image2_std
    
    return numerator / denominator
