import numpy as np

def decrypt(share1, share2):
    overlap = share1 & share2
    row, col = share1.shape
    row //= 2
    col //= 2
    output = np.ones((row, col), dtype=np.uint8)

    for i in range(row):
        for j in range(col):
            block = overlap[2*i:2*i+2, 2*j:2*j+2]
            if np.sum(block) == 0:
                output[i, j] = 0
    return overlap, output
