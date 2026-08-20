import os
from PIL import Image, ImageDraw

# Extension directory check
ext_dir = os.path.join(os.getcwd(), "extension")
if not os.path.exists(ext_dir):
    os.makedirs(ext_dir)

def create_applypulse_icon(size):
    # 1. Create canvas with dark background (#0F172A)
    img = Image.new("RGBA", (size, size), color=(15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    
    scale = size / 128.0

    # 2. Draw Briefcase Body (Sky Blue #38BDF8)
    bx1, by1 = int(28 * scale), int(44 * scale)
    bx2, by2 = int(100 * scale), int(96 * scale)
    stroke_w = max(1, int(6 * scale))
    draw.rectangle([bx1, by1, bx2, by2], outline=(56, 189, 248, 255), width=stroke_w)

    # 3. Draw Briefcase Handle
    hx1, hy1 = int(46 * scale), int(30 * scale)
    hx2, hy2 = int(82 * scale), int(44 * scale)
    draw.rectangle([hx1, hy1, hx2, hy2], outline=(56, 189, 248, 255), width=stroke_w)

    # 4. Draw Green Pulse Line (#22C55E)
    points = [
        (int(18 * scale), int(70 * scale)),
        (int(38 * scale), int(70 * scale)),
        (int(48 * scale), int(50 * scale)),
        (int(58 * scale), int(88 * scale)),
        (int(70 * scale), int(60 * scale)),
        (int(78 * scale), int(70 * scale)),
        (int(110 * scale), int(70 * scale))
    ]
    pulse_w = max(1, int(7 * scale))
    draw.line(points, fill=(34, 197, 94, 255), width=pulse_w, joint="curve")

    return img

# Generate all 3 icons directly into extension/ folder
sizes = [16, 48, 128]
for s in sizes:
    icon_img = create_applypulse_icon(s)
    path = os.path.join(ext_dir, f"icon{s}.png")
    icon_img.save(path, "PNG")
    print(f"✅ Created: {path}")

print("\nAll extension icons generated successfully!")