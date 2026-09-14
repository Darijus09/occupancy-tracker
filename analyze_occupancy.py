#!/usr/bin/env python3
"""
Quick look at collected occupancy data.
Reads occupancy_lazdynu.csv and prints a weekday x hour average grid.
Pure stdlib. Run whenever you want a sanity check:  python3 analyze_occupancy.py
"""

import csv
import os
from collections import defaultdict

CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "occupancy_lazdynu.csv")
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def main():
    sums = defaultdict(float)   # (dow, hour) -> sum
    counts = defaultdict(int)   # (dow, hour) -> n
    total_rows, ok_rows = 0, 0

    with open(CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            total_rows += 1
            if r["status"] != "ok" or r["occupancy_pct"] == "":
                continue
            ok_rows += 1
            key = (int(r["dow"]), int(r["hour"]))
            sums[key] += float(r["occupancy_pct"])
            counts[key] += 1

    print(f"rows: {total_rows} total, {ok_rows} usable\n")
    hours = range(6, 24)  # tweak to the pool's open hours

    header = "hr  " + "  ".join(DAYS)
    print(header)
    for h in hours:
        cells = []
        for d in range(7):
            n = counts[(d, h)]
            if n:
                cells.append(f"{sums[(d, h)] / n:3.0f}")
            else:
                cells.append("  .")
        print(f"{h:02d}  " + "  ".join(cells))

    print("\n(numbers = avg occupancy %, '.' = no data yet)")


if __name__ == "__main__":
    main()
