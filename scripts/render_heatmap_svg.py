#!/usr/bin/env python3
"""
Renders data/contributions.json into an animated SVG contribution heatmap.

Reveal animation: boxes slide down + fade in, staggered diagonally
(week index + day index), then freeze. No infinite looping "glow" -
it plays once per page load, which is what GitHub's <img> embedding
actually supports well.
"""
import json
import os
from collections import defaultdict
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
# index 0..4 = GitHub's own levels, index 5 = neon top accent for the single
# best day, drawn as a distinct highlight rather than a real "level 5".

BOX = 11
GAP = 3
CELL = BOX + GAP
LEFT_PAD = 30      # room for day-of-week labels
TOP_PAD = 32        # room for month labels
RIGHT_PAD = 16
BOTTOM_PAD = 46     # room for legend + stats line

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DOW_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}  # Mon=0 .. Sun=6, sparse labels


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def bucket_by_week(days):
    """Group ISO days into GitHub-style columns (weeks), Sunday-start."""
    weeks = defaultdict(dict)  # week_index -> {dow: day}
    if not days:
        return [], 0

    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    # Align to the Sunday on/before the first date so column 0 is a full week
    start_dow = (first_date.weekday() + 1) % 7  # convert Mon=0..Sun=6 -> Sun=0..Sat=6

    for d in days:
        date = datetime.strptime(d["date"], "%Y-%m-%d")
        dow = (date.weekday() + 1) % 7
        delta_days = (date - first_date).days + start_dow
        week_idx = delta_days // 7
        weeks[week_idx][dow] = d

    max_week = max(weeks.keys()) if weeks else 0
    return weeks, max_week


def month_label_positions(weeks):
    """Return {week_index: 'Mon'} for the first week where a new month starts."""
    labels = {}
    seen_months = set()
    for week_idx in sorted(weeks.keys()):
        for dow in sorted(weeks[week_idx].keys()):
            date = datetime.strptime(weeks[week_idx][dow]["date"], "%Y-%m-%d")
            key = (date.year, date.month)
            if key not in seen_months:
                seen_months.add(key)
                labels[week_idx] = MONTH_NAMES[date.month - 1]
            break
    return labels


def render(data):
    days = data["days"]
    stats = data["stats"]
    username = data.get("username", "")

    weeks, max_week = bucket_by_week(days)
    n_weeks = max_week + 1

    width = LEFT_PAD + n_weeks * CELL + RIGHT_PAD
    height = TOP_PAD + 7 * CELL + BOTTOM_PAD

    best_date = stats["best_day"]["date"] if stats.get("best_day") else None

    svg_parts = []
    svg_parts.append(
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="Consolas, \'SF Mono\', '
        f'\'Courier New\', monospace">'
    )

    svg_parts.append(f'''
    <style>
      .bg {{ fill: #0d1117; }}
      .lbl {{ fill: #8b949e; font-size: 10px; }}
      .stat {{ fill: #c9d1d9; font-size: 11px; }}
      .accent {{ fill: #39d353; font-size: 11px; font-weight: bold; }}
      .box {{
        opacity: 0;
        transform: translateY(-6px);
        animation: revealBox 0.4s ease-out forwards;
      }}
      @keyframes revealBox {{
        to {{ opacity: 1; transform: translateY(0); }}
      }}
    </style>
    <rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="6"/>
    ''')

    # Month labels
    for week_idx, label in month_label_positions(weeks).items():
        x = LEFT_PAD + week_idx * CELL
        svg_parts.append(f'<text class="lbl" x="{x}" y="{TOP_PAD - 10}">{label}</text>')

    # Day-of-week labels (Sun=0..Sat=6)
    for dow, label in DOW_LABELS.items():
        y = TOP_PAD + dow * CELL + BOX - 2
        svg_parts.append(f'<text class="lbl" x="0" y="{y}">{label}</text>')

    # Boxes
    max_delay = 0.0
    for week_idx in range(n_weeks):
        for dow in range(7):
            day = weeks.get(week_idx, {}).get(dow)
            x = LEFT_PAD + week_idx * CELL
            y = TOP_PAD + dow * CELL

            if not day:
                color = PALETTE[0]
                delay = 0
            else:
                level = min(max(day.get("level", 0), 0), 4)
                color = PALETTE[level]
                if best_date and day["date"] == best_date:
                    color = PALETTE[5]
                delay = (week_idx * 7 + dow) * 0.0035
                max_delay = max(max_delay, delay)

            title = f'{day["date"]}: {day["count"]} contributions' if day else ""
            svg_parts.append(
                f'<rect class="box" x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                f'rx="2" fill="{color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{title}</title></rect>'
            )

    # Legend: Less -> More
    legend_y = TOP_PAD + 7 * CELL + 20
    legend_x = LEFT_PAD
    svg_parts.append(f'<text class="lbl" x="{legend_x}" y="{legend_y + 8}">Less</text>')
    lx = legend_x + 32
    for color in PALETTE[:5]:
        svg_parts.append(f'<rect x="{lx}" y="{legend_y}" width="{BOX}" height="{BOX}" rx="2" fill="{color}"/>')
        lx += CELL
    svg_parts.append(f'<text class="lbl" x="{lx + 4}" y="{legend_y + 8}">More</text>')

    # Stats line
    total = stats.get("total_last_year", 0)
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    stat_y = legend_y + 22
    svg_parts.append(
        f'<text class="stat" x="{legend_x}" y="{stat_y}">{total:,} contributions in the last year'
        f' &#183; <tspan class="accent">{streak}</tspan> day streak'
        f' &#183; longest {longest} days</text>'
    )

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def main():
    data = load_data()
    svg = render(data)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
