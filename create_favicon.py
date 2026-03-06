from PIL import Image, ImageDraw, ImageOps
import os

def make_circular_favicon(input_path, output_path, size=(64, 64)):
    # Open the image
    img = Image.open(input_path).convert("RGBA")
    
    # Resize image to target favicon size
    img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
    
    # Create circular mask
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    
    # Apply mask
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    
    # Save as PNG
    output.save(output_path, "PNG")

# Paths
logo_path = r'c:\Users\balakrishna\OneDrive\Desktop\ok\static\images\logo.jpeg'
favicon_path = r'c:\Users\balakrishna\OneDrive\Desktop\ok\static\images\favicon.png'

if os.path.exists(logo_path):
    make_circular_favicon(logo_path, favicon_path)
    print("Circular favicon created successfully.")
else:
    print(f"Logo file not found at: {logo_path}")
