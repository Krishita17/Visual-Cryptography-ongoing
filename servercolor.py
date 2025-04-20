import os
import shutil
from PIL import Image
import numpy as np
from tkinter import Tk, filedialog
from modularcolor_enc import encrypt

def distribute_shares(shares, n1, n2, image_id):
    total = shares.shape[3]
    n3 = total - (n1 + n2)
    paths = [f"shared/client{i}/{image_id}" for i in range(1, 4)]
    for p in paths:
        os.makedirs(p, exist_ok=True)

    idx = 0
    for i in range(n1):
        Image.fromarray(shares[:, :, :, idx]).save(f"{paths[0]}/MA_share_{i+1}.png")
        idx += 1
    for i in range(n2):
        Image.fromarray(shares[:, :, :, idx]).save(f"{paths[1]}/MA_share_{i+1}.png")
        idx += 1
    for i in range(n3):
        Image.fromarray(shares[:, :, :, idx]).save(f"{paths[2]}/MA_share_{i+1}.png")
        idx += 1

    print(f"\n✅ Distributed {n1} to Client 1, {n2} to Client 2, and {n3} to Client 3.")

if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    print("🖼️ Select 3 image files (PNG, JPG, JPEG, BMP)...")
    file_paths = filedialog.askopenfilenames(
        title="Select 3 color images",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
    )

    if len(file_paths) != 3:
        print("❌ Please select exactly 3 images.")
        exit()

    # Clear existing shared directory
    if os.path.exists("shared"):
        shutil.rmtree("shared")
    os.makedirs("shared", exist_ok=True)

    total = int(input("🔢 Total number of shares to create for each image (max 8): "))
    n1 = int(input(f"📦 Shares to Client 1 (0 to {total - 2}): "))
    n2 = int(input(f"📦 Shares to Client 2 (0 to {total - n1 - 1}): "))

    for file_path in file_paths:
        image_id = os.path.splitext(os.path.basename(file_path))[0]
        image = Image.open(file_path).convert("RGB")
        shares, _ = encrypt(image, total)
        distribute_shares(shares, n1, n2, image_id)
