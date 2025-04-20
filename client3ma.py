import os
import numpy as np
from PIL import Image
from modularbinary_dec import decrypt
from skimage.metrics import structural_similarity as ssim
from BinaryMetrics import psnr, normxcorr2D

def compute_hash(img_array):
    import hashlib
    return hashlib.sha256(img_array.tobytes()).hexdigest()

def load_shares(paths):
    return np.stack([np.array(Image.open(p).convert("L")) // 255 for p in sorted(paths)], axis=-1)

def evaluate_metrics(orig, recon):
    mse = np.mean((orig - recon) ** 2)
    psnr_val = 100.0 if mse == 0 else 10 * np.log10((255 ** 2) / mse)

    numerator = np.sum(orig * recon)
    denominator = np.sqrt(np.sum(orig ** 2) * np.sum(recon ** 2))
    ncorr_val = 0 if denominator == 0 else numerator / denominator

    ssim_val = ssim(orig, recon, data_range=255)

    return psnr_val, ncorr_val, ssim_val

if __name__ == "__main__":
    image_id = input("Enter image ID (e.g. 'Input'): ")
    base = f"shared/client3/{image_id}"

    combined_path = os.path.join(base, "combined")
    combined = [os.path.join(combined_path, f) for f in os.listdir(combined_path) if f.endswith(".png")] if os.path.exists(combined_path) else []
    own = [os.path.join(base, f) for f in os.listdir(base) if f.endswith(".png")]

    all_paths = combined + own
    if len(all_paths) < 2:
        print("❌ Not enough shares to decrypt.")
        exit()

    print(f"\n🔐 Total shares used for decryption: {len(all_paths)}")
    for p in all_paths:
        print(" -", p)

    shares = load_shares(all_paths)
    output_img, output_np = decrypt(shares)

    os.makedirs("outputs", exist_ok=True)
    output_path = f"outputs/decrypted_MA_{image_id}.png"
    output_img.save(output_path)
    print(f"\n✅ Decrypted image saved at: {output_path}")

    try:
        original = np.array(Image.open(f"{image_id}.png").convert("L"))
        psnr_val, ncorr_val, ssim_val = evaluate_metrics(original, output_np * 255)
        print("\n📊 --- Evaluation ---")
        print(f"📈 PSNR: {psnr_val:.2f} dB")
        print(f"🔎 NCORR: {ncorr_val:.6f}")
        print(f"📊 SSIM: {ssim_val:.4f}")
        print(f"🔐 Hash Match: {'YES ✅' if compute_hash(original) == compute_hash(output_np * 255) else 'NO ❌'}")
    except:
        print("⚠️ Original image not found for comparison.")
