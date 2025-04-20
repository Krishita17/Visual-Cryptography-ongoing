import os
import shutil
from tkinter import Tk, filedialog
from PIL import Image
from pebinaryenc import encrypt

if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    image_paths = filedialog.askopenfilenames(
        title="Select 3 binary images",
        filetypes=[("Image Files", "*.png *.bmp *.jpg *.jpeg")]
    )

    if not image_paths or len(image_paths) != 3:
        print("❌ Please select exactly 3 images.")
        exit()

    for image_path in image_paths:
        image_id = os.path.splitext(os.path.basename(image_path))[0]
        image = Image.open(image_path).convert("1")

        share1, share2 = encrypt(image)

        base_path = "shared"
        paths = [f"{base_path}/client1/{image_id}", f"{base_path}/client2/{image_id}"]
        for path in paths:
            os.makedirs(path, exist_ok=True)

        Image.fromarray(share1 * 255).save(f"{paths[0]}/PE_share_1.png")
        Image.fromarray(share2 * 255).save(f"{paths[1]}/PE_share_2.png")

        print(f"\n✅ Shared PE_share_1 of '{image_id}' to Client1 and PE_share_2 to Client2.")
