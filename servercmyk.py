import os
from PIL import Image
from tkinter import Tk, filedialog
from enccmyk import cmyk_encrypt  # Make sure this contains the encrypt logic

def main():
    root = Tk()
    root.withdraw()

    # Select 3 images
    image_paths = filedialog.askopenfilenames(
        title="Select 3 color images (preferably in RGB or CMYK)",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tif")]
    )

    if len(image_paths) != 3:
        print("❌ You must select exactly 3 images.")
        return

    for image_path in image_paths:
        image_id = os.path.splitext(os.path.basename(image_path))[0]
        image = Image.open(image_path).convert("CMYK")

        # Encrypt
        share1, share2, input_matrix = cmyk_encrypt(image)

        # Output paths
        paths = [
            f"shared/client1/{image_id}",
            f"shared/client2/{image_id}",
            f"shared/client3/{image_id}"
        ]

        for path in paths:
            os.makedirs(path, exist_ok=True)

        # Save after converting to RGB (PNG doesn't support CMYK directly)
        share1.convert("RGB").save(f"{paths[0]}/CMYK_share1.png")
        share2.convert("RGB").save(f"{paths[1]}/CMYK_share2.png")

        print(f"\n✅ Server distributed shares for image {image_id}:")
        print(f" - To Client 1: {paths[0]}/CMYK_share1.png")
        print(f" - To Client 2: {paths[1]}/CMYK_share2.png")

if __name__ == "__main__":
    main()
