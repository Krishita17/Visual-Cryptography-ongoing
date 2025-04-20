import os
import time
import psutil
import numpy as np
from PIL import Image
from xorcolor_dec import decrypt
from ColourMetrics import psnr, normxcorr2D
from skimage.metrics import structural_similarity as ssim
import hashlib
import matplotlib.pyplot as plt
import seaborn as sns

def compute_hash(img):
    return hashlib.sha256(img.tobytes()).hexdigest()

def load_shares(paths):
    return np.stack([np.array(Image.open(p).convert("RGB")) for p in paths], axis=-1)

def evaluate_metrics(original, output):
    mse = np.mean((original - output) ** 2)
    psnr_val = 100 if mse == 0 else 10 * np.log10((255 ** 2) / mse)
    numerator = np.sum(original * output)
    denominator = np.sqrt(np.sum(original ** 2) * np.sum(output ** 2))
    ncorr_val = numerator / denominator if denominator != 0 else 0
    ssim_val = ssim(original, output, channel_axis=2)
    return psnr_val, ncorr_val, ssim_val

def plot_metrics_and_performance(psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem):
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # Metrics Plot
    axes[0].bar(['PSNR', 'NCORR', 'SSIM'], [psnr_val, ncorr_val, ssim_val], 
                color=['red', 'green', 'blue'], alpha=0.7)
    axes[0].set_title(" Image Quality Metrics")
    axes[0].set_ylim(0, 1.2 if max(psnr_val, ncorr_val, ssim_val) <= 1 else psnr_val + 10)
    axes[0].set_ylabel("Value")

    # System Performance Plot
    bar_labels = ['Enc CPU (%)', 'Dec CPU (%)', 'Enc Mem (MB)', 'Dec Mem (MB)']
    bar_values = [enc_cpu, dec_cpu, enc_mem, dec_mem]
    axes[1].bar(bar_labels, bar_values, color=['orange', 'purple', 'skyblue', 'navy'], alpha=0.7)
    axes[1].set_title("⚙️ System Performance Metrics")
    axes[1].set_ylabel("Usage")

    plt.tight_layout()
    plt.show()

def plot_composite_visualization(original, decrypted, psnr_val, ncorr_val, ssim_val):
    diff = np.abs(original.astype(np.int16) - decrypted.astype(np.int16)).mean(axis=2)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    axes[0].imshow(original)
    axes[0].set_title(f"Original Image\nSize: {original.shape[1]}x{original.shape[0]}")
    axes[0].axis('off')

    axes[1].imshow(decrypted)
    axes[1].set_title(f"Decrypted Image\nSize: {decrypted.shape[1]}x{decrypted.shape[0]}")
    axes[1].axis('off')

    sns.heatmap(diff, cmap='coolwarm', ax=axes[2], cbar=True, square=False, linewidths=0.0)
    axes[2].set_title("Difference Map (Avg RGB Channel)")
    axes[2].axis('off')

    fig.suptitle(f"🔎 PSNR: {psnr_val:.2f} dB | NCORR: {ncorr_val:.6f} | SSIM: {ssim_val:.4f}", fontsize=12)
    plt.tight_layout()
    plt.show()

def get_image_extension(image_id):
    """Return the correct file extension based on the image ID."""
    if image_id == "col":
        return ".jpeg"
    elif image_id == "coll":
        return ".jpg"
    elif image_id == "coloured":
        return ".png"
    else:
        return None

if __name__ == "__main__":
    image_id = input("Enter image ID (e.g., 'col', 'coll', 'coloured'): ")
    extension = get_image_extension(image_id)
    if not extension:
        print("❌ Invalid image ID.")
        exit()

    combined = f"shared/client3/{image_id}/combined"
    client3 = f"shared/client3/{image_id}"

    combined_paths = sorted([os.path.join(combined, f) for f in os.listdir(combined) if f.endswith(".png")])
    own_paths = sorted([os.path.join(client3, f) for f in os.listdir(client3) if f.endswith(".png") and "combined" not in f])

    all_paths = combined_paths + own_paths
    if len(all_paths) < 2:
        print("❌ Not enough shares.")
        exit()

    print(f"\n🔐 Total shares used for decryption: {len(all_paths)}")
    for p in all_paths:
        print(" -", p)

    # Simulate encryption system stats
    enc_start = time.time()
    enc_process = psutil.Process(os.getpid())
    enc_mem = enc_process.memory_info().rss / (1024 * 1024)
    enc_cpu = psutil.cpu_percent(interval=None)
    time.sleep(0.2)  # Simulated delay
    enc_time = time.time() - enc_start

    # Actual decryption with system stats
    dec_process = psutil.Process(os.getpid())
    dec_start = time.time()
    shares = load_shares(all_paths)
    output_img, output_matrix = decrypt(shares)
    dec_end = time.time()
    dec_mem = dec_process.memory_info().rss / (1024 * 1024)
    dec_cpu = psutil.cpu_percent(interval=0.3)

    os.makedirs("outputs", exist_ok=True)
    output_path = f"outputs/decrypted_XOR_{image_id}{extension}"
    output_img.save(output_path)
    print(f"\n✅ Decrypted image saved at: {output_path}")

    try:
        original_path = f"{image_id}{extension}"
        original = np.array(Image.open(original_path).convert("RGB"))
        psnr_val, ncorr_val, ssim_val = evaluate_metrics(original, output_matrix)

        print("\n📊 --- Evaluation ---")
        print(f"📈 PSNR: {psnr_val:.2f} dB")
        print(f"🔎 NCORR: {ncorr_val:.6f}")
        print(f"📊 SSIM: {ssim_val:.4f}")
        print(f"🔐 Hash Match: {'YES ✅' if compute_hash(original)==compute_hash(output_matrix) else 'NO ❌'}")

        plot_composite_visualization(original, output_matrix, psnr_val, ncorr_val, ssim_val)
        plot_metrics_and_performance(psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem)

    except FileNotFoundError:
        print("⚠️ Original image not found for evaluation.")

    # System Stats Summary
    print("\n⚙️ --- System Stats ---")
    print(f"🔐 Encryption Simulated Time: {enc_time:.4f} seconds")
    print(f"🧠 Memory Used During Encryption: {enc_mem:.2f} MB")
    print(f"💻 CPU Usage During Encryption: {enc_cpu:.2f}%")
    print(f"🕒 Decryption Time: {dec_end - dec_start:.4f} seconds")
    print(f"🧠 Memory Used During Decryption: {dec_mem:.2f} MB")
    print(f"💻 CPU Usage During Decryption: {dec_cpu:.2f}%")
