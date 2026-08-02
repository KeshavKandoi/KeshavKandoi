#!/usr/bin/env python3
"""
Converts scripts/prepped-source.png into a self-typing, monochrome ASCII SVG.

Design choices:
  - One light-gray fill color only (no per-character rainbow -> avoids the
    "noisy static" look).
  - High contrast composite (from prep_photo.py) so the busy background
    washes to the blank glyph and only the subject prints.
  - Each row wipes left-to-right via a clip-path animation, staggered
    top-to-bottom, with a small block "cursor" riding the wipe edge.
  - Plays once and freezes - no looping.

Usage:
    python scripts/make_ascii_svg.py
Writes:
    avi-ascii.svg  (renamed appropriately for this project)
"""
import os
from PIL import Image

SRC_PATH = os.path.join(os.path.dirname(__file__), "prepped-source.png")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "ascii-portrait.svg")

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense); leading space = blank
COLS = 100
ROWS = 53

CHAR_W = 6.0   # px per column in the output SVG (monospace cell width)
CHAR_H = 11.5  # px per row (monospace cell height)
FONT_SIZE = 11
FILL_COLOR = "#c9d1d9"   # single light-gray fill - no rainbow

ROW_WIPE_DURATION = 0.9   # seconds for one row to fully wipe in
ROW_STAGGER = 0.045       # seconds between successive row starts


def image_to_ascii_rows(img: Image.Image):
    img = img.convert("L").resize((COLS, ROWS))
    pixels = list(img.tobytes())
    ramp_len = len(RAMP)

    rows = []
    for r in range(ROWS):
        row_chars = []
        for c in range(COLS):
            brightness = pixels[r * COLS + c]  # 0 = black, 255 = white
            # invert: brighter pixel -> sparser (earlier) ramp character
            idx = int((255 - brightness) / 255 * (ramp_len - 1))
            row_chars.append(RAMP[idx])
        rows.append("".join(row_chars))
    return rows


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_svg(rows):
    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    svg_parts = [
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, \'SF Mono\', \'Courier New\', monospace">',
        '<style>',
        f'  text {{ fill: {FILL_COLOR}; font-size: {FONT_SIZE}px; white-space: pre; }}',
        '  .row-clip rect { animation: wipe var(--dur) linear forwards; animation-delay: var(--delay); }',
        '  @keyframes wipe { from { width: 0; } to { width: 100%; } }',
        '  .cursor { animation: ride var(--dur) linear forwards, blinkOut 0.01s linear forwards; animation-delay: var(--delay), calc(var(--delay) + var(--dur)); }',
        '  @keyframes ride { from { transform: translateX(0); } to { transform: translateX(100%); } }',
        '  @keyframes blinkOut { to { opacity: 0; } }',
        '</style>',
        '<rect x="0" y="0" width="100%" height="100%" fill="#0d1117"/>',
    ]

    for i, row in enumerate(rows):
        y = (i + 1) * CHAR_H - 2
        row_width = COLS * CHAR_W
        delay = i * ROW_STAGGER
        clip_id = f"clip{i}"

        svg_parts.append(
            f'<clipPath id="{clip_id}">'
            f'<g class="row-clip" style="--dur:{ROW_WIPE_DURATION}s;--delay:{delay:.3f}s">'
            f'<rect x="0" y="{y - CHAR_H + 2}" height="{CHAR_H}" width="0"/>'
            f'</g></clipPath>'
        )
        svg_parts.append(
            f'<text x="0" y="{y}" clip-path="url(#{clip_id})">{esc(row)}</text>'
        )
        # small block cursor riding the wipe edge
        svg_parts.append(
            f'<rect class="cursor" x="0" y="{y - CHAR_H + 3}" width="{CHAR_W}" height="{CHAR_H - 2}" '
            f'fill="{FILL_COLOR}" style="--dur:{ROW_WIPE_DURATION}s;--delay:{delay:.3f}s" '
            f'transform-origin="0 0">'
            f'<title></title></rect>'
        )

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def main():
    if not os.path.exists(SRC_PATH):
        print(f"Missing {SRC_PATH}. Run prep_photo.py first.")
        return
    img = Image.open(SRC_PATH)
    rows = image_to_ascii_rows(img)
    svg = build_svg(rows)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
