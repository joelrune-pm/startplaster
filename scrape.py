import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://www.startplatser.se/startplats-stockholm-marathon-kopes-saljes/"
DATA_FILE = Path(__file__).parent / "data" / "prices.csv"
COLUMNS = ["scraped_at", "listing_id", "date_posted", "type", "title", "price_sek"]


def parse_date(ddmmyy: str) -> str:
    return datetime.strptime(ddmmyy.strip(), "%d%m%y").strftime("%Y-%m-%d")


def extract_id(href: str) -> str:
    m = re.search(r"id=(\d+)", href or "")
    return m.group(1) if m else ""


def fetch_listings() -> list[dict]:
    resp = requests.get(URL, timeout=30)
    if resp.status_code != 200:
        print(f"ERROR: Got HTTP {resp.status_code} from {URL}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(resp.text, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows = []

    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue

        listing_type = tds[1].get_text(strip=True)
        if listing_type != "Säljes":
            continue

        date_text = tds[0].get_text(strip=True)
        # Cell may contain BankID icon text; grab the 6-digit date at the end
        date_match = re.search(r"(\d{6})$", date_text)
        if not date_match:
            continue

        link = tds[1].find("a") or tds[2].find("a")
        listing_id = extract_id(link.get("href", "") if link else "")
        title = tds[2].get_text(strip=True)
        price_text = tds[3].get_text(strip=True).replace(" ", "").replace("\xa0", "")

        try:
            price = int(price_text)
        except ValueError:
            continue

        rows.append({
            "scraped_at": scraped_at,
            "listing_id": listing_id,
            "date_posted": parse_date(date_match.group(1)),
            "type": listing_type,
            "title": title,
            "price_sek": price,
        })

    return rows


def append_to_csv(rows: list[dict]) -> None:
    DATA_FILE.parent.mkdir(exist_ok=True)
    write_header = not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0
    with DATA_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    listings = fetch_listings()
    append_to_csv(listings)
    print(f"Scraped {len(listings)} Saljes listings -> {DATA_FILE}")
