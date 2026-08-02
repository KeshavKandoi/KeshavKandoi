#!/usr/bin/env python3
"""
Fetch a public GitHub contribution calendar without any API token.

GitHub serves the calendar fragment used on the profile page at:
    https://github.com/users/<username>/contributions
This is public HTML, no auth required. We parse the day cells with
BeautifulSoup and write out raw days + derived stats.
"""
import json
import os
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "KeshavKandoi")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_html(username: str) -> str:
    resp = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.text


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # GitHub renders each day as a <td> with class "ContributionCalendar-day"
    # and data-date / data-level attributes (newer markup), falling back to
    # <rect> elements with data-date/data-count (older markup) just in case.
    cells = soup.select("td.ContributionCalendar-day")
    if cells:
        for cell in cells:
            date = cell.get("data-date")
            level = cell.get("data-level")
            if date is None:
                continue
            tooltip_id = cell.get("id")
            count = 0
            tt = soup.find("tool-tip", attrs={"for": tooltip_id}) if tooltip_id else None
            if tt and tt.text:
                txt = tt.text.strip().split(" ")[0].replace(",", "")
                if txt.isdigit():
                    count = int(txt)
            days.append({
                "date": date,
                "level": int(level) if level is not None else 0,
                "count": count,
            })
    else:
        rects = soup.select("rect[data-date]")
        for r in rects:
            date = r.get("data-date")
            count = r.get("data-count")
            level = r.get("data-level")
            days.append({
                "date": date,
                "level": int(level) if level is not None else 0,
                "count": int(count) if count and count.isdigit() else 0,
            })

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)

    # Current streak: consecutive days with count > 0, walking back from the
    # most recent day that has data.
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly = {}
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": monthly,
    }


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    html = fetch_html(username)
    days = parse_days(html)

    if not days:
        print("WARNING: no contribution cells parsed - GitHub markup may have "
              "changed, or the account has no public contribution graph.",
              file=sys.stderr)

    stats = compute_stats(days)
    payload = {
        "username": username,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "days": days,
        "stats": stats,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote {len(days)} days -> {OUT_PATH}")
    print(f"Total: {stats['total_last_year']} | "
          f"Current streak: {stats['current_streak']} | "
          f"Longest streak: {stats['longest_streak']}")


if __name__ == "__main__":
    main()
