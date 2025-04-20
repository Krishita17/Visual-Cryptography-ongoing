import os
import time
import psutil
import numpy as np
from PIL import Image
from modularcolor_dec import decrypt
from ColourMetrics import psnr, normxcorr2D
from skimage.metrics import structural_similarity as ssim
import hashlib
import matplotlib.pyplot as plt
import seaborn as sns

def compute_hash(arr):
    return hashlib.sha256(arr.tobytes()).hexdigest()

def load_shares(paths):
    return np.stack([np.array(Image.open(p).convert("RGB")) for p in sorted(paths)], axis=-1)

def find_original_image(image_id):
    for ext in ['.png', '.jpg', '.jpeg']:
        path = f"{image_id}{ext}"
        if os.path.exists(path):
            return path
    return None

def plot_metrics_and_performance(original, decrypted, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem):
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    
    axes[0].bar(['PSNR', 'NCORR', 'SSIM'], [psnr_val, ncorr_val, ssim_val], 
                color=['red', 'green', 'blue'], alpha=0.7)
    axes[0].set_title("Image Quality Metrics")
    max_val = max(psnr_val, ssim_val)
    min_val = min(psnr_val, ncorr_val, ssim_val)
    axes[0].set_ylim(min_val - 0.1, max_val + 10)
    axes[0].set_ylabel("Value")

    axes[1].bar(['Enc CPU', 'Dec CPU'], [enc_cpu, dec_cpu], color='orange', alpha=0.7, label='CPU Usage (%)')
    axes[1].bar(['Enc Mem', 'Dec Mem'], [enc_mem, dec_mem], color='blue', alpha=0.5, label='Memory Usage (MB)')
    axes[1].set_title("System Performance Metrics")
    axes[1].set_ylabel("Percentage / MB")
    axes[1].legend()

    plt.tight_layout()
    plt.show()

def plot_composite_visualization(original, decrypted, diff, original_size, decrypted_size, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    axes[0].imshow(original)
    axes[0].set_title(f"Original Image\nSize: {original_size[0]}x{original_size[1]}")
    axes[0].axis('off')

    axes[1].imshow(decrypted)
    axes[1].set_title(f"Decrypted Image\nSize: {decrypted_size[0]}x{decrypted_size[1]}")
    axes[1].axis('off')

    sns.heatmap(diff, cmap='coolwarm', ax=axes[2], cbar=True, square=True, linewidths=0.5)
    axes[2].set_title("Difference (Original - Decrypted)")
    axes[2].axis('off')

    fig.text(0.5, 0.01, f"PSNR: {psnr_val:.2f} dB   NCORR: {ncorr_val:.6f}   SSIM: {ssim_val:.4f}", 
             ha='center', va='center', fontsize=12, color='black')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    image_id = input("Enter image ID (e.g. 'Input'): ")
    base = f"shared/client3/{image_id}"
    combined_dir = os.path.join(base, "combined")

    combined_paths = sorted([
        os.path.join(combined_dir, f) for f in os.listdir(combined_dir)
        if f.endswith(".png")
    ])
    client3_own_paths = sorted([
        os.path.join(base, f) for f in os.listdir(base)
        if f.endswith(".png") and not f.startswith("._")
    ])

    all_paths = combined_paths + client3_own_paths
    print(f"\n🔐 Total shares used for decryption: {len(all_paths)}")
    for path in all_paths:
        print(" -", path)

    enc_process = psutil.Process(os.getpid())
    enc_start_time = time.time()
    enc_cpu_start = psutil.cpu_percent(interval=None)
    enc_mem_info = enc_process.memory_info()

    shares_stack = np.stack(
        [np.array(Image.open(p).convert("RGB")) for p in all_paths], axis=-1
    )

    enc_end_time = time.time()
    enc_cpu_end = psutil.cpu_percent(interval=0.5)

    dec_process = psutil.Process(os.getpid())
    dec_start_time = time.time()
    output_img, output_np = decrypt(shares_stack)
    dec_end_time = time.time()
    dec_mem_info = dec_process.memory_info()
    dec_cpu_end = psutil.cpu_percent(interval=0.5)

    os.makedirs("outputs", exist_ok=True)
    output_path = f"outputs/decrypted_MA_{image_id}.png"
    output_img.save(output_path)
    print(f"\n✅ Decrypted image saved at: {output_path}")

    original_path = find_original_image(image_id)
    if original_path:
        original = np.array(Image.open(original_path).convert("RGB"))
        print("\n📊 --- Evaluation ---")
        psnr_val = psnr(original, output_np)
        ncorr_val = normxcorr2D(original, output_np)
        ssim_val = ssim(original, output_np, channel_axis=2)
        hash_match = compute_hash(original) == compute_hash(output_np)

        print(f"📈 PSNR: {psnr_val:.2f} dB")
        print(f"🔎 NCORR: {ncorr_val:.6f}")
        print(f"📊 SSIM: {ssim_val:.4f}")
        print(f"🔐 Hash Match: {'YES ✅' if hash_match else 'NO ❌'}")

        diff = np.abs(original.astype(np.int32) - output_np.astype(np.int32)).sum(axis=2)
        plot_metrics_and_performance(original, output_np, psnr_val, ncorr_val, ssim_val,
                                     enc_cpu_end, dec_cpu_end,
                                     enc_mem_info.rss / (1024 * 1024), dec_mem_info.rss / (1024 * 1024))
        plot_composite_visualization(original, output_np, diff,
                                     original.shape[:2], output_np.shape[:2],
                                     psnr_val, ncorr_val, ssim_val,
                                     enc_cpu_end, dec_cpu_end,
                                     enc_mem_info.rss / (1024 * 1024), dec_mem_info.rss / (1024 * 1024))
    else:
        print("⚠️ Original image not found for evaluation.")

    print("\n⚙️ --- System Stats ---")
    print(f"🔐 Encryption Simulated Time: {enc_end_time - enc_start_time:.4f} seconds")
    print(f"🧠 Memory Used During Encryption: {enc_mem_info.rss / (1024 * 1024):.2f} MB")
    print(f"💻 CPU Usage During Encryption: {enc_cpu_end:.2f}%")
    print(f"🕒 Decryption Time: {dec_end_time - dec_start_time:.4f} seconds")
    print(f"🧠 Memory Used During Decryption: {dec_mem_info.rss / (1024 * 1024):.2f} MB")
    print(f"💻 CPU Usage During Decryption: {dec_cpu_end:.2f}%")

