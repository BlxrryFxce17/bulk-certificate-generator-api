import os
import urllib.request
from PIL import Image, ImageDraw

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# 1. Download Roboto font
font_url = "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Regular.ttf"
font_path = os.path.join(ASSETS_DIR, "Roboto-Regular.ttf")
if not os.path.exists(font_path):
    print("Downloading font...")
    try:
        urllib.request.urlretrieve(font_url, font_path)
    except Exception as e:
        print(f"Failed to download font: {e}")

# 2. Generate a dummy template image
template_path = os.path.join(ASSETS_DIR, "template.jpg")
if not os.path.exists(template_path):
    print("Generating dummy template...")
    # 800x600 white image with a border
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 780, 580], outline="gold", width=10)
    # Just generic placeholder as we may not have the font loaded yet
    img.save(template_path)

print("Assets setup complete.")
