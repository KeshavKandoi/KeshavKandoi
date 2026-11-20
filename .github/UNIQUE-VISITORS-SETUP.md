# Unique repository visitors badge — one-time setup

The profile README shows the static dark badge `traffic-unique.svg`. GitHub Actions updates it daily with the official **unique visitors to this repository over the previous 14 days**. Reloading the README does not change the SVG or increase the displayed number.

This is **not** an all-time total, and **not** a count of all visitors to the GitHub user profile.

## One-time setup

1. In GitHub, open **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token** (https://github.com/settings/personal-access-tokens/new).
2. Choose resource owner **KeshavKandoi** and limit repository access to **Only select repositories → KeshavKandoi**.
3. Under **Repository permissions**, set **Administration → Read-only**. Do not grant write or admin rights to this token. The GitHub traffic API requires this permission. Choose a suitable expiry date.
4. Generate and copy the token. **Never put it in README, a committed file, or chat.**
5. Open **KeshavKandoi/KeshavKandoi → Settings → Secrets and variables → Actions → New repository secret**.
6. Name it exactly **GH_TRAFFIC_TOKEN** and paste the token as its value.
7. Open **Actions → Update unique repository visitors → Run workflow** on branch main.
8. After the run succeeds, the top badge will show the current 14-day unique repository visitor count instead of a dash.

The workflow runs daily, writes `traffic-unique.svg` only if its content changes, and commits the updated badge using `GITHUB_TOKEN`. Standard GitHub-hosted Actions runners are free for public repositories.

If the token expires or is revoked, create a new read-only token and replace the secret. The previous badge will remain visible until the workflow updates successfully again.

The official traffic data is a rolling 14-day period: it can go up or down as days enter or leave the window. Counts for distinct people cannot be reliably generated from profile README image requests.
