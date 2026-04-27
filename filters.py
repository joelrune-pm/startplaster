import re
import statistics

# Matches patterns like: "2 startplatser", "2st platser", "2x startplats",
# "säljer 2 platser", "2 biljetter", "2 tickets"
_MULTI_RE = re.compile(
    r"\b([2-9])\s*(?:st\.?|stycken|x)?\s*"
    r"(?:startplatser?|platser?|biljetter?|tickets?)\b"
    r"|"
    r"\b([2-9])\s*x\s*startplats",
    re.IGNORECASE,
)


def ticket_count(title: str) -> int:
    m = _MULTI_RE.search(title)
    if m:
        return int(m.group(1) or m.group(2))
    return 1


def normalize(price: int, title: str) -> float:
    return price / ticket_count(title)


def filter_outliers(prices: list[float], threshold: float = 0.6) -> list[float]:
    if not prices:
        return prices
    med = statistics.median(prices)
    lo, hi = med * (1 - threshold), med * (1 + threshold)
    return [p for p in prices if lo <= p <= hi]
