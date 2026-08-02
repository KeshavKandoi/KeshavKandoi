#!/usr/bin/env python3
"""
Builds a neofetch-style info card SVG: a title bar + colored key/value rows,
each fading + sliding in on a short stagger.

Set STATIC=1 to emit a version with no animation (useful for a quick local
preview / Quick Look on macOS, where SMIL/CSS keyframes don't always play).
"""
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")
STATIC = os.environ.get("STATIC") == "1"

# --- Edit this block to update the card content ---
USERNAME = "keshav@github"
ROWS = [
    ("Now", "Final-year B.E. (ISE), job hunting"),
    ("Prev", "VectorShift technical assessment"),
    ("Stack", "React Native/Expo, Node.js, FastAPI"),
    ("Highlight", "LetsTalk - live on Play Store (testing)"),
    ("Highlight", "HealthGuard AI"),
    ("Highlight", "Offline AI Chatbot (Electron + Ollama)"),
]
# ---------------------------------------------------

WIDTH = 490
ROW_H = 26
TITLE_H = 40
PAD_X = 20
HEIGHT = TITLE_H + len(ROWS) * ROW_H + 24

KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"
TITLE_COLOR = "#8b949e"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_rows():
    parts = []
    y = TITLE_H + 22
    for i, (key, val) in enumerate(ROWS):
        anim = ""
        if not STATIC:
            delay = 0.15 + i * 0.12
            anim = f' style="animation-delay:{delay:.2f}s"'
        row_class = "row" if not STATIC else "row row-static"
        parts.append(
            f'<g class="{row_class}"{anim}>'
            f'<text x="{PAD_X}" y="{y}" class="key">{esc(key)}:</text>'
            f'<text x="{PAD_X + 92}" y="{y}" class="val">{esc(val)}</text>'
            f'</g>'
        )
        y += ROW_H
    return "\n".join(parts)


def build():
    anim_css = "" if STATIC else '''
      .row { opacity: 0; transform: translateX(-8px); animation: fadeSlide 0.45s ease-out forwards; }
      @keyframes fadeSlide { to { opacity: 1; transform: translateX(0); } }
      .cursor { animation: blink 1s step-end infinite; }
      @keyframes blink { 50% { opacity: 0; } }
    '''
    cursor = '<tspan class="cursor">_</tspan>' if not STATIC else ""

    svg = f'''<svg viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}"
     xmlns="http://www.w3.org/2000/svg"
     font-family="Consolas, 'SF Mono', 'Courier New', monospace">
  <style>
    .bg {{ fill: {BG_COLOR}; }}
    .titlebar {{ fill: #161b22; }}
    .title {{ fill: {TITLE_COLOR}; font-size: 12px; }}
    .key {{ fill: {KEY_COLOR}; font-size: 12px; font-weight: bold; }}
    .val {{ fill: {VAL_COLOR}; font-size: 12px; }}
    {anim_css}
  </style>

  <rect class="bg" x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="8"/>
  <rect class="bg" x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="8"
        fill="none" stroke="{BORDER_COLOR}"/>
  <rect class="titlebar" x="0" y="0" width="{WIDTH}" height="{TITLE_H}" rx="8"/>
  <rect class="titlebar" x="0" y="{TITLE_H - 8}" width="{WIDTH}" height="8"/>
  <circle cx="20" cy="{TITLE_H/2}" r="5" fill="#ff5f56"/>
  <circle cx="38" cy="{TITLE_H/2}" r="5" fill="#ffbd2e"/>
  <circle cx="56" cy="{TITLE_H/2}" r="5" fill="#27c93f"/>
  <text x="{WIDTH/2}" y="{TITLE_H/2 + 4}" text-anchor="middle" class="title">{USERNAME}</text>

  {build_rows()}
  <text x="{PAD_X}" y="{HEIGHT - 10}" class="val">{cursor}</text>
</svg>'''
    return svg


def main():
    svg = build()
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
