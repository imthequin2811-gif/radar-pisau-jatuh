#!/usr/bin/env python3
"""Optional Coinalyze -> GitHub radar bridge. Does NOT modify existing LOCKED radar."""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

UTC = timezone.utc
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "coinalyze"
API = "https://api.coinalyze.net/v1"
HIST = (
    "open-interest-history",
    "funding-rate-history",
    "predicted-funding-rate-history",
    "liquidation-history",
    "long-short-ratio-history",
    "ohlcv-history",
)
SIMPLE = ("open-interest", "funding-rate", "predicted-funding-rate")
TIMEFRAMES = (4, 6, 12, 18)
DEFAULT_ASSETS = "BTC,ETH,SOL,BNB,TAO,FET,HOT,RSR,JCT,AIOT"


def dump_json(path: Path, content) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dump_csv(path: Path, data: list[dict]) -> None:
    if not data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = list(dict.fromkeys(k for item in data for k in item))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=cols)
        writer.writeheader()
        writer.writerows(data)


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", s)


class Coinalyze:
    """Stay below Coinalyze's 40 symbol-calls/minute limit."""

    def __init__(self, key: str):
        if not key:
            raise ValueError("COINALYZE_API_KEY missing: add as GitHub Actions secret")
        self.key = key
        self.calls = deque()

    def throttle(self, cost: int) -> None:
        while True:
            now = time.monotonic()
            while self.calls and now - self.calls[0] > 61:
                self.calls.popleft()
            if len(self.calls) + cost <= 35:
                self.calls.extend([now] * cost)
                return
            time.sleep(max(1.0, 61 - (now - self.calls[0])))

    def get(self, endpoint: str, params: dict | None = None, cost: int = 1):
        self.throttle(cost)
        url = API + "/" + endpoint
        if params:
            url += "?" + urlencode(params)
        req = Request(url, headers={"api_key": self.key, "User-Agent": "radar-coinalyze-bridge/1.0"})
        for attempt in range(5):
            try:
                with urlopen(req, timeout=45) as response:
                    return json.load(response)
            except HTTPError as exc:
                if exc.code == 401:
                    raise RuntimeError("Coinalyze API key invalid or unauthorized") from exc
                if exc.code == 429 and attempt < 4:
                    time.sleep(max(float(exc.headers.get("Retry-After", "60")), 1))
                    continue
                if exc.code >= 500 and attempt < 4:
                    time.sleep(min(60, 2 ** attempt + 2))
                    continue
                raise
            except (URLError, TimeoutError):
                if attempt == 4:
                    raise
                time.sleep(min(30, 2 ** attempt + 1))
        raise RuntimeError("API request retries exhausted")


def batches(items: list[str], size: int = 10):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def current_snapshots(client: Coinalyze, markets: list[dict], now: str):
    syms = [m["symbol"] for m in markets]
    for endpoint in SIMPLE:
        rows = []
        for part in batches(syms):
            try:
                result = client.get(endpoint, {"symbols": ",".join(part),
                                              **({"convert_to_usd": "true"} if endpoint == "open-interest" else {})},
                                    cost=len(part))
                for item in result:
                    item["fetched_utc"] = now
                    item["source"] = "Coinalyze"
                    item["unit"] = "USD" if endpoint == "open-interest" else "API native rate"
                rows += result
            except HTTPError as exc:
                print("WARNING current", endpoint, part, exc, file=sys.stderr)
        dump_csv(OUT / "current" / (endpoint + ".csv"), rows)


def get_history(client: Coinalyze, endpoint: str, sym: str, from_ts: int, to_ts: int):
    params = {"symbols": sym, "interval": "daily", "from": from_ts, "to": to_ts}
    if endpoint in ("open-interest-history", "liquidation-history"):
        params["convert_to_usd"] = "true"
    result = client.get(endpoint, params)
    return (result[0].get("history", []) if result else [])


