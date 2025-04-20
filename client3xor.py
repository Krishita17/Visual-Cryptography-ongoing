import os
import time
import tracemalloc
import numpy as np
import psutil
from PIL import Image
from xordec import decrypt
from GrayscaleMetrics import psnr, normxcorr2D
from skimage.metrics import structural_similarity as ssim
from XOR import compute_hash
import matplotlib.pyplot as plt
import seaborn as sns


def load_shares(paths):
    return np.stack([np.array(Image.open(p).convert('L')) for p in paths], axis=-1)

def memory_usage():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    return top_stats[0].size / (1024 * 1024)  # in MB

def plot_metrics_and_performance(psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem):
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    # Quality Metrics
    metrics = ['PSNR', 'NCORR', 'SSIM']
    values = [psnr_val, ncorr_val, ssim_val]
    colors = ['red', 'green', 'blue']

    bars = axes[0].bar(metrics, values, color=colors)
    axes[0].set_title("Image Quality Metrics")
    axes[0].set_ylabel("Metric Value")
    axes[0].set_ylim(0, max(50, psnr_val + 10))  # Adjust y-axis for better visibility

    for bar in bars:
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                     f'{height:.4f}', ha='center', va='bottom', fontsize=10)

    # Performance Metrics
    perf_labels = ['Enc CPU', 'Dec CPU', 'Enc Mem', 'Dec Mem']
    perf_values = [enc_cpu, dec_cpu, enc_mem, dec_mem]
    perf_colors = ['orange', 'orange', 'blue', 'blue']

    bars2 = axes[1].bar(perf_labels, perf_values, color=perf_colors)
    axes[1].set_title("System Performance Metrics")
    axes[1].set_ylabel("Usage (%) or MB")

    for bar in bars2:
        height = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                     f'{height:.2f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.show()

def plot_composite_visualization(original, decrypted, diff, original_size, decrypted_size, psnr_val, ncorr_val, ssim_val):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    axes[0].imshow(original, cmap='gray')
    axes[0].set_title(f"Original Image\nSize: {original_size[0]}x{original_size[1]}")
    axes[0].axis('off')

    axes[1].imshow(decrypted, cmap='gray')
    axes[1].set_title(f"Decrypted Image\nSize: {decrypted_size[0]}x{decrypted_size[1]}")
    axes[1].axis('off')

    sns.heatmap(diff, cmap='coolwarm', ax=axes[2], cbar=True, square=True, linewidths=0.5)
    axes[2].set_title("Difference Heatmap")
    axes[2].axis('off')

    fig.text(0.5, 0.01,
             f"PSNR: {psnr_val:.2f} dB   NCORR: {ncorr_val:.6f}   SSIM: {ssim_val:.4f}",
             ha='center', va='center', fontsize=12, color='black')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    base_dir = "shared/client3/"
    image_ids = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

    if not image_ids:
        print("❌ No images found in shared/client3/") 
        exit(1)

    os.makedirs("outputs", exist_ok=True)

    for image_id in image_ids:
        base = os.path.join(base_dir, image_id)
        combined_dir = os.path.join(base, "combined")

        if not os.path.exists(combined_dir):
            print(f"⚠️ Skipping '{image_id}' — combined shares not found.")
            continue

        combined_paths = sorted([os.path.join(combined_dir, f) for f in os.listdir(combined_dir) if f.endswith(".png")])
        own_paths = sorted([os.path.join(base, f) for f in os.listdir(base) if f.endswith(".png")])

        all_paths = combined_paths + own_paths
        if len(all_paths) < 2:
            print(f"⚠️ Not enough shares to decrypt '{image_id}'.")
            continue

        # --- Start Memory Tracking --- 
        tracemalloc.start()

        # --- Encryption Simulation --- 
        enc_start = time.time()
        enc_cpu_before = psutil.cpu_percent(interval=None)
        time.sleep(0.01)  # Dummy processing
        enc_end = time.time()
        enc_cpu_after = psutil.cpu_percent(interval=None)
        enc_current, enc_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # --- Decryption --- 
        tracemalloc.start()
        dec_start = time.time()
        dec_cpu_before = psutil.cpu_percent(interval=None)
        shares = load_shares(all_paths)
        output_img, output_matrix = decrypt(shares)
        dec_end = time.time()
        dec_cpu_after = psutil.cpu_percent(interval=None)
        dec_current, dec_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # --- Save Outputs --- 
        output_path = f"outputs/decrypted_XOR_{image_id}.png"
        output_img.save(output_path)
        print(f"\n🖼️ Decrypted '{image_id}' saved at: {output_path}")

        # --- Evaluation and Metrics --- 
        try:
            for ext in ['.png', '.jpg', '.jpeg']:
                orig_path = f"{image_id}{ext}"
                if os.path.exists(orig_path):
                    original = np.array(Image.open(orig_path).convert('L'))
                    break
            else:
                raise FileNotFoundError

            # Resize extraction image to match the original image
            extraction_resized = np.array(Image.fromarray(output_matrix).resize(original.shape[::-1], Image.BILINEAR))

            psnr_val = psnr(original, extraction_resized)
            ncorr_val = normxcorr2D(original, extraction_resized)
            ssim_val = ssim(original, extraction_resized)

            hash_match = compute_hash(original) == compute_hash(extraction_resized)

            print(f"\n📊 Metrics for '{image_id}':")
            print(f"  ✅ PSNR        : {psnr_val:.2f} dB")
            print(f"  ✅ NCORR       : {ncorr_val:.6f}")
            print(f"  ✅ SSIM        : {ssim_val:.4f}")
            print(f"  🔐 Hash Match  : {'YES' if hash_match else 'NO'}")

            diff = np.abs(original.astype(np.int16) - extraction_resized.astype(np.int16))

            plot_composite_visualization(original, extraction_resized, diff, original.shape, extraction_resized.shape, psnr_val, ncorr_val, ssim_val)
            plot_metrics_and_performance(psnr_val, ncorr_val, ssim_val, abs(enc_cpu_after - enc_cpu_before), abs(dec_cpu_after - dec_cpu_before), abs(enc_peak) / (1024 * 1024), abs(dec_peak) / (1024 * 1024))

        except FileNotFoundError:
            print(f"❌ Original file for '{image_id}' not found. Skipping metrics and visualization.")

        print("\n⚙️ --- System Stats ---")
        print(f"🔐 Encryption Simulated Time         : {enc_end - enc_start:.4f} seconds")
        print(f"🧠 Peak Memory During Encryption     : {abs(enc_peak) / (1024 * 1024):.2f} MB")
        print(f"💻 CPU Usage During Encryption       : {abs(enc_cpu_after - enc_cpu_before):.2f}%")
        print(f"🕒 Decryption Time                   : {dec_end - dec_start:.4f} seconds")
        print(f"🧠 Peak Memory During Decryption     : {abs(dec_peak) / (1024 * 1024):.2f} MB")
        print(f"💻 CPU Usage During Decryption       : {abs(dec_cpu_after - dec_cpu_before):.2f}%")
