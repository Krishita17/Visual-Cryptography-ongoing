import os
import time
import tracemalloc
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import psutil
from PIL import Image
import hashlib
from skimage.metrics import structural_similarity as ssim
from ColourMetrics import psnr, normxcorr2D


def compute_hash(image_array):
    return hashlib.sha256(image_array.tobytes()).hexdigest()

def evaluate_metrics(original_np, reconstructed_np):
    psnr_val = psnr(original_np, reconstructed_np)
    ncorr_val = normxcorr2D(original_np, reconstructed_np)
    ssim_val = ssim(original_np, reconstructed_np, channel_axis=2)
    return psnr_val, ncorr_val, ssim_val

def find_original_image_path(image_id):
    extensions = ['.png', '.jpg', '.jpeg']
    for ext in extensions:
        candidate = f"{image_id}{ext}"
        if os.path.exists(candidate):
            return candidate
    return None
def plot_metrics_and_performance(original, decrypted, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem):
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    # Change from line plot to bar chart
    
    axes[0].bar(['PSNR', 'NCORR', 'SSIM'], [psnr_val, ncorr_val, ssim_val], 
                color=['red', 'green', 'blue'], alpha=0.7)
    axes[0].set_title(" Image Quality Metrics")
    axes[0].set_ylim(0, 1.2 if max(psnr_val, ncorr_val, ssim_val) <= 1 else psnr_val + 10)
    axes[0].set_ylabel("Value")

    
    # Adjusting y-axis limits to accommodate negative NCORR values
    max_val = max(psnr_val, ssim_val)
    min_val = min(psnr_val, ncorr_val, ssim_val)
    axes[0].set_ylim(min_val - 0.1, max_val + 10)  # Adjust y-axis for negative values in NCORR

    axes[1].bar(['Enc CPU', 'Dec CPU'], [enc_cpu, dec_cpu], color='orange', alpha=0.7, label='CPU Usage (%)')
    axes[1].bar(['Enc Mem', 'Dec Mem'], [enc_mem, dec_mem], color='blue', alpha=0.5, label='Memory Usage (MB)')

    axes[1].set_title("System Performance Metrics")
    axes[1].set_ylabel("Percentage/MB")
    axes[1].legend()

    plt.tight_layout()
    plt.show()














def plot_composite_visualization(original, decrypted, diff, original_size, decrypted_size, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    axes[0].imshow(original, cmap='gray')
    axes[0].set_title(f"Original Image\nSize: {original_size[0]}x{original_size[1]}")
    axes[0].axis('off')

    axes[1].imshow(decrypted, cmap='gray')
    axes[1].set_title(f"Decrypted Image\nSize: {decrypted_size[0]}x{decrypted_size[1]}")
    axes[1].axis('off')

    sns.heatmap(diff, cmap='coolwarm', ax=axes[2], cbar=True, square=True, linewidths=0.5)
    axes[2].set_title("Difference (Original - Decrypted)")
    axes[2].axis('off')

    fig.text(0.5, 0.01, f"PSNR: {psnr_val:.2f} dB   NCORR: {ncorr_val:.6f}   SSIM: {ssim_val:.4f}", 
             ha='center', va='center', fontsize=12, color='black')

    plt.tight_layout()
    plt.show()

def main():
    image_ids = input("Enter 3 image IDs (separate by space, e.g., 'image1 image2 image3'): ").split()

    if len(image_ids) != 3:
        print("❌ You must provide exactly 3 image IDs.")
        return

    for image_id in image_ids:
        combined_path = f"shared/client3/{image_id}/combined/CMYK_combined.png"
        original_path = find_original_image_path(image_id)

        if not os.path.exists(combined_path):
            print(f"❌ Combined image not found for {image_id}.")
            continue

        if original_path is None:
            print(f"❌ Original image not found for {image_id}.")
            continue

        # Simulate encryption time and CPU
        enc_start = time.time()
        enc_cpu_start = psutil.cpu_percent(interval=None)
        time.sleep(0.2)  # Simulated workload
        enc_cpu_end = psutil.cpu_percent(interval=None)
        enc_time = time.time() - enc_start
        enc_cpu = (enc_cpu_start + enc_cpu_end) / 2

        # Start memory tracking for decryption
        tracemalloc.start()
        dec_cpu_start = psutil.cpu_percent(interval=None)
        dec_start = time.time()

        reconstructed = Image.open(combined_path).convert("RGB")
        original = Image.open(original_path).convert("RGB")

        dec_end = time.time()
        dec_cpu_end = psutil.cpu_percent(interval=None)
        dec_cpu = (dec_cpu_start + dec_cpu_end) / 2

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Convert images to arrays
        reconstructed_np = np.array(reconstructed)
        original_np = np.array(original)

        os.makedirs("outputs", exist_ok=True)
        output_path = f"outputs/decrypted_CMYK_{image_id}.png"
        reconstructed.save(output_path)

        print(f"\n✅ Decrypted image saved at: {output_path}")
        print(f"📐 Input Image Size: {original.size[0]} x {original.size[1]} pixels")
        print(f"📐 Decrypted Image Size: {reconstructed.size[0]} x {reconstructed.size[1]} pixels")

        # Metrics
        psnr_val, ncorr_val, ssim_val = evaluate_metrics(original_np, reconstructed_np)
        hash_match = compute_hash(original_np) == compute_hash(reconstructed_np)
        diff = np.abs(original_np.astype(int) - reconstructed_np.astype(int)).sum(axis=2)

        # Display metrics
        print("\n📊 --- Evaluation ---")
        print(f"📈 PSNR: {psnr_val:.2f} dB")
        print(f"🔎 NCORR: {ncorr_val:.6f}")
        print(f"📊 SSIM: {ssim_val:.4f}")
        print(f"🔐 Hash Match: {'YES ✅' if hash_match else 'NO ❌'}")

        # System performance
        print("\n⚙️ --- System Stats ---")
        print(f"🔐 Encryption Simulated Time: {enc_time:.4f} seconds")
        print(f"💻 Encryption CPU Usage: {enc_cpu:.2f}%")
        print(f"💻 Decryption CPU Usage: {dec_cpu:.2f}%")
        print(f"🧠 Memory Used During Decryption: {current / 1024:.2f} KB (Current) / {peak / 1024:.2f} KB (Peak)")
        print(f"🕒 Decryption Time: {dec_end - dec_start:.4f} seconds")

        # Visualization
        plot_metrics_and_performance(original, reconstructed, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, current / 1024, peak / 1024)
        plot_composite_visualization(original, reconstructed, diff, original.size, reconstructed.size, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, current / 1024, peak / 1024)

if __name__ == "__main__":
    main()
