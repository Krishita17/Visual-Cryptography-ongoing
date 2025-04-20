# server.py

import os
import shutil
from PIL import Image
import numpy as np
from XOR import encrypt
from tkinter import Tk, filedialog

def distribute_shares(shares, n1, n2, client_id):
    total = shares.shape[2]
    n3 = total - (n1 + n2)

    for i in range(1, 4):
        os.makedirs(f'shared/client{i}/{client_id}', exist_ok=True)

    idx = 0
    for i in range(n1):
        Image.fromarray(shares[:, :, idx].astype(np.uint8)).save(f'shared/client1/{client_id}/share_{i+1}.png')
        idx += 1
    for i in range(n2):
        Image.fromarray(shares[:, :, idx].astype(np.uint8)).save(f'shared/client2/{client_id}/share_{i+1}.png')
        idx += 1
    for i in range(n3):
        Image.fromarray(shares[:, :, idx].astype(np.uint8)).save(f'shared/client3/{client_id}/share_{i+1}.png')
        idx += 1

    print(f"[{client_id}] Distributed {n1} to Client 1, {n2} to Client 2, and {n3} to Client 3.")

if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(
        title="Select THREE grayscale images",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
    )

    if len(file_paths) != 3:
        print("You must select exactly 3 images.")
        exit(0)

    if os.path.exists('shared'):
        shutil.rmtree('shared')

    os.makedirs('shared/client1', exist_ok=True)
    os.makedirs('shared/client2', exist_ok=True)
    os.makedirs('shared/client3', exist_ok=True)

    try:
        total = int(input("Total number of shares to create for each image (2–8): "))
        if total < 2 or total > 8:
            raise ValueError
        n1 = int(input(f"Shares to Client 1 (0 to {total-2}): "))
        n2 = int(input(f"Shares to Client 2 (0 to {total-n1-1}): "))
    except ValueError:
        print("Invalid input.")
        exit(0)

    for path in file_paths:
        image_id = os.path.splitext(os.path.basename(path))[0]
        image = Image.open(path).convert('L')
        shares, _ = encrypt(image, total)
        distribute_shares(shares, n1, n2, image_id)
