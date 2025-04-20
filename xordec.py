import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from GrayscaleMetrics import psnr, normxcorr2D
from XOR import encrypt, compute_hash
import os
import time


def decrypt(shares):
    """
    Decrypts an image by XOR-ing the shares together to recover the original image.

    Args:
    - shares: The encrypted shares to be decrypted.

    Returns:
    - decrypted_image: The decrypted image.
    - decrypted_image_matrix: The matrix representation of the decrypted image.
    """
    (row, column, share_size) = shares.shape  # Get the dimensions of the shares
    decrypted_image = shares[:, :, -1].copy()  # Start with the last share, which contains the original data
    
    # XOR the shares together to recover the original image
    for i in range(share_size - 1):
        decrypted_image ^= shares[:, :, i]  # XOR in reverse order to decrypt
    
    return Image.fromarray(decrypted_image.astype(np.uint8)), decrypted_image  # Return as an Image and matrix

if __name__ == "__main__":
    print("Ensure images 'a.png', 'b.jpg', and 'c.png' are present!")

    try:
        share_size = int(input("Enter the number of shares (2-8): "))
        if not (2 <= share_size <= 8):
            raise ValueError  # Ensure share size is between 2 and 8
    except ValueError:
        print("Invalid input! Enter an integer between 2 and 8.")
        exit(0)

    try:
        # Open and convert the images to grayscale
        input_image1 = Image.open('a.png').convert('L')
        input_image2 = Image.open('b.jpg').convert('L')
        input_image3 = Image.open('c.png').convert('L')
    except FileNotFoundError:
        print("One or more input files not found!")
        exit(0)

    print("Images loaded successfully!")
    start_time = time.time()

    # Compute original hashes before encryption for integrity check
    hash_original_1 = compute_hash(np.array(input_image1))
    hash_original_2 = compute_hash(np.array(input_image2))
    hash_original_3 = compute_hash(np.array(input_image3))
    
    print(f"Original Hash of Image 1: {hash_original_1}")
    print(f"Original Hash of Image 2: {hash_original_2}")
    print(f"Original Hash of Image 3: {hash_original_3}")

    # Encrypt images to generate shares
    shares1, input_matrix1 = encrypt(input_image1, share_size)
    shares2, input_matrix2 = encrypt(input_image2, share_size)
    shares3, input_matrix3 = encrypt(input_image3, share_size)
    
    # Compute hashes of the encrypted shares (last share)
    hash_encrypted_1 = compute_hash(shares1[:, :, -1])
    hash_encrypted_2 = compute_hash(shares2[:, :, -1])
    hash_encrypted_3 = compute_hash(shares3[:, :, -1])
    
    print(f"Encrypted Hash of Image 1: {hash_encrypted_1}")
    print(f"Encrypted Hash of Image 2: {hash_encrypted_2}")
    print(f"Encrypted Hash of Image 3: {hash_encrypted_3}")
    
    # Save the shares as images
    for i in range(share_size):
        Image.fromarray(shares1[:, :, i]).save(f"outputs/XOR_Share1_{i+1}.png")
        Image.fromarray(shares2[:, :, i]).save(f"outputs/XOR_Share2_{i+1}.png")
        Image.fromarray(shares3[:, :, i]).save(f"outputs/XOR_Share3_{i+1}.png")

    # Decrypt images to recover original images from shares
    output_image1, output_matrix1 = decrypt(shares1)
    output_image2, output_matrix2 = decrypt(shares2)
    output_image3, output_matrix3 = decrypt(shares3)

    # Compute hashes after decryption to check if they match the original ones
    hash_decrypted_1 = compute_hash(output_matrix1)
    hash_decrypted_2 = compute_hash(output_matrix2)
    hash_decrypted_3 = compute_hash(output_matrix3)
    
    print(f"Decrypted Hash of Image 1: {hash_decrypted_1}")
    print(f"Decrypted Hash of Image 2: {hash_decrypted_2}")
    print(f"Decrypted Hash of Image 3: {hash_decrypted_3}")
    
    # Save the decrypted images
    output_image1.save('outputs/Output_XOR1.png')
    output_image2.save('outputs/Output_XOR2.jpg')
    output_image3.save('outputs/Output_XOR3.png')

    end_time = time.time()
    print("Decryption completed!")

    # Check integrity by comparing the original and decrypted hashes
    integrity_1 = "PASS" if hash_original_1 == hash_decrypted_1 else "FAIL"
    integrity_2 = "PASS" if hash_original_2 == hash_decrypted_2 else "FAIL"
    integrity_3 = "PASS" if hash_original_3 == hash_decrypted_3 else "FAIL"

    # Display evaluation metrics
    print("\n--- Evaluation Metrics ---")
    print(f"PSNR for Image 1: {psnr(input_matrix1, output_matrix1)} dB")
    print(f"NCORR for Image 1: {normxcorr2D(input_matrix1, output_matrix1)}")
    print(f"Integrity Check for Image 1: {integrity_1}")

    print(f"PSNR for Image 2: {psnr(input_matrix2, output_matrix2)} dB")
    print(f"NCORR for Image 2: {normxcorr2D(input_matrix2, output_matrix2)}")
    print(f"Integrity Check for Image 2: {integrity_2}")

    print(f"PSNR for Image 3: {psnr(input_matrix3, output_matrix3)} dB")
    print(f"NCORR for Image 3: {normxcorr2D(input_matrix3, output_matrix3)}")
    print(f"Integrity Check for Image 3: {integrity_3}")

    print(f"Total Execution Time: {end_time - start_time:.4f} seconds")

    # Show decrypted images with integrity checks
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(output_image1, cmap='gray')
    axes[0].set_title(f"Decrypted Image 1\nIntegrity: {integrity_1}")
    axes[0].axis('off')

    axes[1].imshow(output_image2, cmap='gray')
    axes[1].set_title(f"Decrypted Image 2\nIntegrity: {integrity_2}")
    axes[1].axis('off')

    axes[2].imshow(output_image3, cmap='gray')
    axes[2].set_title(f"Decrypted Image 3\nIntegrity: {integrity_3}")
    axes[2].axis('off')

    plt.show()