def read_binance_spot(base: str):
    """CLOSED-only spot closes from the existing GitHub radar dataset, when present."""
    path = ROOT / "data" / "binance" / f"{base}USDT_1D_source.csv"
    if not path.exists():
        return {}
    closes = {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row.get("status", "").upper() != "CLOSED":
                continue
            stamp = datetime.fromisoformat(row["open_time_utc"].replace("Z", "+00:00"))
            closes[stamp.date()] = float(row["close"])
    return closes


def annual_buckets(daily: list[dict], tf: int, now: datetime):
    """Close-only, calendar-year Jan 1 UTC reset; never label partial buckets CLOSED."""
    daymap = {datetime.fromtimestamp(int(x["t"]), UTC).date(): float(x["c"])
              for x in daily if "c" in x and x["c"] is not None}
    groups = defaultdict(list)
    for date_, value in daymap.items():
        anchor = datetime(date_.year, 1, 1, tzinfo=UTC).date()
        idx = (date_ - anchor).days // tf
        groups[(date_.year, idx)].append((date_, value))
    bars = []
    for (year, idx), group in sorted(groups.items()):
        start = datetime(year, 1, 1, tzinfo=UTC) + timedelta(days=idx * tf)
        end = min(start + timedelta(days=tf), datetime(year + 1, 1, 1, tzinfo=UTC))
        needed = [(start + timedelta(days=i)).date() for i in range((end - start).days)]
        # Historical gaps and the latest unclosed bar must not be silently filled.
        if end > now or any(d not in daymap for d in needed):
            continue
        bars.append({"start": start, "end": end, "close": daymap[needed[-1]]})
    return bars


def indicators(bars: list[dict], length: int = 18, wma_length: int = 6):
    result = []
    cci = []
    values = [b["close"] for b in bars]
    for idx, bar in enumerate(bars):
        v = None
        if idx >= length - 1:
            window = values[idx - length + 1:idx + 1]
            mean = sum(window) / length
            mad = sum(abs(z - mean) for z in window) / length
            v = (values[idx] - mean) / (0.015 * mad) if mad > 0 else 0.0
        cci.append(v)
        recent = cci[-wma_length:]
        wma = (sum((j + 1) * x for j, x in enumerate(recent)) / (wma_length * (wma_length + 1) / 2)
               if len(recent) == wma_length and all(x is not None for x in recent) else None)
        prev = result[-1]["wma6"] if result else None
        prevprev = result[-2]["wma6"] if len(result) >= 2 else None
        delta = wma - prev if wma is not None and prev is not None else None
        delta2 = wma - 2 * prev + prevprev if wma is not None and prev is not None and prevprev is not None else None
        angle = math.degrees(math.atan(delta / 20)) if delta is not None else None
        result.append({**bar, "cci18": v, "wma6": wma, "delta": delta,
                       "delta2": delta2, "angle_deg": angle,
                       "status": "CLOSED"})
    return result


def market_history(client: Coinalyze, m: dict, from_ts: int, to_ts: int, now: datetime, summary: list):
    sym = m["symbol"]
    base = str(m.get("base_asset", "UNKNOWN")).upper()
    spot = read_binance_spot(base)
    for endpoint in HIST:
        if endpoint == "long-short-ratio-history" and not m.get("has_long_short_ratio_data"):
            continue
        if endpoint == "ohlcv-history" and not m.get("has_ohlcv_data"):
            continue
        try:
            history = get_history(client, endpoint, sym, from_ts, to_ts)
        except (HTTPError, URLError, RuntimeError, TimeoutError) as exc:
            print(f"WARNING {sym} {endpoint}: {exc}", file=sys.stderr)
            continue
        # Preserve source values without inventing non-existent samples.
        records = [{"symbol": sym, "source": "Coinalyze", **item} for item in history]
        dump_csv(OUT / "history" / f"{slug(sym)}_{endpoint}_daily.csv", records)
        if endpoint not in ("open-interest-history", "funding-rate-history",
                            "predicted-funding-rate-history"):
            continue
        for tf in TIMEFRAMES:
            calculated = indicators(annual_buckets(history, tf, now))
            valid = [x for x in calculated if x["wma6"] is not None]
            if not valid:
                summary.append({"market": sym, "base_asset": base, "metric": endpoint,
                                "timeframe": f"{tf}D", "status": "INSUFFICIENT_HISTORY",
                                "source": "Coinalyze", "last_closed_utc": "",
                                "cci18": "", "wma6": ""})
                continue
            latest = valid[-1]
            prev = valid[-2] if len(valid) > 1 else None
            prev_angle = prev["angle_deg"] if prev else None
            angle_delta = latest["angle_deg"] - prev_angle if latest["angle_deg"] is not None and prev_angle is not None else None
            spot_date = (latest["end"] - timedelta(days=1)).date()
            prev_spot_date = (prev["end"] - timedelta(days=1)).date() if prev else None
            spot_now = spot.get(spot_date)
            spot_prev = spot.get(prev_spot_date) if prev_spot_date else None
            spot_change = ((spot_now / spot_prev - 1) * 100) if spot_now is not None and spot_prev else None
            summary.append({
                "market": sym, "base_asset": base, "metric": endpoint,
                "timeframe": f"{tf}D", "status": "CLOSED",
                "last_closed_utc": latest["end"].isoformat(),
                "last_closed_wib": latest["end"].astimezone(timezone(timedelta(hours=7))).isoformat(),
                "value_close": latest["close"], "cci18": latest["cci18"],
                "prev_wma6": prev["wma6"] if prev else "",
                "wma6": latest["wma6"], "delta": latest["delta"],
                "delta2": latest["delta2"], "angle_deg": latest["angle_deg"],
                "prev_angle_deg": prev_angle, "angle_change_deg": angle_delta,
                "arrow": ("↓↓" if latest["delta"] < 0 and latest["delta2"] <= 0 else
                          "↓↗" if latest["delta"] < 0 else
                          "↑↘" if latest["delta"] >= 0 and latest["delta2"] < 0 else "↑↑")
                         if latest["delta"] is not None and latest["delta2"] is not None else "",
                "source": "Coinalyze",
                "spot_source": "GitHub data/binance CLOSED",
                "spot_closed_date": spot_date.isoformat() if spot_now is not None else "",
                "spot_price_close": spot_now if spot_now is not None else "",
                "spot_change_vs_prev_tf_pct": spot_change if spot_change is not None else "",
                "unit": "USD" if endpoint == "open-interest-history" else "Coinalyze API native",
            })


def select_markets(markets: list[dict], assets: set[str], all_markets: bool, per_asset: int):
    eligible = [m for m in markets if m.get("is_perpetual") and m.get("symbol")]
    if not all_markets:
        eligible = [m for m in eligible if str(m.get("base_asset", "")).upper() in assets]
    # Prefer USDT-margined contracts; preserve venue identity, never sum unlike units.
    eligible.sort(key=lambda m: (
        str(m.get("base_asset", "")),
        str(m.get("quote_asset", "")).upper() != "USDT",
        str(m.get("margined", "")).upper() != "STABLE",
        str(m.get("exchange", "")),
        str(m.get("symbol", ""))))
    if all_markets or per_asset == 0:
        return eligible
    count = defaultdict(int)
    selected = []
    for m in eligible:
        base = str(m.get("base_asset", "")).upper()
        if count[base] < per_asset:
            selected.append(m)
            count[base] += 1
    return selected


def self_test():
    now = datetime(2026, 11, 9, 0, 0, tzinfo=UTC)
    daily = [{"t": int((datetime(2024, 1, 1, tzinfo=UTC) + timedelta(days=j)).timestamp()),
              "c": float(j + 20 + 10 * math.sin(j / 10))} for j in range(650)]
    series = indicators(annual_buckets(daily, 6, now))
    assert len(series) >= 100 and any(x["wma6"] is not None for x in series)
    assert all(x["status"] == "CLOSED" for x in series)
    assert series[0]["start"] == datetime(2024, 1, 1, tzinfo=UTC)
    print("SELF-TEST PASS: annual 6D CLOSED; CCI18 and WMA6 available")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", default=DEFAULT_ASSETS, help="CSV of base tickers")
    parser.add_argument("--all-markets", action="store_true",
                        help="Every perpetual; quota-heavy, runs can take hours")
    parser.add_argument("--per-asset", type=int, default=1,
                        help="Selected contracts per asset; 0 for all exchanges")
    parser.add_argument("--lookback-days", type=int, default=1460)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    now = datetime.now(UTC)
    client = Coinalyze(os.getenv("COINALYZE_API_KEY", ""))
    exchanges = client.get("exchanges")
    markets = client.get("future-markets")
    spots = client.get("spot-markets")
    dump_json(OUT / "catalog" / "exchanges.json", exchanges)
    dump_json(OUT / "catalog" / "future-markets.json", markets)
    dump_json(OUT / "catalog" / "spot-markets.json", spots)
    assets = {x.strip().upper() for x in args.assets.split(",") if x.strip()}
    selected = select_markets(markets, assets, args.all_markets, args.per_asset)
    if not selected:
        raise RuntimeError(f"No eligible perpetual markets for assets={sorted(assets)}")
    dump_csv(OUT / "catalog" / "selected-markets.csv", selected)
    current_snapshots(client, selected, now.isoformat())
    end = int(now.timestamp())
    start = int((now - timedelta(days=args.lookback_days)).timestamp())
    summary = []
    for i, m in enumerate(selected, 1):
        print(f"[{i}/{len(selected)}] {m['symbol']}", flush=True)
        market_history(client, m, start, end, now, summary)
    dump_csv(OUT / "RADAR_OI_FUNDING_CCI18_WMA6.csv", summary)
    dump_json(OUT / "metadata.json", {
        "fetched_utc": now.isoformat(), "source": API, "daily_history": True,
        "closed_only": True, "timeframes": TIMEFRAMES,
        "cci_length": 18, "cci_source": "daily close of the metric",
        "wma_length": 6, "wma_source": "CCI18",
        "angle": "degrees(atan(delta_WMA6 / 20))",
        "aggregation": "Jan 1 00:00 UTC annual reset, continuous complete days only",
        "selected_markets": len(selected), "row_count": len(summary),
        "funding_unit": "Coinalyze API native, do not assume % or 8H",
        "price_comparison": "Use data/binance/*_1D_source.csv independently; never mix spot and futures",
    })
    print(f"Saved {len(summary)} analytical rows across {len(selected)} contracts")


if __name__ == "__main__":
    main()
