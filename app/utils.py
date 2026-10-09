from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import csv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMPLATE_PATH = os.path.join(ASSETS_DIR, "template.jpg")
FONT_PATH = os.path.join(ASSETS_DIR, "Roboto-Regular.ttf")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_csv_content(csv_text: str) -> list[dict]:
    """
    Parses CSV or comma-separated text into a list of recipient dictionaries:
    [{"name": "...", "course": "..."}, ...]
    Handles headers (e.g., name, course) or raw comma-separated lines.
    """
    lines = [line.strip() for line in csv_text.splitlines() if line.strip()]
    if not lines:
        return []

    reader = csv.reader(lines)
    all_rows = [row for row in reader if any(cell.strip() for cell in row)]
    if not all_rows:
        return []

    first_row = [c.strip().lower() for c in all_rows[0]]
    has_header = any("name" in col for col in first_row) and any("course" in col for col in first_row)

    name_idx = 0
    course_idx = 1
    start_idx = 0

    if has_header:
        for idx, col in enumerate(first_row):
            if "name" in col and "course" not in col:
                name_idx = idx
            elif "course" in col:
                course_idx = idx
        start_idx = 1

    recipients = []
    for row in all_rows[start_idx:]:
        name = row[name_idx].strip() if len(row) > name_idx else ""
        course = row[course_idx].strip() if len(row) > course_idx else ""
        if name or course:
            recipients.append({"name": name, "course": course})

    return recipients

def generate_certificate_image(name: str, course: str) -> str:
    """
    Generates a certificate image for a given name and course.
    Returns the file path to the generated image.
    Throws Exception on failure.
    """
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError("Certificate template not found.")

    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype(FONT_PATH, 60)
        font_medium = ImageFont.truetype(FONT_PATH, 40)
    except IOError:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()

    width, height = img.size

    # Centered recipient name and course text
    draw.text((width / 2, height / 2 - 20), name, fill="black", font=font_large, anchor="mm")
    draw.text((width / 2, height / 2 + 60), f"For completing: {course}", fill="gray", font=font_medium, anchor="mm")

    file_name = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    img.save(file_path)

    return file_path
