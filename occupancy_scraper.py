#!/usr/bin/env python3
"""
Occupancy collector for lazdynubaseinas.eu
Appends one row per run to data/occupancy_lazdynu.csv.
Pure stdlib — no pip install. Designed to run in GitHub Actions on a schedule.
"""

import csv
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo
    LOCAL_TZ = ZoneInfo("Europe/Vilnius")
except Exception:
    LOCAL_TZ = None  # falls back to system local time

# ---- config ----------------------------------------------------------------
URL = "https://www.lazdynubaseinas.eu/"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "occupancy_lazdynu.csv")
UA = "Mozilla/5.0 (occupancy-logger; personal analytics; contact via site owner)"
TIMEOUT = 20
# ----------------------------------------------------------------------------

FIELDS = ["ts_utc", "ts_local", "weekday", "dow", "hour", "minute", "occupancy_pct", "status"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-8", "replace")


def extract_pct(html):
    """Anchored on '...imtumas' (užimtumas) so we grab the right number.
    Tolerant of tags/whitespace between the word and the percentage."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&nbsp;?|&#160;?", " ", text)
    m = re.search(r"imtumas[^0-9%]{0,80}?(\d{1,3})\s*%", text, re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    val = int(m.group(1))
    return val if 0 <= val <= 100 else None


def main():
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(LOCAL_TZ) if LOCAL_TZ else datetime.now()

    pct, status = None, "ok"
    try:
        html = fetch(URL)
        pct = extract_pct(html)
        if pct is None:
            status = "no_match"
    except Exception as e:
        status = f"http_error:{type(e).__name__}"

    row = {
        "ts_utc": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ts_local": now_local.strftime("%Y-%m-%d %H:%M:%S"),
        "weekday": now_local.strftime("%A"),
        "dow": now_local.weekday(),      # 0 = Monday
        "hour": now_local.hour,
        "minute": now_local.minute,
        "occupancy_pct": pct if pct is not None else "",
        "status": status,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    new_file = not os.path.exists(OUT) or os.path.getsize(OUT) == 0
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        w.writerow(row)

    print(f"{row['ts_local']}  {status}  {pct if pct is not None else '-'}%")
    # Always exit 0 so the workflow still commits no_match / error rows (visible gaps).
    sys.exit(0)


if __name__ == "__main__":
    main()
