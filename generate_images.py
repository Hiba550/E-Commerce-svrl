"""
Generate placeholder product images locally using PIL
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Create images directory
images_dir = Path('static/images')
images_dir.mkdir(parents=True, exist_ok=True)

# Product configurations (name, color, text_color)
products = [
    ('rbo-1l.jpg', '#FFD700', '#1d1d1f', 'Rice Bran Oil\n1 Litre'),
    ('rbo-2l.jpg', '#FFB900', '#1d1d1f', 'Rice Bran Oil\n2 Litres'),
    ('rbo-5l.jpg', '#FFA500', '#FFFFFF', 'Rice Bran Oil\n5 Litres'),
    ('rbo-10l.jpg', '#FF8C00', '#FFFFFF', 'Rice Bran Oil\n10 Litres'),
    ('rbo-15l.jpg', '#FF7F00', '#FFFFFF', 'Rice Bran Oil\n15 Litres'),
    ('premium-rbo-1l.jpg', '#0071e3', '#FFFFFF', 'Premium\nRice Bran Oil\n1 Litre'),
    ('logo.png', '#0071e3', '#FFFFFF', 'Shree Vinayaga\nAgro')
]

print("Generating product images...")
print("=" * 50)

for filename, bg_color, text_color, text in products:
    # Determine size
    if filename == 'logo.png':
        size = (600, 200)
    else:
        size = (800, 800)
    
    # Create image
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fall back to default if not available
    try:
        font_size = 60 if filename != 'logo.png' else 50
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (center)
    # Get bounding box of text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw text
    draw.multiline_text(position, text, fill=text_color, font=font, align='center')
    
    # Save image
    filepath = images_dir / filename
    img.save(filepath, quality=95)
    
    file_size = filepath.stat().st_size / 1024  # KB
    print(f"✓ Created {filename} - {file_size:.1f} KB")

print("\n" + "=" * 50)
print(f"All {len(products)} images created successfully!")
print(f"Images saved to: {images_dir.absolute()}")
print("\nNote: These are placeholder images. Replace with actual product photos for production.")
