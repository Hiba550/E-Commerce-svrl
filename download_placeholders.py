"""
Download placeholder product images for Rice Bran Oil
"""
import requests
import os
from pathlib import Path

# Create images directory
images_dir = Path('static/images')
images_dir.mkdir(parents=True, exist_ok=True)

# Using placeholder images with appropriate colors and sizes
# These are free placeholder image services
images = {
    'rbo-1l.jpg': 'https://via.placeholder.com/800x800/FFD700/000000?text=Rice+Bran+Oil+1L',
    'rbo-2l.jpg': 'https://via.placeholder.com/800x800/FFD700/000000?text=Rice+Bran+Oil+2L',
    'rbo-5l.jpg': 'https://via.placeholder.com/800x800/FFD700/000000?text=Rice+Bran+Oil+5L',
    'rbo-10l.jpg': 'https://via.placeholder.com/800x800/FFD700/000000?text=Rice+Bran+Oil+10L',
    'rbo-15l.jpg': 'https://via.placeholder.com/800x800/FFD700/000000?text=Rice+Bran+Oil+15L',
    'premium-rbo-1l.jpg': 'https://via.placeholder.com/800x800/FF8C00/FFFFFF?text=Premium+RBO+1L',
    'logo.png': 'https://via.placeholder.com/400x150/0071e3/FFFFFF?text=Shree+Vinayaga',
}

print("Downloading product images...")
print("=" * 50)

success_count = 0
fail_count = 0

for filename, url in images.items():
    filepath = images_dir / filename
    
    try:
        print(f"\nDownloading: {filename}")
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        file_size = os.path.getsize(filepath) / 1024  # KB
        print(f"✓ Success! Size: {file_size:.1f} KB")
        success_count += 1
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        fail_count += 1

print("\n" + "=" * 50)
print(f"\nDownload Summary:")
print(f"✓ Successful: {success_count}/{len(images)}")
print(f"✗ Failed: {fail_count}/{len(images)}")
print(f"\nImages saved to: {images_dir.absolute()}")
print("\nNote: These are placeholder images. Replace with actual product photos for production.")
