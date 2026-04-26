import csv
import statistics
from collections import defaultdict
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "prices.csv"


def load_prices() -> dict[str, list[int]]:
    by_day: dict[str, list[int]] = defaultdict(list)
    with DATA_FILE.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            day = row["scraped_at"][:10]  # YYYY-MM-DD from ISO datetime
            by_day[day].append(int(row["price_sek"]))
    return by_day


def print_report(by_day: dict[str, list[int]]) -> None:
    header = f"{'Date':<12} {'Count':>5} {'Mean':>7} {'Min':>6} {'Max':>6} {'StdDev':>8}"
    print(header)
    print("-" * len(header))
    for day in sorted(by_day):
        prices = by_day[day]
        mean = statistics.mean(prices)
        low = min(prices)
        high = max(prices)
        std = statistics.stdev(prices) if len(prices) > 1 else 0.0
        print(f"{day:<12} {len(prices):>5} {mean:>7.0f} {low:>6} {high:>6} {std:>8.0f}")


if __name__ == "__main__":
    if not DATA_FILE.exists():
        print(f"No data yet. Run scrape.py first.")
    else:
        print_report(load_prices())
