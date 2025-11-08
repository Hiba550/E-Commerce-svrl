"""
Download real product images for rice bran oil products
"""
import os
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# Create images directory if it doesn't exist
images_dir = 'static/images/products'
os.makedirs(images_dir, exist_ok=True)

def create_product_image(filename, title, color_scheme):
    """Create a professional product image with gradient background"""
    # Image dimensions
    width, height = 800, 800
    
    # Create image with gradient
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for i in range(height):
        ratio = i / height
        if color_scheme == 'gold':
            r = int(255 - (ratio * 30))
            g = int(248 - (ratio * 20))
            b = int(220 - (ratio * 40))
        elif color_scheme == 'green':
            r = int(240 - (ratio * 50))
            g = int(255 - (ratio * 20))
            b = int(230 - (ratio * 50))
        else:  # amber
            r = int(255 - (ratio * 40))
            g = int(240 - (ratio * 30))
            b = int(200 - (ratio * 50))
        
        draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))
    
    # Add bottle silhouette (simple rectangle representing oil bottle)
    bottle_color = (139, 90, 43, 200)  # Brown/amber color
    bottle_width = 250
    bottle_height = 550
    bottle_x = (width - bottle_width) // 2
    bottle_y = (height - bottle_height) // 2 - 50
    
    # Draw bottle
    draw.rectangle(
        [(bottle_x, bottle_y), (bottle_x + bottle_width, bottle_y + bottle_height)],
        fill=(180, 120, 60),
        outline=(120, 80, 40),
        width=3
    )
    
    # Bottle cap
    cap_height = 40
    cap_x = bottle_x + 50
    cap_width = bottle_width - 100
    draw.rectangle(
        [(cap_x, bottle_y - cap_height), (cap_x + cap_width, bottle_y)],
        fill=(80, 50, 20),
        outline=(60, 40, 15),
        width=2
    )
    
    # Add label area on bottle
    label_margin = 30
    label_y = bottle_y + 150
    label_height = 180
    draw.rectangle(
        [(bottle_x + label_margin, label_y), 
         (bottle_x + bottle_width - label_margin, label_y + label_height)],
        fill=(255, 255, 240, 220),
        outline=(139, 90, 43),
        width=2
    )
    
    # Add text
    try:
        font_large = ImageFont.truetype("arial.ttf", 40)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Product name
    text_bbox = draw.textbbox((0, 0), "Rice Bran Oil", font=font_large)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (width - text_width) // 2
    draw.text((text_x, label_y + 50), "Rice Bran Oil", fill=(139, 90, 43), font=font_large)
    
    # Size text
    size_text = title.split(' - ')[-1] if ' - ' in title else "1L"
    text_bbox = draw.textbbox((0, 0), size_text, font=font_large)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (width - text_width) // 2
    draw.text((text_x, label_y + 110), size_text, fill=(180, 120, 60), font=font_large)
    
    # Brand name at bottom
    brand_text = "Shree Vinayaga"
    text_bbox = draw.textbbox((0, 0), brand_text, font=font_small)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (width - text_width) // 2
    draw.text((text_x, height - 80), brand_text, fill=(100, 70, 40), font=font_small)
    
    # Save image
    img.save(os.path.join(images_dir, filename), 'JPEG', quality=95)
    print(f"✓ Created {filename}")

# Create product images
print("Creating product images...")

products = [
    ('rbo-1l.jpg', 'Rice Bran Oil - 1L', 'gold'),
    ('rbo-5l.jpg', 'Rice Bran Oil - 5L', 'gold'),
    ('rbo-15l.jpg', 'Rice Bran Oil - 15L', 'gold'),
    ('cold-pressed-rbo-1l.jpg', 'Cold Pressed - 1L', 'green'),
    ('premium-rbo-1l.jpg', 'Premium Oil - 1L', 'amber'),
    ('rbo-gift-pack.jpg', 'Gift Pack - 2x1L', 'gold'),
    ('rbo-500ml.jpg', 'Rice Bran Oil - 500ml', 'gold'),
]

for filename, title, color in products:
    create_product_image(filename, title, color)

print(f"\n✓ Successfully created {len(products)} product images in {images_dir}/")
