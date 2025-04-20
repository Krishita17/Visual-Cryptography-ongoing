import os
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from xorbinarydec import decrypt
from xorbinaryenc import compute_hash

def load_binary_shares(paths):
    return np.stack([np.array(Image.open(p).convert('L')) for p in sorted(paths)], axis=-1)

def evaluate_metrics(original, output):
    mse = np.mean((original - output) ** 2)

    # Handle perfect match
    if mse == 0:
        psnr_value = 100.0
    else:
        psnr_value = 10 * np.log10((255 ** 2) / mse)

    # Normalized Cross-Correlation (NCORR)
    numerator = np.sum(original * output)
    denominator = np.sqrt(np.sum(original ** 2) * np.sum(output ** 2))
    n_corr = numerator / denominator if denominator != 0 else 0

    # Structural Similarity Index (SSIM)
    ssim_value = ssim(original, output, data_range=255)

    return {
        "PSNR": psnr_value,
        "NCORR": n_corr,
        "SSIM": ssim_value
    }

if __name__ == "__main__":
    image_id = input("Enter image ID (e.g., 'a'): ")
    base = f"shared/client3/{image_id}"

    # Load Client 3's own shares
    client3_own_paths = sorted([
        os.path.join(base, f) for f in os.listdir(base)
        if f.endswith(".png") and not f.startswith("._")
    ])

    # Load combined shares from Client 1 and 2
    combined_dir = os.path.join(base, 'combined')
    if not os.path.exists(combined_dir):
        print("❌ Combined shares not found. Make sure Client 2 has sent them.")
        exit(1)

    combined_paths = sorted([
        os.path.join(combined_dir, f) for f in os.listdir(combined_dir)
        if f.endswith(".png") and not f.startswith("._")
    ])

    all_paths = combined_paths + client3_own_paths
    if len(all_paths) < 2:
        print("❌ Not enough shares to decrypt.")
        exit(1)

    print(f"\n🔐 Total shares used for decryption: {len(all_paths)}")
    for p in all_paths:
        print(" -", p)

    shares_stack = load_binary_shares(all_paths)
    output_image, output_matrix = decrypt(shares_stack)

    os.makedirs("outputs", exist_ok=True)
    output_path = f"outputs/decrypted_BINARY_{image_id}.png"
    output_image.save(output_path)
    print(f"\n✅ Decrypted binary image saved at: {output_path}")

    # Evaluation
    try:
        original = np.array(Image.open(f"{image_id}.png").convert('L'))
        print("\n📊 --- Evaluation ---")
        metrics = evaluate_metrics(original, output_matrix)
        print(f"📈 PSNR: {metrics['PSNR']:.2f} dB")
        print(f"🔎 NCORR: {metrics['NCORR']:.6f}")
        print(f"📊 SSIM: {metrics['SSIM']:.4f}")
        print(f"🔐 Hash Match: {'YES ✅' if compute_hash(original) == compute_hash(output_matrix) else 'NO ❌'}")
    except FileNotFoundError:
        print("⚠️ Original image not found for comparison.")
