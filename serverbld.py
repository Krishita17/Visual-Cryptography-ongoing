# server_bld_multi.py

import os
import shutil
from PIL import Image
import numpy as np
from BLDen import BLD_encrypt, compute_hash
from tkinter import Tk, filedialog

def distribute_shares(shares_list, n1, n2, hash_val, client_id):
    total = len(shares_list)
    n3 = total - (n1 + n2)

    if n1 + n2 > total:
        print(f"❌ Error: Total shares assigned ({n1 + n2}) exceed total generated ({total})")
        return

    paths = [f'shared/client{i}/{client_id}' for i in range(1, 4)]
    for path in paths:
        os.makedirs(path, exist_ok=True)

    idx = 0
    for i in range(n1):
        Image.fromarray(shares_list[idx].astype(np.uint8)).save(f'shared/client1/{client_id}/share_{i+1}.png')
        idx += 1
    for i in range(n2):
        Image.fromarray(shares_list[idx].astype(np.uint8)).save(f'shared/client2/{client_id}/share_{i+1}.png')
        idx += 1
    for i in range(n3):
        Image.fromarray(shares_list[idx].astype(np.uint8)).save(f'shared/client3/{client_id}/share_{i+1}.png')
        idx += 1

    # Save hash to Client 1
    with open(f'shared/client1/{client_id}/hash.txt', 'w') as f:
        f.write(hash_val)

    print(f"\n✅ [{client_id}] Distributed {n1} to Client 1, {n2} to Client 2, {n3} to Client 3.")
    print(f"🔐 Hash saved at shared/client1/{client_id}/hash.txt")

if __name__ == "__main__":
    print("📁 Please select 3 grayscale images...")

    root = Tk()
    root.withdraw()
    root.update()

    file_paths = filedialog.askopenfilenames(
        title="Select 3 grayscale images",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
    )

    if len(file_paths) != 3:
        print("❌ You must select exactly 3 images.")
        exit(0)

    # Clean old shares
    if os.path.exists('shared'):
        shutil.rmtree('shared')

    for i in range(1, 4):
        os.makedirs(f'shared/client{i}', exist_ok=True)

    try:
        total = int(input("🔢 Enter total number of shares to create per image (min 3): "))
        if total < 3:
            raise ValueError("Need at least 3 shares to distribute among 3 clients.")
        n1 = int(input(f"📦 Enter shares to Client 1 (0 to {total - 2}): "))
        n2 = int(input(f"📦 Enter shares to Client 2 (0 to {total - n1 - 1}): "))
    except Exception as e:
        print(f"❌ Invalid input: {e}")
        exit(1)

    # Encrypt and distribute each image
    for path in file_paths:
        try:
            image = Image.open(path).convert('L')
            image_id = os.path.splitext(os.path.basename(path))[0]

            shares, original_image = BLD_encrypt(image, total)
            hash_val = compute_hash(original_image)

            distribute_shares(
                [shares[:, :, i] for i in range(shares.shape[2])],
                n1, n2, hash_val, image_id
            )
        except Exception as e:
            print(f"❌ Failed for image '{path}': {e}")
