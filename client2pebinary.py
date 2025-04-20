import os
from PIL import Image

def load(path):
    return Image.open(path).convert("1")

if __name__ == "__main__":
    image_ids = input("Enter image IDs to transfer combined shares (separated by space, e.g., 'a b c'): ").split()

    for image_id in image_ids:
        c1 = f"shared/client1/{image_id}/PE_share_1.png"
        c2 = f"shared/client2/{image_id}/PE_share_2.png"
        combined_dir = f"shared/client3/{image_id}/combined"
        os.makedirs(combined_dir, exist_ok=True)

        load(c1).save(f"{combined_dir}/PE_share_1.png")
        load(c2).save(f"{combined_dir}/PE_share_2.png")

        print(f"✅ Client 2 successfully sent combined shares of '{image_id}' to Client 3.")
