import os
import shutil
from PIL import Image
import numpy as np
from xorbinaryenc import encrypt
from tkinter import Tk, filedialog

def distribute_shares(shares, n1, n2, client_id="image1"):
    total = shares.shape[2]
    n3 = total - (n1 + n2)

    paths = [f'shared/client{i}/{client_id}' for i in range(1, 4)]
    for path in paths:
        os.makedirs(path, exist_ok=True)

    idx = 0
    for i in range(n1):
        Image.fromarray(shares[:, :, idx]).save(f'shared/client1/{client_id}/share_{i+1}.png')
        idx += 1
    for i in range(n2):
        Image.fromarray(shares[:, :, idx]).save(f'shared/client2/{client_id}/share_{i+1}.png')
        idx += 1
    for i in range(n3):
        Image.fromarray(shares[:, :, idx]).save(f'shared/client3/{client_id}/share_{i+1}.png')
        idx += 1

    print(f"\n✅ Distributed {n1} to Client 1, {n2} to Client 2, and {n3} to Client 3.")

if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    image_path = filedialog.askopenfilename(
        title="Select a grayscale image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
    )

    if not image_path:
        print("No image selected.")
        exit(0)

    image_id = os.path.splitext(os.path.basename(image_path))[0]

    if os.path.exists('shared'):
        shutil.rmtree('shared')

    os.makedirs('shared/client1', exist_ok=True)
    os.makedirs('shared/client2', exist_ok=True)
    os.makedirs('shared/client3', exist_ok=True)

    image = Image.open(image_path).convert("L")  # Grayscale
    total = int(input("🔢 Total number of shares to create (e.g., 6): "))
    n1 = int(input(f"📦 Shares to Client 1 (0 to {total-2}): "))
    n2 = int(input(f"📦 Shares to Client 2 (0 to {total-n1-1}): "))

    shares, _ = encrypt(image, total)
    distribute_shares(shares, n1, n2, image_id)
