import os
from PIL import Image
import numpy as np

def load_shares(folder):
    files = sorted([f for f in os.listdir(folder) if f.endswith(".png")])
    return [np.array(Image.open(os.path.join(folder, f)).convert("RGB")) for f in files]

if __name__ == "__main__":
    image_ids = input("Enter 3 image IDs to transfer combined shares (separated by space): ").split()

    if len(image_ids) != 3:
        print("❌ Please enter exactly 3 image IDs.")
        exit()

    for image_id in image_ids:
        client1_path = f"shared/client1/{image_id}"
        client2_path = f"shared/client2/{image_id}"
        combined_path = f"shared/client3/{image_id}/combined"
        os.makedirs(combined_path, exist_ok=True)

        try:
            shares1 = load_shares(client1_path)
            shares2 = load_shares(client2_path)
        except FileNotFoundError as e:
            print(f"❌ Error loading shares for '{image_id}': {e}")
            continue

        combined = shares1 + shares2

        for i, share in enumerate(combined):
            Image.fromarray(share).save(f"{combined_path}/MA_share_{i+1}.png")

        print(f"✅ Client 2 successfully sent {len(combined)} combined shares to Client 3 for image ID '{image_id}'.")
