#!/usr/bin/env python3
"""Update a static badge with the repository's official 14-day unique visitors."""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

OWNER = "KeshavKandoi"
REPO = "KeshavKandoi"
BADGE = Path(__file__).resolve().parents[1] / "visitor-count.svg"


def make_badge(count: int) -> str:
    number = str(count)
    label_width = 218
    value_width = max(46, 24 + len(number) * 10)
    width = label_width + value_width
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="28" viewBox="0 0 {width} 28" role="img" aria-label="Unique repository visitors in the last 14 days: {number}">
  <title>Unique visitors to this GitHub repository in the last 14 days: {number}. Not overall GitHub profile views.</title>
  <rect width="{width}" height="28" rx="5" fill="#24292e"/>
  <rect x="{label_width}" y="0" width="{value_width}" height="28" fill="#101923"/>
  <rect x="0.5" y="0.5" width="{width - 1}" height="27" rx="4.5" fill="none" stroke="#39424e"/>
  <rect width="3" height="28" rx="1.5" fill="#58a6ff"/>
  <g font-family="Arial,sans-serif" font-weight="600" text-anchor="middle">
    <text x="{(label_width + 3) / 2:.1f}" y="18" fill="#e6edf3" font-size="11">VISITORS</text>
    <text x="{label_width + value_width / 2:.1f}" y="18" fill="#79c0ff" font-size="12">{number}</text>
  </g>
</svg>
'''

def main():
    token = os.environ.get("GH_TRAFFIC_TOKEN", "").strip()
    if not token:
        raise SystemExit("Missing GH_TRAFFIC_TOKEN GitHub Actions secret")
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/traffic/views"
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "repository-traffic-badge",
    })
    with urlopen(request, timeout=20) as response:
        data = json.load(response)
    uniques = data.get("uniques")
    if type(uniques) is not int or uniques < 0:
        raise RuntimeError("Unexpected GitHub traffic response: invalid uniques")
    rendered = make_badge(uniques)
    if not BADGE.exists() or BADGE.read_text(encoding="utf-8") != rendered:
        BADGE.write_text(rendered, encoding="utf-8")
    print(f"Unique visitors to this repository over the last 14 days: {uniques}")


if __name__ == "__main__":
    main()
