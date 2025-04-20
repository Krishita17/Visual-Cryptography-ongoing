# madec.py

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from GrayscaleMetrics import psnr, normxcorr2D
from MA import encrypt, compute_hash
import os
import time

def decrypt(shares):
    """Decrypts an image from encrypted shares using modular subtraction."""
    import numpy as np
from PIL import Image

def decrypt(shares_image):
    shares_image = shares_image.astype(np.int16)  # Safe arithmetic

    for i in range(shares_image.shape[2] - 1):
        shares_image[:, :, -1] = (shares_image[:, :, -1] - shares_image[:, :, i] + 256) % 256

    final_image = shares_image[:, :, -1].astype(np.uint8)
    return Image.fromarray(final_image), final_image


def display_images(images, integrity_checks):
    """Displays the three reconstructed images in a single figure using Matplotlib."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    fig.suptitle("Reconstructed Images", fontsize=14, fontweight='bold')
    titles = ["Image 1", "Image 2", "Image 3"]

    for i, ax in enumerate(axes):
        ax.imshow(images[i], cmap='gray')
        ax.set_title(titles[i], fontsize=12)
        ax.set_xlabel(f"Hash Integrity: {'PASS' if integrity_checks[i] else 'FAIL'}", 
                      fontsize=10, color="green" if integrity_checks[i] else "red")
        ax.axis('off')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    print("Ensure images 'a.png', 'b.jpg', and 'c.png' are present in the same folder!")

    try:
        shares_input = input("Enter number of shares for all three images (e.g., '3 4 5'): ")
        shares_list = list(map(int, shares_input.split()))
        if len(shares_list) != 3 or any(s < 2 or s > 8 for s in shares_list):
            raise ValueError
    except ValueError:
        print("Invalid input! Enter three integers (2-8) separated by spaces.")
        exit(0)

    try:
        input_image1 = Image.open('a.png').convert('L')
        input_image2 = Image.open('b.jpg').convert('L')
        input_image3 = Image.open('c.png').convert('L')
    except FileNotFoundError:
        print("One or more input files not found!")
        exit(0)

    print("Images loaded successfully!")

    hash_original_1 = compute_hash(np.array(input_image1))
    hash_original_2 = compute_hash(np.array(input_image2))
    hash_original_3 = compute_hash(np.array(input_image3))

    start_time = time.time()

    shares1, input_matrix1 = encrypt(input_image1, shares_list[0])
    shares2, input_matrix2 = encrypt(input_image2, shares_list[1])
    shares3, input_matrix3 = encrypt(input_image3, shares_list[2])

    os.makedirs("outputs", exist_ok=True)

    for ind in range(shares_list[0]):
        Image.fromarray(shares1[:, :, ind].astype(np.uint8)).save(f"outputs/MA_Share1_{ind+1}.png")
    for ind in range(shares_list[1]):
        Image.fromarray(shares2[:, :, ind].astype(np.uint8)).save(f"outputs/MA_Share2_{ind+1}.png")
    for ind in range(shares_list[2]):
        Image.fromarray(shares3[:, :, ind].astype(np.uint8)).save(f"outputs/MA_Share3_{ind+1}.png")

    output_image1, output_matrix1 = decrypt(shares1)
    output_image2, output_matrix2 = decrypt(shares2)
    output_image3, output_matrix3 = decrypt(shares3)

    hash_reconstructed_1 = compute_hash(output_matrix1)
    hash_reconstructed_2 = compute_hash(output_matrix2)
    hash_reconstructed_3 = compute_hash(output_matrix3)

    integrity_1 = hash_original_1 == hash_reconstructed_1
    integrity_2 = hash_original_2 == hash_reconstructed_2
    integrity_3 = hash_original_3 == hash_reconstructed_3

    output_image1.save('outputs/Output_MA1.png')
    output_image2.save('outputs/Output_MA2.png')
    output_image3.save('outputs/Output_MA3.png')

    end_time = time.time()

    print("\n--- Evaluation Metrics ---")
    print(f"PSNR for Image 1: {psnr(input_matrix1, output_matrix1)} dB")
    print(f"NCORR for Image 1: {normxcorr2D(input_matrix1, output_matrix1)}")
    print(f"Integrity Check for Image 1: {'PASS' if integrity_1 else 'FAIL'}")

    print(f"PSNR for Image 2: {psnr(input_matrix2, output_matrix2)} dB")
    print(f"NCORR for Image 2: {normxcorr2D(input_matrix2, output_matrix2)}")
    print(f"Integrity Check for Image 2: {'PASS' if integrity_2 else 'FAIL'}")

    print(f"PSNR for Image 3: {psnr(input_matrix3, output_matrix3)} dB")
    print(f"NCORR for Image 3: {normxcorr2D(input_matrix3, output_matrix3)}")
    print(f"Integrity Check for Image 3: {'PASS' if integrity_3 else 'FAIL'}")

    print(f"Total Execution Time: {end_time - start_time:.4f} seconds")

    display_images([output_image1, output_image2, output_image3], [integrity_1, integrity_2, integrity_3])
