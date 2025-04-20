import os
from PIL import Image

def load_shares(folder):
    return [Image.open(os.path.join(folder, f)).convert("RGB")
            for f in sorted(os.listdir(folder)) if f.endswith(".png")]

def combine_and_transfer_shares(image_id):
    path1 = f"shared/client1/{image_id}"
    path2 = f"shared/client2/{image_id}"
    combined_dir = f"shared/client3/{image_id}/combined"
    os.makedirs(combined_dir, exist_ok=True)

    shares1 = load_shares(path1)
    shares2 = load_shares(path2)

    all_shares = shares1 + shares2
    for i, share in enumerate(all_shares):
        share.save(f"{combined_dir}/XOR_share_{i+1}.png")

    print(f"✅ Combined and transferred {len(all_shares)} shares for image '{image_id}' to Client 3.")

if __name__ == "__main__":
    print("📥 Enter 3 image IDs (comma-separated, e.g., img1,img2,img3):")
    image_ids = input("Image IDs: ").strip().split(',')

    if len(image_ids) != 3:
        print("❌ Please enter exactly 3 image IDs.")
        exit(0)

    for img_id in image_ids:
        combine_and_transfer_shares(img_id.strip())
