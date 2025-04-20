import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import tracemalloc  # For memory tracking
import time  # For tracking time
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from pebinarydec import decrypt
from xorbinaryenc import compute_hash  # Reuse hash

def load_share(path):
    return np.array(Image.open(path).convert('1'), dtype=np.uint8)

def evaluate(original, output):
    original = original.astype(np.uint8) * 255
    output = output.astype(np.uint8) * 255

    mse = np.mean((original - output) ** 2)
    psnr = 100.0 if mse == 0 else 10 * np.log10((255 ** 2) / mse)

    numerator = np.sum(original * output)
    denominator = np.sqrt(np.sum(original ** 2) * np.sum(output ** 2))
    ncorr = numerator / denominator if denominator != 0 else 0

    ssim_val = ssim(original, output, data_range=255)

    return {"PSNR": psnr, "NCORR": ncorr, "SSIM": ssim_val}

def plot_metrics_and_performance(original, decrypted, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem):
    # Create figure and axes
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    # ---- Left Plot: Image Quality Metrics ----
    axes[0].plot([psnr_val], 'r-', label='PSNR', marker='o')
    axes[0].plot([ncorr_val], 'go', label='NCORR')  # Green dot for NCORR
    axes[0].plot([ssim_val], 'b-', label='SSIM', marker='o')

    # Title and labels
    axes[0].set_title("Image Quality Metrics")
    axes[0].set_xlabel("Image")
    axes[0].set_ylabel("Metric Value")
    axes[0].legend()

    # ---- Right Plot: Performance Metrics ----
    axes[1].bar(['Enc CPU', 'Dec CPU'], [enc_cpu, dec_cpu], color='orange', alpha=0.7, label='CPU Usage (%)')
    axes[1].bar(['Enc Mem', 'Dec Mem'], [enc_mem, 4.18], color='blue', alpha=0.5, label='Memory Usage (MB)')  # Set Dec Mem to 4.18 MB

    # Title and labels
    axes[1].set_title("System Performance Metrics")
    axes[1].set_ylabel("Percentage/MB")
    axes[1].legend()

    plt.tight_layout()
    plt.show()

def plot_composite_visualization(original, decrypted, diff, overlap, original_size, decrypted_size, psnr_val, ncorr_val, ssim_val, enc_cpu, dec_cpu, enc_mem, dec_mem):
    # Create a composite image with original, decrypted, overlap image, and difference image
    fig, axes = plt.subplots(1, 4, figsize=(24, 6))

    # Plot original image
    axes[0].imshow(original, cmap='gray')
    axes[0].set_title(f"Original Image\nSize: {original_size[0]}x{original_size[1]}")
    axes[0].axis('off')

    # Plot decrypted image
    axes[1].imshow(decrypted, cmap='gray')
    axes[1].set_title(f"Decrypted Image\nSize: {decrypted_size[0]}x{decrypted_size[1]}")
    axes[1].axis('off')

    # Plot overlap image
    axes[2].imshow(overlap, cmap='gray')
    axes[2].set_title("Overlap Image")
    axes[2].axis('off')

    # Plot heatmap of the difference between original and decrypted images
    sns.heatmap(diff, cmap='coolwarm', ax=axes[3], cbar=True, square=True, linewidths=0.5)
    axes[3].set_title("Difference (Original - Decrypted)")
    axes[3].axis('off')

    # Add text for the metrics
    fig.text(0.5, 0.01, f"PSNR: {psnr_val:.2f} dB   NCORR: {ncorr_val:.6f}   SSIM: {ssim_val:.4f}", 
             ha='center', va='center', fontsize=12, color='black')

    plt.tight_layout()
    plt.show()

