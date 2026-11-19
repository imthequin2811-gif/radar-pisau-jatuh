"""Refresh daily Binance Spot candles for the radar."""
import csv
import json
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from build_radar import SOURCE_DIR, SYMBOLS

HOSTS = ("data-api.binance.vision", "api.binance.com")
DAY_MS = 86_400_000
COLUMNS = (
    "open_time_utc", "open", "high", "low", "close", "volume",
    "close_time_utc", "status",
)


def utc(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate(candles, now_ms):
    if not isinstance(candles, list) or len(candles) < 600:
        raise ValueError("Fewer than 600 daily candles")

    previous_open = None
    for candle in candles:
        start, opening, high, low, close, volume, end = candle[:7]
        if (
            type(start) is not int or type(end) is not int
            or start < 0 or start > now_ms
            or start % DAY_MS or end != start + DAY_MS - 1
            or (previous_open is not None and start != previous_open + DAY_MS)
        ):
            raise ValueError("Invalid or noncontiguous daily candle timestamps")

        opening, high, low, close, volume = map(Decimal, (opening, high, low, close, volume))
        if (
            not all(value.is_finite() for value in (opening, high, low, close, volume))
            or not 0 < low <= min(opening, close) <= max(opening, close) <= high
            or volume < 0
        ):
            raise ValueError("Invalid daily OHLCV")
        previous_open = start

    if previous_open < (now_ms // DAY_MS - 1) * DAY_MS:
        raise ValueError("Latest completed UTC day is missing")


def fetch_candles(symbol):
    query = urlencode({"symbol": symbol, "interval": "1d", "limit": 1000})
    errors = []
    for host in HOSTS:
        try:
            with urlopen(f"https://{host}/api/v3/klines?{query}", timeout=40) as response:
                candles = json.load(response)
            now_ms = time.time_ns() // 1_000_000
            validate(candles, now_ms)
        except (URLError, OSError, ValueError, TypeError, InvalidOperation) as exc:
            errors.append(f"{host}: {exc}")
            print(f"{symbol}: {errors[-1]}", flush=True)
            continue
        print(f"{symbol}: {host} returned {len(candles)} validated candles", flush=True)
        return candles, now_ms
    raise RuntimeError(f"No usable Binance Spot feed for {symbol}: {' | '.join(errors)}")


def main():
    # Fetch and validate every symbol before replacing any tracked input.
    snapshots = {symbol: fetch_candles(symbol) for symbol in SYMBOLS}
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    for symbol, (candles, now_ms) in snapshots.items():
        path = SOURCE_DIR / f"{symbol}_1D_source.csv"
        temporary = path.with_suffix(".csv.tmp")
        with temporary.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(COLUMNS)
            for start, opening, high, low, close, volume, end, *_ in candles:
                writer.writerow([
                    utc(start), opening, high, low, close, volume,
                    utc(end + 1), "CLOSED" if end < now_ms else "RUNNING",
                ])
        temporary.replace(path)


if __name__ == "__main__":
    main()
