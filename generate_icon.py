"""Generate the SlickClick application icon."""
from PIL import Image, ImageDraw
import os

os.makedirs("assets", exist_ok=True)

sizes = [16, 32, 48, 64, 128, 256]
images = []

for s in sizes:
    img = Image.new("RGBA", (s, s), (26, 26, 46, 255))
    d = ImageDraw.Draw(img)

    # Draw a cursor arrow shape
    cx, cy = s * 0.3, s * 0.15
    points = [
        (cx, cy),
        (cx, cy + s * 0.65),
        (cx + s * 0.18, cy + s * 0.48),
        (cx + s * 0.35, cy + s * 0.7),
        (cx + s * 0.42, cy + s * 0.63),
        (cx + s * 0.27, cy + s * 0.42),
        (cx + s * 0.45, cy + s * 0.42),
    ]
    d.polygon(points, fill=(234, 234, 234, 255))

    # Draw click ripple circles
    rx, ry = int(cx + s * 0.05), int(cy + s * 0.1)
    for r in [s * 0.35, s * 0.28, s * 0.2]:
        ri = int(r)
        d.ellipse(
            [rx - ri, ry - ri, rx + ri, ry + ri],
            outline=(233, 69, 96, 180),
            width=max(1, s // 32),
        )

    # Accent dot at cursor tip
    dot_r = max(2, s // 16)
    d.ellipse(
        [int(cx) - dot_r, int(cy) - dot_r, int(cx) + dot_r, int(cy) + dot_r],
        fill=(233, 69, 96, 255),
    )

    images.append(img)

# Save as ICO
images[-1].save(
    "assets/icon.ico",
    format="ICO",
    sizes=[(s, s) for s in sizes],
    append_images=images[:-1],
)
print("Icon created: assets/icon.ico")
