import os
import urllib.request
from PIL import Image, ImageDraw

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# 1. Download Roboto font if not present
font_url = "https://cdnjs.cloudflare.com/ajax/libs/ink/3.1.10/fonts/Roboto/roboto-regular-webfont.ttf"
font_path = os.path.join(ASSETS_DIR, "Roboto-Regular.ttf")
if not os.path.exists(font_path):
    print("Downloading font...")
    try:
        urllib.request.urlretrieve(font_url, font_path)
    except Exception as e:
        print(f"Failed to download font: {e}")

# 2. Generate a dummy template image if not present
template_path = os.path.join(ASSETS_DIR, "template.jpg")
if not os.path.exists(template_path):
    print("Generating template...")
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 780, 580], outline="gold", width=10)
    img.save(template_path)

print("Assets setup complete.")
