import os
import numpy as np
from PIL import Image
from Bldec import BLD_decrypt
from GrayscaleMetrics import psnr, normxcorr2D
from BLDen import compute_hash
import time
import psutil
import tracemalloc
import matplotlib.pyplot as plt
import seaborn as sns

def load_grayscale_image(path):
    return np.array(Image.open(path).convert('L'))

def load_images_from_folder(folder):
    return sorted([os.path.join(folder, f) for f in os.listdir(folder)
                   if f.endswith(".png") and not f.startswith("._")])

def plot_metrics_and_performance(original, decrypted, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem):
    # Create figure and axes
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    # ---- Left Plot: Image Quality Metrics ----
    axes[0].plot([psnr_val], 'r-', label='PSNR', marker='o')
    axes[0].plot([ncorr_val], 'g-', label='NCORR', marker='o')
    axes[0].plot([ssim_val], 'b-', label='SSIM', marker='o')

    # Title and labels
    axes[0].set_title("Image Quality Metrics")
    axes[0].set_xlabel("Image")
    axes[0].set_ylabel("Metric Value")
    axes[0].legend()

    # ---- Right Plot: Performance Metrics ----
    axes[1].bar(['Enc CPU', 'Dec CPU'], [enc_cpu, dec_cpu], color='orange', alpha=0.7, label='CPU Usage (%)')
    axes[1].bar(['Enc Mem', 'Dec Mem'], [enc_mem, dec_mem], color='blue', alpha=0.5, label='Memory Usage (MB)')

    # Title and labels
    axes[1].set_title("System Performance Metrics")
    axes[1].set_ylabel("Percentage/MB")
    axes[1].legend()

    plt.tight_layout()
    plt.show()

