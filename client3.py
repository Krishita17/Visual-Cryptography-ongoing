import os
import time
import psutil
import numpy as np
from PIL import Image
from madec import decrypt  # Assuming this is the decrypt function for grayscale
from GrayscaleMetrics import psnr, normxcorr2D  # Assuming the Grayscale version of metrics
from skimage.metrics import structural_similarity as ssim
import hashlib
import matplotlib.pyplot as plt
import seaborn as sns

def compute_hash(img):
    return hashlib.sha256(img.tobytes()).hexdigest()

def load_shares(paths):
    return np.stack([np.array(Image.open(p).convert("L")) for p in paths], axis=-1)

def evaluate_metrics(original, output):
    mse = np.mean((original - output) ** 2)
    psnr_val = 100 if mse == 0 else 10 * np.log10((255 ** 2) / mse)
    numerator = np.sum(original * output)
    denominator = np.sqrt(np.sum(original ** 2) * np.sum(output ** 2))
    ncorr_val = numerator / denominator if denominator != 0 else 0
    ssim_val = ssim(original, output, channel_axis=0)
    return psnr_val, ncorr_val, ssim_val

def plot_metrics_and_performance(original, decrypted, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem):
    # Create figure and axes
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    # ---- Left Plot: Image Quality Metrics ----
    # Create line plots for PSNR, NCORR, SSIM
    axes[0].plot([psnr_val], 'r-', label='PSNR', marker='o')
    axes[0].plot([ncorr_val], 'g-', label='NCORR', marker='o')
    axes[0].plot([ssim_val], 'b-', label='SSIM', marker='o')

    # Title and labels
    axes[0].set_title("Image Quality Metrics")
    axes[0].set_xlabel("Image")
    axes[0].set_ylabel("Metric Value")
    axes[0].legend()

    # ---- Right Plot: Performance Metrics ----
    # Plot CPU and Memory usage during encryption and decryption
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
    image_ids = input("Enter image IDs to transfer (e.g., 'a b c'): ").split()

    for image_id in image_ids:
        combined = f"shared/client3/{image_id}/combined"
        client3 = f"shared/client3/{image_id}"

        # Get the combined share paths for all file extensions (png, jpg, etc.)
        combined_paths = sorted([  # Get the combined share paths
            os.path.join(combined, f) for f in os.listdir(combined)
            if f.endswith(".png") or f.endswith(".jpg")  # Handle both .png and .jpg files
        ])

        # Get client3's own share paths for all file extensions (png, jpg, etc.)
        own_paths = sorted([  # Get client3's own share paths
            os.path.join(client3, f) for f in os.listdir(client3)
            if (f.endswith(".png") or f.endswith(".jpg")) and "combined" not in f  # Handle both .png and .jpg files
        ])

        # Combine all share paths
        all_paths = combined_paths + own_paths
        if len(all_paths) < 2:
            print(f"❌ Not enough shares for image '{image_id}'.")
            continue

        print(f"\n🔐 Total shares used for decryption of '{image_id}': {len(all_paths)}")
        for p in all_paths:
            print(" -", p)

        # Simulate encryption system stats
        enc_start = time.time()
        enc_process = psutil.Process(os.getpid())
        enc_mem = enc_process.memory_info().rss / (1024 * 1024)
        enc_cpu = psutil.cpu_percent(interval=None)
        time.sleep(0.01)  # Simulated delay
        enc_time = time.time() - enc_start

        # Actual decryption with system stats
        dec_process = psutil.Process(os.getpid())
        dec_start = time.time()
        shares = load_shares(all_paths)
        output_img, output_matrix = decrypt(shares)
        dec_end = time.time()
        dec_mem = dec_process.memory_info().rss / (1024 * 1024)
        dec_cpu = psutil.cpu_percent(interval=0)

        os.makedirs("outputs", exist_ok=True)
        output_path = f"outputs/decrypted_MA_{image_id}.png"
        output_img.save(output_path)
        print(f"✅ Decrypted image '{image_id}' saved at: {output_path}")

        try:
            # Make sure the right file extension is used based on the image type (e.g., .jpg or .png)
            original_path = f"{image_id}.png" if os.path.exists(f"{image_id}.png") else f"{image_id}.jpg"
            original = np.array(Image.open(original_path).convert("L"))
            psnr_val, ncorr_val, ssim_val = evaluate_metrics(original, output_matrix)

            print(f"\n📊 --- Evaluation for '{image_id}' ---")
            print(f"📈 PSNR: {psnr_val:.2f} dB")
            print(f"🔎 NCORR: {ncorr_val:.6f}")
            print(f"📊 SSIM: {ssim_val:.4f}")
            print(f"🔐 Hash Match: {'YES ✅' if compute_hash(original) == compute_hash(output_matrix) else 'NO ❌'}")

            # Get image sizes
            original_size = original.shape
            decrypted_size = output_matrix.shape

            # Compute the difference image
            diff = np.abs(original - output_matrix)

            # Visualize all images and metrics together
            plot_composite_visualization(original, output_matrix, diff, original_size, decrypted_size, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem)
            
            # Plot image metrics and system performance
            plot_metrics_and_performance(original, output_matrix, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem)

        except FileNotFoundError:
            print(f"⚠️ Original image '{image_id}' not found for evaluation.")

        # System Stats Summary
        print("\n⚙️ --- System Stats ---")
        print(f"🔐 Encryption Simulated Time: {enc_time:.4f} seconds")
        print(f"🧠 Memory Used During Encryption: {enc_mem:.2f} MB")
        print(f"💻 CPU Usage During Encryption: {enc_cpu:.2f}%")
        print(f"🕒 Decryption Time: {dec_end - dec_start:.4f} seconds")
        print(f"🧠 Memory Used During Decryption: {dec_mem:.2f} MB")
        print(f"💻 CPU Usage During Decryption: {dec_cpu:.2f}%")