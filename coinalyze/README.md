# Coinalyze + GitHub — radar derivatives (isolated extension)

This folder extends the existing radar without changing any LOCKED price-indicator rules,
existing `build_radar.py`, or files under `data/radar`.

## Sources

- **Coinalyze official API** — futures and spot market catalogs, exchanges, current
  open interest, current/predicted funding, historical open interest, funding,
  predicted funding, long/short liquidations, long/short ratio and futures OHLCV.
  Source: https://api.coinalyze.net/v1/doc/
- **Existing GitHub CSV** — `data/binance/{BTC,ETH,SOL,BNB}USDT_1D_source.csv`.
  The CLOSED Binance **spot** price is joined by UTC date for side-by-side
  comparison only. Futures OI/funding and spot price are **different datasets**.
- All raw daily history is preserved *per exchange contract* in
  `data/coinalyze/history`, so one contract's values are never mislabeled
  as coin-wide aggregated open interest. A listing of each selected market is
  saved as `data/coinalyze/catalog/selected-markets.csv`.

## Indicators / integrity

- **CCI(18, Close)** of the daily metric series aggregated into custom
  **4D, 6D, 12D and 18D** candles, then **WMA(6) of that CCI**.
- Annual reset every **1 January at 00:00 UTC**.
- **CLOSED only**: every daily value must be present for a complete multi-day
  interval. No missing-day forward-fill. RUNNING never becomes CLOSED by
  extrapolation.
- Store WMA previous -> latest, delta, delta squared, angle, angle change,
  crossing-relevant value (CCI vs WMA), and arrows. Angle is
  `atan(delta_WMA / 20)` in degrees; reporting this formula is mandatory.
- Funding values remain in **native API units**, not falsely labeled % or
  rescaled to 8-hour intervals.
- Coinalyze historical daily "close" is a *daily metric close*, **not**
  daily mean funding and not spot price.
- The data in `data/coinalyze` is additive. Do not overwrite or modify the
  existing price-only LOCKED radar.
- Historical depth and market coverage vary: "INSUFFICIENT_HISTORY" is
  shown instead of fake CCI/WMA where there are too few candles.

## Activate GitHub workflow

1. Sign in to https://coinalyze.net/ and generate your free official API key
   via https://coinalyze.net/api/
2. In this GitHub repository open **Settings > Secrets and variables >
   Actions > New repository secret**.
3. Secret name **`COINALYZE_API_KEY`**, value = your Coinalyze API key.
   **Do not** commit, paste into chat, or publish the key.
4. Merge the separate review PR when you're ready. Scheduled runs on
   default branch are then automatic at 03:17 UTC (= 10:17 WIB).
   The collector is skipped if the key is not configured. Run
   **Actions > Coinalyze OI/Funding Bridge > Run workflow** to fetch manually.
5. Scan output:
   `data/coinalyze/RADAR_OI_FUNDING_CCI18_WMA6.csv`.
   Raw historical CSV, current snapshots and catalog files sit in sibling
   subdirectories. Each file includes its source and/or contract symbol.

Local test (no key): `python coinalyze/collect.py --self-test`

Local collection:

```bash
export COINALYZE_API_KEY="...private..."  # prefer GitHub secret
python coinalyze/collect.py --assets BTC,ETH,SOL,BNB,TAO,FET,HOT,RSR,JCT,AIOT --per-asset 1
```

For every perpetual listed by Coinalyze:
`python coinalyze/collect.py --all-markets --per-asset 0`

**Important quota note:** Coinalyze permits 40 symbol-calls/minute, and
requests containing N contracts consume N calls. A full-market historical
backfill might require thousands of calls and several hours. Run separately
from the normal scheduled watchlist scan; a standard GitHub-hosted job may
timeout. The workflow intentionally defaults to the 10-coin shortlist, not
the unbounded all-markets mode. The collector retries 429s.

**Limits:** This extension cannot fetch protected historical data before
a valid API key is configured. It does not claim that source coverage,
exchange aggregation or backtests are verified without an actual API run.
