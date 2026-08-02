#!/usr/bin/env python3
"""
Prep a photo for ASCII conversion:
  1. Remove the background (rembg) so only the subject remains
  2. Boost local contrast with CLAHE so a flat face gets real highlights/shadows
  3. Composite onto pure white -> background maps to the blank end of the ramp

Usage:
    python scripts/prep_photo.py source-photo.jpg
Writes:
    scripts/prepped-source.png  (grayscale, ready for make_ascii_svg.py)
"""
import sys
import os

import numpy as np
import cv2
from PIL import Image
from rembg import remove

OUT_PATH = os.path.join(os.path.dirname(__file__), "prepped-source.png")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <photo.jpg>")
        sys.exit(1)

    src_path = sys.argv[1]

    # 1. Remove background
    with open(src_path, "rb") as f:
        input_bytes = f.read()
    no_bg_bytes = remove(input_bytes)

    from io import BytesIO
    no_bg = Image.open(BytesIO(no_bg_bytes)).convert("RGBA")

    # 2. Composite onto pure white
    white_bg = Image.new("RGBA", no_bg.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, no_bg).convert("RGB")

    # 3. Boost local contrast with CLAHE (operates on grayscale/L channel)
    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    out_img = Image.fromarray(enhanced)
    out_img.save(OUT_PATH)
    print(f"Wrote {OUT_PATH} ({out_img.size[0]}x{out_img.size[1]})")


if __name__ == "__main__":
    main()
