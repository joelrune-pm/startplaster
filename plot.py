import csv
import statistics
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from filters import filter_outliers, normalize

DATA_FILE = Path(__file__).parent / "data" / "prices.csv"
OUT_FILE = Path(__file__).parent / "data" / "prices.png"
RACE_DAY = date(2026, 6, 30)


def load_by_day() -> dict[date, list[float]]:
    by_day: dict[date, list[float]] = defaultdict(list)
    with DATA_FILE.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            day = date.fromisoformat(row["scraped_at"][:10])
            by_day[day].append(normalize(int(row["price_sek"]), row["title"]))
    return {day: filter_outliers(prices) for day, prices in by_day.items()}


def build_series(by_day):
    days, means, lows, highs = [], [], [], []
    for day in sorted(by_day):
        prices = by_day[day]
        if not prices:
            continue
        days.append(day)
        means.append(statistics.mean(prices))
        lows.append(min(prices))
        highs.append(max(prices))
    return days, means, lows, highs


def plot(days, means, lows, highs):
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.fill_between(days, lows, highs, alpha=0.18, color="#1f77b4", label="Min – Max range")
    ax.plot(days, means, color="#1f77b4", linewidth=2, marker="o", markersize=4, label="Daily mean")

    if days:
        ax.annotate(
            f"{means[-1]:.0f} SEK",
            xy=(days[-1], means[-1]),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color="#1f77b4",
        )

    ax.axvline(RACE_DAY, color="red", linewidth=1, linestyle="--", alpha=0.6, label=f"Race day ({RACE_DAY})")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))
    if days:
        ax.set_xlim(days[0] - timedelta(days=1), RACE_DAY + timedelta(days=2))
    fig.autofmt_xdate(rotation=45, ha="right")

    ax.set_title("Stockholm Marathon 2026 — second-hand start ticket prices (Säljes)", fontsize=13)
    ax.set_ylabel("Price (SEK)")
    ax.set_xlabel("Date")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(OUT_FILE, dpi=150)
    print(f"Chart saved to {OUT_FILE}")
    plt.show()


if __name__ == "__main__":
    if not DATA_FILE.exists():
        print("No data yet. Run scrape.py first.")
    else:
        plot(*build_series(load_by_day()))
