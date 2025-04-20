import os
from PIL import Image

def load_shares(folder_path):
    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".png")])
    return [Image.open(os.path.join(folder_path, f)).convert("L") for f in files]

if __name__ == "__main__":
    image_id = input("Enter image ID to transfer combined shares (e.g., 'a'): ")

    client1_dir = f"shared/client1/{image_id}"
    client2_dir = f"shared/client2/{image_id}"

    combined_dir = f"shared/client3/{image_id}/combined"
    os.makedirs(combined_dir, exist_ok=True)

    shares_client1 = load_shares(client1_dir)
    shares_client2 = load_shares(client2_dir)

    all_shares = shares_client1 + shares_client2

    for i, share in enumerate(all_shares):
        share.save(os.path.join(combined_dir, f"share_{i+1}.png"))

    print(f"✅ Client 2 successfully sent {len(all_shares)} combined shares to Client 3.")
