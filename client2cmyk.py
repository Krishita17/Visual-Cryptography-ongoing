import os
from PIL import Image

def process_image(image_id):
    # Define paths
    c1_path = f"shared/client1/{image_id}/CMYK_share1.png"
    c2_path = f"shared/client2/{image_id}/CMYK_share2.png"
    combined_dir = f"shared/client3/{image_id}/combined"

    # Validate existence of share files
    if not (os.path.exists(c1_path) and os.path.exists(c2_path)):
        print(f"❌ One or both share files not found for {image_id}.")
        return

    # Create combined directory if not exists
    os.makedirs(combined_dir, exist_ok=True)

    # Load and convert to CMYK just in case
    img1 = Image.open(c1_path).convert("CMYK")
    img2 = Image.open(c2_path).convert("CMYK")

    # Create a new CMYK image to hold the combined result
    combined = Image.new("CMYK", img1.size)

    # Combine channels (C from img1, M from img2, others zero)
    for x in range(img1.width):
        for y in range(img1.height):
            c = img1.getpixel((x, y))[0]
            m = img2.getpixel((x, y))[1]
            combined.putpixel((x, y), (c, m, 0, 0))

    # Save the result as RGB so PNG format accepts it
    combined.convert("RGB").save(f"{combined_dir}/CMYK_combined.png")

    print(f"✅ Client 2 combined and sent to Client 3 for image {image_id}.")

def main():
    # Input for image IDs (should match 3 images selected by server)
    image_ids = input("Enter 3 image IDs (separate by space, e.g., 'image1 image2 image3'): ").split()

    # Check if exactly 3 image IDs are provided
    if len(image_ids) != 3:
        print("❌ You must provide exactly 3 image IDs.")
        return

    # Process each image
    for image_id in image_ids:
        process_image(image_id)

if __name__ == "__main__":
    main()
