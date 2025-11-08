"""
Download product images from internet
"""
import requests
import os
from pathlib import Path

# Create images directory if it doesn't exist
images_dir = Path('static/images')
images_dir.mkdir(parents=True, exist_ok=True)

# Rice Bran Oil product images - using placeholder service with realistic images
images = {
    'rbo-1l.jpg': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800&h=800&fit=crop',
    'rbo-2l.jpg': 'https://images.unsplash.com/photo-1628009368231-7bb7cfcb0def?w=800&h=800&fit=crop',
    'rbo-5l.jpg': 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=800&h=800&fit=crop',
    'rbo-10l.jpg': 'https://images.unsplash.com/photo-1598808503491-8c93f398c4c1?w=800&h=800&fit=crop',
    'rbo-15l.jpg': 'https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=800&h=800&fit=crop',
    'premium-rbo-1l.jpg': 'https://images.unsplash.com/photo-1608047092615-8b8c3c6e3cfb?w=800&h=800&fit=crop',
    'logo.png': 'https://images.unsplash.com/photo-1599305445671-ac291c95aaa9?w=400&h=200&fit=crop',
}

print("Downloading product images...")

for filename, url in images.items():
    filepath = images_dir / filename
    
    try:
        print(f"Downloading {filename}...")
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ Successfully downloaded {filename}")
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")

print("\nAll images downloaded!")
print(f"Images saved to: {images_dir.absolute()}")
