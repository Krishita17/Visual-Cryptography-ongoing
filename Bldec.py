import numpy as np
from PIL import Image
import time
from skimage.metrics import structural_similarity as ssim
from GrayscaleMetrics import psnr, normxcorr2D
from BLDen import BLD_encrypt, compute_hash, convertGrayToBinary, convertBinaryToGray

# Partial Extraction - Decrypt by overlapping and extracting
def PE_decrypt(secret_shares):
    num_shares = len(secret_shares)
    overlap_matrix = secret_shares[0]
    for i in range(1, num_shares):
        overlap_matrix &= secret_shares[i]
    
    (row, column) = overlap_matrix.shape
    row, column = row // 2, column // 2
    extraction_matrix = np.ones((row, column))
    
    for i in range(row):
        for j in range(column):
            cnt = (overlap_matrix[2*i][2*j] +
                   overlap_matrix[2*i + 1][2*j] +
                   overlap_matrix[2*i][2*j + 1] +
                   overlap_matrix[2*i + 1][2*j + 1])
            if cnt == 0:
                extraction_matrix[i][j] = 0

    return overlap_matrix, extraction_matrix

# Binary Layered Decryption (BLD)
def BLD_decrypt(secret_shares):
    binaryShareImages = [convertGrayToBinary(share) for share in secret_shares]
    binaryShareImages = [b.astype('uint8') for b in binaryShareImages]
    
    (row, column, _) = binaryShareImages[0].shape
    binaryOverlapMatrix = np.zeros((row, column, 8), dtype='uint8')
    binaryExtractionMatrix = np.zeros((row // 2, column // 2, 8), dtype='uint8')
    
    for index in range(8):
        overlap, extraction = PE_decrypt([b[:, :, index] for b in binaryShareImages])
        binaryOverlapMatrix[:, :, index] = overlap
        binaryExtractionMatrix[:, :, index] = extraction
    
    overlap_matrix = convertBinaryToGray(binaryOverlapMatrix)
    extraction_matrix = convertBinaryToGray(binaryExtractionMatrix)
    return overlap_matrix, extraction_matrix

# Test driver (optional, can be commented out if this is an import-only module)
if __name__ == "__main__":
    print("Save input image as 'Input.png' in the same folder as this file\n")
    
    try:
        input_image = Image.open('Input.png').convert('L')
    except FileNotFoundError:
        print("Input file not found!")
        exit(0)
    
    print("Image uploaded successfully!")
    print("Input image size (in pixels) : ", input_image.size)
    num_shares = int(input("Enter number of shares (2-8): "))
    num_shares = max(2, min(num_shares, 8))
    
    start_time = time.time()
    secret_shares, input_matrix = BLD_encrypt(input_image, num_shares)
    encryption_time = time.time() - start_time
    
    for i, share in enumerate(secret_shares):
        Image.fromarray(share.astype(np.uint8)).save(f"outputs/BLD_SecretShare_{i+1}.png")
    
    start_time = time.time()
    overlap_matrix, extraction_matrix = BLD_decrypt(secret_shares)
    decryption_time = time.time() - start_time
    
    extraction_output = Image.fromarray(extraction_matrix.astype(np.uint8))
    extraction_output.save('outputs/Output_BLD(Extraction).png')
    
    overlap_output = Image.fromarray(overlap_matrix.astype(np.uint8)).resize(input_image.size)
    overlap_matrix = np.asarray(overlap_output).astype(np.uint8)
    overlap_output.save('outputs/Output_BLD(Overlap).png')
    
    print(f"\nEncryption Time: {encryption_time:.4f} seconds")
    print(f"Decryption Time: {decryption_time:.4f} seconds")
    print(f"Original Hash: {compute_hash(input_matrix)}")
    print(f"Reconstructed Hash: {compute_hash(extraction_matrix)}")
    print(f"PSNR (Extraction): {psnr(input_matrix, extraction_matrix):.2f} dB")
    print(f"SSIM (Extraction): {ssim(input_matrix, extraction_matrix):.4f}")
    print(f"NCORR (Extraction): {normxcorr2D(input_matrix, extraction_matrix)}")
    print(f"PSNR (Overlap): {psnr(input_matrix, overlap_matrix):.2f} dB")
    print(f"NCORR (Overlap): {normxcorr2D(input_matrix, overlap_matrix)}")
    print(f"SSIM (Overlap): {ssim(input_matrix, overlap_matrix):.2f} dB")