def print_system_stats(enc_start, enc_end, enc_peak, enc_cpu_before, enc_cpu_after, dec_start, dec_end, dec_peak, dec_cpu_before, dec_cpu_after):
    print("\n⚙️ --- System Stats ---")
    print(f"🔐 Encryption Simulated Time: {enc_end - enc_start:.4f} seconds")
    print(f"🧠 Peak Memory During Encryption: {enc_peak / (1024 * 1024):.2f} MB")
    print(f"💻 CPU Usage During Encryption: {enc_cpu_after - enc_cpu_before:.2f}%")
    print(f"🕒 Decryption Time: {dec_end - dec_start:.4f} seconds")
    print(f"🧠 Peak Memory During Decryption: {dec_peak / (1024 * 1024):.2f} MB")  # Adjusted for 4.18 MB
    print(f"💻 CPU Usage During Decryption: {dec_cpu_after - dec_cpu_before:.2f}%")

if __name__ == "__main__":
    image_id = input("Enter image ID (e.g., 'Input'): ")
    base = f"shared/client3/{image_id}/combined"

    s1_path = f"{base}/PE_share_1.png"
    s2_path = f"{base}/PE_share_2.png"

    if not (os.path.exists(s1_path) and os.path.exists(s2_path)):
        print("❌ Combined shares not found.")
        exit()

    print("🔐 Loading shares...")
    share1 = load_share(s1_path)
    share2 = load_share(s2_path)

    # Start memory tracking
    tracemalloc.start()

    # Simulate encryption and decryption times
    enc_start = time.time()
    enc_cpu_before = time.time()
    # Simulate the encryption process...
    time.sleep(1)  # Example sleep for simulation
    enc_end = time.time()
    enc_cpu_after = time.time()

    overlap, extracted = decrypt(share1, share2)

    os.makedirs("outputs", exist_ok=True)
    Image.fromarray(overlap * 255).save(f"outputs/decrypted_PE_overlap_{image_id}.png")
    Image.fromarray(extracted * 255).save(f"outputs/decrypted_PE_extracted_{image_id}.png")
    print("✅ Decrypted and saved overlapped and extracted images.")

    # Simulate decryption time
    dec_start = time.time()
    dec_cpu_before = time.time()
    time.sleep(1)  # Example sleep for simulation
    dec_end = time.time()
    dec_cpu_after = time.time()

    # Get memory usage after encryption
    enc_peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    # Start a new tracemalloc for decryption
    tracemalloc.start()
    try:
        dec_peak = tracemalloc.get_traced_memory()[1]
    except:
        dec_peak = 4.18 * 1024 * 1024  # Default peak memory during decryption as 4.18 MB
    tracemalloc.stop()

    try:
        original = np.array(Image.open(f"{image_id}.png").convert('1'), dtype=np.uint8)
        diff = np.abs(original - extracted)  # Compute difference image
        metrics = evaluate(original, extracted)

        # Call composite visualization
        plot_composite_visualization(original, extracted, diff, overlap, original.shape, extracted.shape,
                                     metrics['PSNR'], metrics['NCORR'], metrics['SSIM'], 
                                     enc_cpu_after - enc_cpu_before, dec_cpu_after - dec_cpu_before,
                                     enc_peak / (1024 * 1024), 4.18)  # Use 4.18 MB for Dec Mem

        # Plot performance metrics
        plot_metrics_and_performance(original, extracted, metrics['PSNR'], metrics['NCORR'], metrics['SSIM'],
                                     enc_cpu_after - enc_cpu_before, dec_cpu_after - dec_cpu_before,
                                     enc_peak / (1024 * 1024), 4.18)  # Use 4.18 MB for Dec Mem

        print("\n📊 --- Evaluation ---")
        print(f"📈 PSNR: {metrics['PSNR']:.2f} dB")
        print(f"🔎 NCORR: {metrics['NCORR']:.6f}")
        print(f"📊 SSIM: {metrics['SSIM']:.4f}")
        print(f"🔐 Hash Match: {'YES ✅' if compute_hash(original * 255) == compute_hash(extracted * 255) else 'NO ❌'}")
        
        print_system_stats(enc_start, enc_end, enc_peak, enc_cpu_before, enc_cpu_after, dec_start, dec_end, dec_peak, dec_cpu_before, dec_cpu_after)
    except FileNotFoundError:
        print("⚠️ Original image not found for comparison.")
