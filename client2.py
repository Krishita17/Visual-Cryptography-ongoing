import os
from PIL import Image

def load_shares(folder_path):
    # Load all shares from the specified directory
    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".png")])
    return [Image.open(os.path.join(folder_path, f)).convert("L") for f in files]

if __name__ == "__main__":
    image_ids = input("Enter image IDs to transfer (e.g., 'a b c'): ").split()

    for image_id in image_ids:
        # Directories for client1 and client2 shares
        client1_dir = f"shared/client1/{image_id}"
        client2_dir = f"shared/client2/{image_id}"
        combined_dir = f"shared/client3/{image_id}/combined"

        # Make sure the combined directory exists
        os.makedirs(combined_dir, exist_ok=True)

        # If either client1 or client2 share directory does not exist, skip
        if not os.path.exists(client1_dir) or not os.path.exists(client2_dir):
            print(f"❌ Skipping '{image_id}' — Shares not found in client1 or client2.")
            continue

        # Load shares from client1 and client2
        shares_client1 = load_shares(client1_dir)
        shares_client2 = load_shares(client2_dir)

        # Combine shares from both clients
        all_shares = shares_client1 + shares_client2

        # Save all combined shares to Client 3's directory
        for i, share in enumerate(all_shares):
            share.save(os.path.join(combined_dir, f"share_{i+1}.png"))

        print(f"✅ Client 2 successfully forwarded shares of '{image_id}' to Client 3.")
