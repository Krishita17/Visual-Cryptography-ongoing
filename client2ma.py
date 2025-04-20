import os
from PIL import Image

def load(path):
    return [Image.open(os.path.join(path, f)).convert("L") for f in sorted(os.listdir(path)) if f.endswith(".png")]

if __name__ == "__main__":
    image_id = input("Enter image ID to transfer combined shares (e.g., 'Input'): ")
    c1_path = f"shared/client1/{image_id}"
    c2_path = f"shared/client2/{image_id}"
    combined_path = f"shared/client3/{image_id}/combined"

    os.makedirs(combined_path, exist_ok=True)

    shares1 = load(c1_path)
    shares2 = load(c2_path)
    all_shares = shares1 + shares2

    for idx, img in enumerate(all_shares):
        img.save(f"{combined_path}/MA_share_{idx+1}.png")

    print(f"✅ Client 2 successfully sent {len(all_shares)} combined shares to Client 3.")
