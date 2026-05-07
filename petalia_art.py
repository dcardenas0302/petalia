from PIL import Image, ImageDraw, ImageFont
import math
import re

def clean_label(label):
    # remove weird unicode spacing characters
    return re.sub(r"[\u00A0\u200B-\u200D\uFEFF]", " ", str(label)).strip()


FLOWER_COLORS = {
    "rose": "red",
    "tulip": "pink",
    "daisy": "gold",
    "lily": "purple",
    "orchid": "violet",
    "sunflower": "orange",
    "daffodil": "yellow",
    "default": "lightgreen",
}

def draw_flower(draw, x, y, flower_type, label):
    color = FLOWER_COLORS.get(flower_type.lower(), FLOWER_COLORS["default"])

    # stem
    draw.line((x, y + 20, x, y + 80), fill="green", width=4)

    # petals
    for angle in range(0, 360, 45):
        dx = math.cos(math.radians(angle)) * 18
        dy = math.sin(math.radians(angle)) * 18
        draw.ellipse((x + dx - 10, y + dy - 10, x + dx + 10, y + dy + 10), fill=color)

    # center
    draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill="brown")

    # label
    clean = clean_label(label)
    draw.text((x - 10, y + 83), clean, fill="black")

def save_garden_image(items, output_path="petalia_output.png"):
    width = 900
    height = 650

    image = Image.new("RGB", (width, height), "skyblue")
    draw = ImageDraw.Draw(image)

    # grass
    draw.rectangle((0, 400, width, height), fill="lightgreen")

    draw.text((30, 30), "Petalia Garden Output", fill="black")

    cols = 5
    start_x = 100
    start_y = 330
    spacing_x = 160
    spacing_y = 175

    for i, (flower_type, label) in enumerate(items):
        row = i // cols
        col = i % cols
        x = start_x + col * spacing_x
        y = start_y + row * spacing_y
        draw_flower(draw, x, y, flower_type, label)

    image.save(output_path)
    print(f"Image saved as {output_path}")