import os
import shutil
from PIL import Image
from xorcolor_enc import encrypt 
from tkinter import Tk, filedialog
import numpy as np

def distribute_shares(shares, n1, n2, image_id="Input"):
    total = shares.shape[3]
    n3 = total - (n1 + n2)

    paths = [f'shared/client{i}/{image_id}' for i in range(1, 4)]
    for path in paths:
        os.makedirs(path, exist_ok=True)

    idx = 0
    for i in range(n1):
        Image.fromarray(shares[:, :, :, idx]).save(f'{paths[0]}/XOR_share_{i+1}.png')
        idx += 1
    for i in range(n2):
        Image.fromarray(shares[:, :, :, idx]).save(f'{paths[1]}/XOR_share_{i+1}.png')
        idx += 1
    for i in range(n3):
        Image.fromarray(shares[:, :, :, idx]).save(f'{paths[2]}/XOR_share_{i+1}.png')
        idx += 1

    print(f"\n✅ Distributed {n1} to Client 1, {n2} to Client 2, and {n3} to Client 3 for image '{image_id}'.")

if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    print("📂 Select 3 images:")
    image_paths = filedialog.askopenfilenames(
        title="Select three color images",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
    )

    if len(image_paths) != 3:
        print("❌ Please select exactly 3 images.")
        exit(0)

    if os.path.exists('shared'):
        shutil.rmtree('shared')
    os.makedirs('shared', exist_ok=True)

    total = int(input("🔢 Total number of shares to create for each image (max 8): "))
    n1 = int(input(f"📦 Shares to Client 1 (0 to {total-2}): "))
    n2 = int(input(f"📦 Shares to Client 2 (0 to {total-n1-1}): "))

    for image_path in image_paths:
        image = Image.open(image_path).convert("RGB")
        image_id = os.path.splitext(os.path.basename(image_path))[0]
        shares, _ = encrypt(image, total)
        distribute_shares(shares, n1, n2, image_id)
