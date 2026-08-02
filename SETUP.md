# Setup notes (delete this file before pushing, it's just for you)

1. Copy everything in this folder into your cloned `KeshavKandoi` repo
   (except this SETUP.md).

2. Once you send me your photo, I'll generate `ascii-portrait.svg` for you
   and hand it back — drop that in too.

3. Install deps and do a local smoke test (optional but recommended):
   ```
   python -m venv .venv && source .venv/bin/activate
   pip install -r scripts/requirements.txt
   python scripts/fetch_contributions.py KeshavKandoi
   python scripts/render_heatmap_svg.py
   python scripts/make_info_card.py
   ```

4. Commit and push:
   ```
   git add .
   git commit -m "profile art: ascii portrait, info card, live heatmap"
   git push
   ```

5. Go to the repo's **Actions** tab → "Update profile art" → **Run workflow**
   once by hand to confirm it commits a fresh heatmap. After that it runs
   automatically every day at ~06:17 UTC.

6. To update the info card text later (new project, new role, etc.), edit
   the `ROWS` list in `scripts/make_info_card.py`, rerun it, commit, push.