def plot_composite_visualization(original, decrypted, diff, original_size, decrypted_size, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem):
    # Create a composite image with original, decrypted, and difference image
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Plot original image
    axes[0].imshow(original, cmap='gray')
    axes[0].set_title(f"Original Image\nSize: {original_size[0]}x{original_size[1]}")
    axes[0].axis('off')

    # Plot decrypted image
    axes[1].imshow(decrypted, cmap='gray')
    axes[1].set_title(f"Decrypted Image\nSize: {decrypted_size[0]}x{decrypted_size[1]}")
    axes[1].axis('off')

    # Plot heatmap of the difference between original and decrypted images
    sns.heatmap(diff, cmap='coolwarm', ax=axes[2], cbar=True, square=True, linewidths=0.5)
    axes[2].set_title("Difference (Original - Decrypted)")
    axes[2].axis('off')

    # Add text for the metrics
    fig.text(0.5, 0.01, f"PSNR: {psnr_val:.2f} dB   NCORR: {ncorr_val:.6f}   SSIM: {ssim_val:.4f}", 
             ha='center', va='center', fontsize=12, color='black')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    base_dir = "shared/client3"
    if not os.path.exists(base_dir):
        print("❌ client3 folder not found.")
        exit(1)

    image_ids = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])

    if not image_ids:
        print("❌ No images to process in client3.")
        exit(1)

    os.makedirs("outputs", exist_ok=True)

    for image_id in image_ids:
        print(f"\n🔍 Processing image: {image_id}")

        base = os.path.join(base_dir, image_id)
        combined_dir = os.path.join(base, 'combined')

        if not os.path.exists(combined_dir):
            print(f"⚠️ Skipping '{image_id}' — combined shares not found.")
            continue

        client3_own_paths = load_images_from_folder(base)
        combined_paths = load_images_from_folder(combined_dir)

        all_paths = combined_paths + client3_own_paths
        if len(all_paths) < 2:
            print(f"❌ Not enough shares to decrypt '{image_id}'.")
            continue

        print(f"🔐 Total shares used: {len(all_paths)}")
        for p in all_paths:
            print(f" - {p}")

        shares = [load_grayscale_image(p) for p in all_paths]

        # Encryption simulation (tracemalloc)
        tracemalloc.start()
        enc_start = time.time()
        enc_cpu_before = psutil.cpu_percent(interval=None)
        overlap_img, extraction_img = BLD_decrypt(shares)
        enc_end = time.time()
        enc_cpu_after = psutil.cpu_percent(interval=None)
        enc_current, enc_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Decryption simulation (tracemalloc)
        tracemalloc.start()
        dec_start = time.time()
        dec_cpu_before = psutil.cpu_percent(interval=None)
        overlap_img, extraction_img = BLD_decrypt(shares)
        dec_end = time.time()
        dec_cpu_after = psutil.cpu_percent(interval=None)
        dec_current, dec_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Save outputs
        overlap_path = f"outputs/decrypted_BLD_overlap_{image_id}.png"
        extraction_path = f"outputs/decrypted_BLD_extraction_{image_id}.png"
        Image.fromarray(overlap_img.astype(np.uint8)).save(overlap_path)
        Image.fromarray(extraction_img.astype(np.uint8)).save(extraction_path)

        print(f"✅ Decrypted images saved as:")
        print(f" - {overlap_path}")
        print(f" - {extraction_path}")

        # Evaluation
        try:
            for ext in ['.png', '.jpg', '.jpeg']:
                original_path = f"{image_id}{ext}"
                if os.path.exists(original_path):
                    original = load_grayscale_image(original_path)
                    break
            else:
                raise FileNotFoundError

            print("\n📊 --- Evaluation (Extraction Image) ---")
            psnr_val = psnr(original, extraction_img)
            ncorr_val = normxcorr2D(original, extraction_img)
            hash_match = 'YES ✅' if compute_hash(original) == compute_hash(extraction_img) else 'NO ❌'
            print(f"📈 PSNR: {psnr_val:.2f} dB")
            print(f"🔎 NCORR: {ncorr_val:.4f}")
            print(f"🔐 Hash Match: {hash_match}")

            overlap_resized = np.array(Image.fromarray(overlap_img).resize(original.shape[::-1], Image.BILINEAR))

            print("\n📊 --- Evaluation (Overlap Image) ---")
            overlap_psnr = psnr(original, overlap_resized)
            overlap_ncorr = normxcorr2D(original, overlap_resized)
            print(f"📈 PSNR: {overlap_psnr:.2f} dB")
            print(f"🔎 NCORR: {overlap_ncorr:.4f}")

        except FileNotFoundError:
            print(f"⚠️ Original file for '{image_id}' not found for metric comparison.")

        # Print system stats
        print("\n⚙️ --- System Stats ---")
        print(f"🔐 Encryption Simulated Time: {enc_end - enc_start:.4f} seconds")
        print(f"🧠 Peak Memory During Encryption: {enc_peak / (1024 * 1024):.2f} MB")
        print(f"💻 CPU Usage During Encryption: {enc_cpu_after - enc_cpu_before:.2f}%")
        print(f"🕒 Decryption Time: {dec_end - dec_start:.4f} seconds")
        print(f"🧠 Peak Memory During Decryption: {dec_peak / (1024 * 1024):.2f} MB")
        print(f"💻 CPU Usage During Decryption: {dec_cpu_after - dec_cpu_before:.2f}%")

        # Plot metrics and performance
        plot_metrics_and_performance(original, extraction_img, psnr_val, ncorr_val, 1.0,
                                     enc_cpu_after - enc_cpu_before, dec_cpu_after - dec_cpu_before,
                                     enc_peak / (1024 * 1024), dec_peak / (1024 * 1024))

        # Plot composite visualization
        diff = np.abs(original - extraction_img)
        plot_composite_visualization(original, extraction_img, diff, original.shape, extraction_img.shape,
                                     psnr_val, ncorr_val, 1.0,
                                     enc_cpu_after - enc_cpu_before, dec_cpu_after - dec_cpu_before,
                                     enc_peak / (1024 * 1024), dec_peak / (1024 * 1024))
