# Lazdynų baseinas occupancy tracker

Scrapes the live occupancy % from [lazdynubaseinas.eu](https://www.lazdynubaseinas.eu/)
every 15 minutes via GitHub Actions, stores each reading in `data/occupancy_lazdynu.csv`,
and shows the weekday × hour averages on a GitHub Pages dashboard.

No servers, no cost (public repo). Runs itself.

```
occupancy_scraper.py            # the collector (pure stdlib)
analyze_occupancy.py            # optional local sanity check (prints a text grid)
index.html                      # the dashboard (GitHub Pages)
data/occupancy_lazdynu.csv      # created on first run; one row per scrape
.github/workflows/scrape.yml    # the every-15-min schedule
```

## One-time setup

1. **Create a new GitHub repo** and push these files to it.
   Make it **Public** — that's what makes Actions minutes and Pages free.
   ```bash
   cd occupancy-tracker
   git init && git add . && git commit -m "init"
   git branch -M main
   git remote add origin https://github.com/<you>/<repo>.git
   git push -u origin main
   ```

2. **Give Actions permission to commit data back.**
   Repo → **Settings → Actions → General → Workflow permissions** →
   select **Read and write permissions** → Save.
   (Without this the scraper runs but can't save the CSV.)

3. **Turn on the dashboard.**
   Repo → **Settings → Pages** → Source: **Deploy from a branch** →
   Branch: **main**, folder: **/ (root)** → Save.
   Your dashboard appears at `https://<you>.github.io/<repo>/` within a minute or two.

4. **Kick off the first run manually** (don't wait for the schedule):
   Repo → **Actions** tab → **scrape-occupancy** → **Run workflow**.
   Check the run log — it should print a line like `... ok 54%`, and a new commit
   should appear updating `data/occupancy_lazdynu.csv`.

That's it. From now on it runs on its own.

## What to check on the first run

- **Run log says `ok NN%`** → working.
- **Run log says `no_match`** → the site either rendered the number with JavaScript
  (so a plain fetch can't see it) or changed its markup. Send that back and it's a
  quick fix to the extractor.
- **Commit step says "no changes to commit"** → the scraper didn't produce a new
  row (usually an error); check the "Run scraper" step output.

## Reality checks

- **GitHub's cron is best-effort.** Runs commonly land 15–30 min late and one gets
  skipped now and then. Irrelevant here — you're averaging over weeks, so jitter
  and the odd missed sample wash out.
- **Give it 2–3 weeks** before the pattern is trustworthy. Each weekday+hour cell
  needs several samples across several weeks to mean anything. The dashboard shows
  a dashed outline for cells with no data yet.
- **The source counter may only refresh every 30–60 min.** If so, some consecutive
  15-min rows will be identical — harmless, and the average is unaffected.

## Data format

`data/occupancy_lazdynu.csv`

| column | meaning |
|---|---|
| `ts_utc` | timestamp, UTC |
| `ts_local` | timestamp, Europe/Vilnius |
| `weekday` | Monday…Sunday |
| `dow` | 0=Mon … 6=Sun |
| `hour`, `minute` | local hour/minute |
| `occupancy_pct` | 0–100, or blank if not read |
| `status` | `ok`, `no_match`, or `http_error:*` |

## Adding more venues later

Each venue is its own scraper + CSV. When you're ready, the pattern is: copy
`occupancy_scraper.py`, change `URL` and the extraction anchor, write to a second
CSV, and add the dashboard a second heatmap. Different sites format the number
differently (and some *will* be JavaScript-rendered), so each one is a small
per-site job — but the plumbing above stays identical.
