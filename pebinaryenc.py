import numpy as np
from PIL import Image

def extract_colour():
    colour = [[0,0,1,1], [1,1,0,0], [1,0,0,1], [0,1,1,0], [1,0,1,0], [0,1,0,1]]
    return np.array(colour[np.random.randint(0, 6)])

def encrypt(input_image):
    input_matrix = np.asarray(input_image).astype(np.uint8)
    row, col = input_matrix.shape

    share1 = np.empty((2 * row, 2 * col), dtype=np.uint8)
    share2 = np.empty((2 * row, 2 * col), dtype=np.uint8)

    for i in range(row):
        for j in range(col):
            color = extract_colour()
            # Same pattern for both shares
            for dx in range(2):
                for dy in range(2):
                    share1[2*i+dx, 2*j+dy] = color[2*dx+dy]
                    share2[2*i+dx, 2*j+dy] = color[2*dx+dy]

            # Invert share2 if pixel is black
            if input_matrix[i, j] == 0:
                for dx in range(2):
                    for dy in range(2):
                        share2[2*i+dx, 2*j+dy] ^= 1

    return share1, share2
