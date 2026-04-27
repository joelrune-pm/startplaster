import csv
import statistics
from collections import defaultdict
from pathlib import Path

from filters import filter_outliers, normalize

DATA_FILE = Path(__file__).parent / "data" / "prices.csv"


def load_prices() -> dict[str, list[float]]:
    by_day: dict[str, list[float]] = defaultdict(list)
    with DATA_FILE.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            day = row["scraped_at"][:10]
            by_day[day].append(normalize(int(row["price_sek"]), row["title"]))
    return {day: filter_outliers(prices) for day, prices in by_day.items()}


def print_report(by_day: dict[str, list[float]]) -> None:
    header = f"{'Date':<12} {'Count':>5} {'Mean':>7} {'Min':>6} {'Max':>6} {'StdDev':>8}"
    print(header)
    print("-" * len(header))
    for day in sorted(by_day):
        prices = by_day[day]
        if not prices:
            continue
        mean = statistics.mean(prices)
        std = statistics.stdev(prices) if len(prices) > 1 else 0.0
        print(f"{day:<12} {len(prices):>5} {mean:>7.0f} {min(prices):>6.0f} {max(prices):>6.0f} {std:>8.0f}")


if __name__ == "__main__":
    if not DATA_FILE.exists():
        print("No data yet. Run scrape.py first.")
    else:
        print_report(load_prices())
