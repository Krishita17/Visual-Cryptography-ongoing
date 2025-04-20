import numpy as np
import hashlib

def extract_colour():
    colour = [[0,0,1,1], [1,1,0,0], [1,0,0,1],[0,1,1,0],[1,0,1,0],[0,1,0,1]]
    return np.array(colour[np.random.randint(0,6)])

def compute_hash(image_matrix):
    return hashlib.sha256(image_matrix.tobytes()).hexdigest()

def convertGrayToBinary(image):
    grayScaleImage = image.copy()
    (row, column) = grayScaleImage.shape
    binaryImage = np.ones((row, column, 8))  
    
    for i in range(8):
        binaryImage[:,:,i] = (grayScaleImage.copy()) % 2
        grayScaleImage = (grayScaleImage / 2).astype('uint8')
        
    return binaryImage

def convertBinaryToGray(image):
    binaryImage = image.copy()
    (row, column, _) = binaryImage.shape
    grayScaleImage = np.zeros((row, column))
    
    for i in range(8):
        grayScaleImage = (grayScaleImage * 2 + binaryImage[:,:,7-i]).astype('uint8')
    
    return grayScaleImage

def PE_encrypt(input_matrix, num_shares):
    (row, column) = input_matrix.shape
    secret_shares = [np.empty((2*row, 2*column)).astype('uint8') for _ in range(num_shares)]
    
    for i in range(row):
        for j in range(column):
            colour = extract_colour()
            for k in range(num_shares):
                secret_shares[k][2*i][2*j] = colour[0]
                secret_shares[k][2*i + 1][2*j] = colour[1]
                secret_shares[k][2*i][2*j + 1] = colour[2]
                secret_shares[k][2*i + 1][2*j + 1] = colour[3]

            if input_matrix[i][j] == 0:
                for k in range(1, num_shares):
                    secret_shares[k][2*i][2*j] ^= 1
                    secret_shares[k][2*i + 1][2*j] ^= 1
                    secret_shares[k][2*i][2*j + 1] ^= 1
                    secret_shares[k][2*i + 1][2*j + 1] ^= 1
    
    return secret_shares

def BLD_encrypt(input_image, num_shares):
    input_matrix = np.asarray(input_image)
    binaryDecomposition = convertGrayToBinary(input_matrix.copy())
    
    (row, column, _) = binaryDecomposition.shape
    binaryShareImages = [np.zeros((2*row, 2*column, 8)).astype('uint8') for _ in range(num_shares)]
    
    for index in range(8):
        shares = PE_encrypt(binaryDecomposition[:,:,index], num_shares)
        for k in range(num_shares):
            binaryShareImages[k][:,:,index] = shares[k]
    
    secret_shares = [convertBinaryToGray(binaryShareImages[k]) for k in range(num_shares)]
    
    # ✅ FIXED RETURN: Return as numpy array so server code works
    return np.stack(secret_shares, axis=-1), input_matrix
