# encryption_cmyk.py
import numpy as np
from PIL import Image

def cmyk_encrypt(input_image):
    input_matrix = np.asarray(input_image.convert("RGB"))

    cmyk_image = input_image.convert("CMYK")

    # Decompose into two CMYK channels: Cyan and Magenta
    cyan_image = Image.new("CMYK", input_image.size)
    magenta_image = Image.new("CMYK", input_image.size)

    for x in range(input_image.width):
        for y in range(input_image.height):
            c, m, y_, k = cmyk_image.getpixel((x, y))
            cyan_image.putpixel((x, y), (c, 0, 0, 0))
            magenta_image.putpixel((x, y), (0, m, 0, 0))

    return cyan_image, magenta_image, input_matrix
