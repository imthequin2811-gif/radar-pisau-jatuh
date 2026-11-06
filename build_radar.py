#!/usr/bin/env python3
"""Build annual-anchored Binance Spot 4D/6D/12D/18D CCI radar from OHLCV CSV.

All calculations use UTC. Each calendar year starts a new 4D/6D/12D/18D
aggregation sequence at January 1, 00:00 UTC. The last bucket of a year may
be shorter. CCI(20) is calculated from the aggregated CLOSE price (not HLC3).
WMA(5) applies to CCI on 4D/6D; WMA(10) applies to CCI on 12D/18D.

Only fully covered candles with all source days closed are labeled CLOSED.
The current partial candle is labeled RUNNING and must not be treated as a
confirmed trade signal. All arrows are momentum descriptions, not orders.
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "data" / "binance"
OUTPUT_DIR = ROOT / "data" / "radar"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT")
TIMEFRAMES = (4, 6, 12, 18)
UTC = timezone.utc
WIB = timezone(timedelta(hours=7))


def parse_utc(value: str) -> datetime:
    timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("Source timestamp must contain an explicit UTC timezone")
    return timestamp.astimezone(UTC)


def utc_str(d: datetime) -> str:
    return d.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def wib_str(d: datetime) -> str:
    return d.astimezone(WIB).strftime("%Y-%m-%d %H:%M WIB")


def num(value: float | None, decimals: int = 5) -> str:
    return "" if value is None else f"{value:.{decimals}f}"


def read_source(symbol: str) -> list[dict]:
    path = SOURCE_DIR / f"{symbol}_1D_source.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing source: {path}")
    rows = []
    seen_dates = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for raw in csv.DictReader(handle):
            start = parse_utc(raw["open_time_utc"])
            if start.hour or start.minute or start.second:
                raise ValueError(f"{symbol}: unexpected 1D open time: {start}")
            if start.date() in seen_dates:
                raise ValueError(f"{symbol}: duplicate date: {start.date()}")
            seen_dates.add(start.date())
            status = raw["status"].upper().strip()
            if status not in ("CLOSED", "RUNNING"):
                raise ValueError(f"{symbol}: unknown candle status: {status}")
            open_price = float(raw["open"])
            high = float(raw["high"])
            low = float(raw["low"])
            close = float(raw["close"])
            volume = float(raw["volume"])
            if not (low <= min(open_price, close) <= max(open_price, close) <= high):
                raise ValueError(f"{symbol}: invalid OHLC for {start.date()}")
            rows.append(dict(start=start, open=open_price, high=high,
                             low=low, close=close, volume=volume, status=status))
    rows.sort(key=lambda row: row["start"])
    if len(rows) < 600:
        raise ValueError(f"{symbol}: insufficient daily history ({len(rows)})")
    return rows


def aggregate(daily: list[dict], days: int) -> list[dict]:
    groups = defaultdict(list)
    for row in daily:
        stamp = row["start"]
        anchor = datetime(stamp.year, 1, 1, tzinfo=UTC)
        index = (stamp - anchor).days // days
        groups[(stamp.year, index)].append(row)

    candles = []
    newest_source_day = daily[-1]["start"]
    for (year, index), group in sorted(groups.items()):
        start = datetime(year, 1, 1, tzinfo=UTC) + timedelta(days=index * days)
        end = min(start + timedelta(days=days), datetime(year + 1, 1, 1, tzinfo=UTC))
        group.sort(key=lambda item: item["start"])
        dates = {item["start"] for item in group}
        expected = (end - start).days
        completely_covered = (
            len(dates) == expected
            and all(start + timedelta(days=i) in dates for i in range(expected))
        )
        if completely_covered and all(item["status"] == "CLOSED" for item in group):
            status = "CLOSED"
        elif end > newest_source_day and group[-1]["start"] == newest_source_day:
            # Current/latest incomplete bucket. Previous completed days within it
            # can be combined with the latest RUNNING daily candle provisionally.
            if group[0]["start"] != start:
                continue
            status = "RUNNING"
        else:
            # Do not silently treat missing historic days as valid completed bars.
            continue
        candles.append(dict(start=start, end=end, open=group[0]["open"],
                            high=max(r["high"] for r in group),
                            low=min(r["low"] for r in group),
                            close=group[-1]["close"],
                            volume=sum(r["volume"] for r in group),
                            status=status, source_days=len(group)))
    if not candles or len(candles) < 30:
        raise ValueError(f"Not enough {days}D aggregates for CCI/WMA")
    # A RUNNING candle must be the last row only.
    if any(c["status"] == "RUNNING" for c in candles[:-1]):
        raise ValueError("Unclosed historical candle found")
    return candles


def calculate(candles: list[dict], wma_length: int) -> None:
    close_values = [x["close"] for x in candles]
    cci_values: list[float | None] = []
    for i in range(len(candles)):
        if i < 19:
            cci_values.append(None)
            continue
        window = close_values[i - 19:i + 1]
        avg = sum(window) / 20
        mean_dev = sum(abs(x - avg) for x in window) / 20
        cci_values.append((close_values[i] - avg) / (0.015 * mean_dev) if mean_dev else 0.0)
    weights_sum = wma_length * (wma_length + 1) / 2
    for i, candle in enumerate(candles):
        candle["cci20"] = cci_values[i]
        window = cci_values[i - wma_length + 1:i + 1] if i >= wma_length - 1 else []
        candle["wma"] = (
            sum((j + 1) * value for j, value in enumerate(window)) / weights_sum
            if len(window) == wma_length and all(v is not None for v in window)
            else None
        )
        prev = candles[i - 1]["wma"] if i else None
        prevprev = candles[i - 2]["wma"] if i >= 2 else None
        candle["delta"] = candle["wma"] - prev if prev is not None and candle["wma"] is not None else None
        candle["delta2"] = candle["wma"] - 2 * prev + prevprev if prevprev is not None and prev is not None and candle["wma"] is not None else None
        candle["angle"] = math.degrees(math.atan(candle["delta"] / 100)) if candle["delta"] is not None else None
        candle["angle_change"] = candle["angle"] - candles[i - 1]["angle"] if i and candles[i - 1]["angle"] is not None and candle["angle"] is not None else None
        candle["arrow"] = arrow(candle["delta"], candle["delta2"])


def arrow(delta: float | None, curvature: float | None) -> str:
    if delta is None or curvature is None:
        return ""
    if abs(delta) < 1e-10:
        return "→"
    if delta < 0:
        return "↓↗" if curvature > 0 else "↓↓"
    return "↑↘" if curvature < 0 else "↑↑"


def save_csv(path: Path, columns: list[str], data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def process(symbol: str, daily: list[dict], timeframe: int) -> dict:
    wma_length = 5 if timeframe in (4, 6) else 10
    bars = aggregate(daily, timeframe)
    calculate(bars, wma_length)
    series = []
    for c in bars:
        series.append(dict(symbol=symbol, timeframe=f"{timeframe}D", wma_length=wma_length,
                           open_utc=utc_str(c["start"]), close_utc=utc_str(c["end"]),
                           close_wib=wib_str(c["end"]), status=c["status"],
                           open=num(c["open"], 8), high=num(c["high"], 8),
                           low=num(c["low"], 8), close=num(c["close"], 8),
                           volume=num(c["volume"], 6), source_days=c["source_days"],
                           cci20_close=num(c["cci20"]), wma_cci=num(c["wma"]),
                           delta_wma=num(c["delta"]), delta2_wma=num(c["delta2"]),
                           angle_deg=num(c["angle"]), delta_angle_deg=num(c["angle_change"]),
                           arrow=c["arrow"]))
    save_csv(OUTPUT_DIR / f"{symbol}_{timeframe}D_radar.csv", list(series[0]), series)

    closed = [c for c in bars if c["status"] == "CLOSED" and c["wma"] is not None]
    if len(closed) < 3:
        raise ValueError(f"{symbol} {timeframe}D: insufficient CLOSED WMA history")
    latest = closed[-1]
    previous = closed[-2]
    running = bars[-1] if bars[-1]["status"] == "RUNNING" else None
    last_price = daily[-1]["close"]
    return dict(symbol=symbol, timeframe=f"{timeframe}D", wma_length=wma_length,
                last_closed_open_utc=utc_str(latest["start"]),
                last_closed_at_utc=utc_str(latest["end"]),
                last_closed_at_wib=wib_str(latest["end"]),
                last_closed_price=num(latest["close"], 8),
                previous_closed_wma=num(previous["wma"]),
                latest_closed_wma=num(latest["wma"]),
                delta_wma=num(latest["delta"]),
                delta2_wma=num(latest["delta2"]),
                previous_angle_deg=num(previous["angle"]),
                latest_angle_deg=num(latest["angle"]),
                delta_angle_deg=num(latest["angle_change"]),
                arrow_closed=latest["arrow"],
                running_status="RUNNING" if running else "NONE",
                running_open_utc=utc_str(running["start"]) if running else "",
                next_close_wib=wib_str(running["end"]) if running else wib_str(latest["end"] + timedelta(days=timeframe)),
                running_wma_provisional=num(running["wma"]) if running else "",
                running_angle_provisional_deg=num(running["angle"]) if running else "",
                last_1d_price=num(last_price, 8),
                last_1d_status=daily[-1]["status"],
                last_1d_open_utc=utc_str(daily[-1]["start"]),
                price_vs_closed_tf_pct=num((last_price / latest["close"] - 1) * 100, 4))


def main() -> None:
    summary = []
    for symbol in SYMBOLS:
        daily = read_source(symbol)
        for timeframe in TIMEFRAMES:
            item = process(symbol, daily, timeframe)
            summary.append(item)
            print(f"{symbol} {timeframe}D CLOSED {item['last_closed_at_utc']} {item['arrow_closed']}")
    save_csv(OUTPUT_DIR / "RADAR_SUMMARY.csv", list(summary[0]), summary)
    print(f"Saved {len(summary)} summary rows and 16 timeframe CSV files")


if __name__ == "__main__":
    main()
