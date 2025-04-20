import os
import shutil
from PIL import Image
import numpy as np
from tkinter import Tk, filedialog
from modularbinary_enc import encrypt

def save_shares(shares, n1, n2, image_id="Input"):
    total = shares.shape[2]
    n3 = total - n1 - n2

    base_paths = [f"shared/client{i}/{image_id}" for i in range(1, 4)]
    for p in base_paths:
        os.makedirs(p, exist_ok=True)

    idx = 0
    for i in range(n1):
        Image.fromarray(shares[:, :, idx] * 255).save(f"{base_paths[0]}/MA_share_{i+1}.png")
        idx += 1
    for i in range(n2):
        Image.fromarray(shares[:, :, idx] * 255).save(f"{base_paths[1]}/MA_share_{i+1}.png")
        idx += 1
    for i in range(n3):
        Image.fromarray(shares[:, :, idx] * 255).save(f"{base_paths[2]}/MA_share_{i+1}.png")
        idx += 1

    print(f"\n✅ Distributed {n1} to Client 1, {n2} to Client 2, {n3} to Client 3.")

if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    image_path = filedialog.askopenfilename(
        title="Select a binary image",
        filetypes=[("Image Files", "*.png *.bmp")]
    )

    if not image_path:
        print("No image selected.")
        exit()

    image_id = os.path.splitext(os.path.basename(image_path))[0]

    if os.path.exists("shared"):
        shutil.rmtree("shared")

    total = int(input("🔢 Total number of shares (max 8): "))
    n1 = int(input(f"📦 Shares to Client 1 (0 to {total-2}): "))
    n2 = int(input(f"📦 Shares to Client 2 (0 to {total-n1-1}): "))

    image = Image.open(image_path)
    shares, _ = encrypt(image, total)
    save_shares(shares, n1, n2, image_id)
