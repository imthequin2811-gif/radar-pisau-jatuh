# CRYPTO CASH | Two-Method Radar — CCI18 + WMA6

This is a **separate** module. It does not modify the existing BTC/ETH/SOL radar.

## Sources

- **A: TradingView** `CRYPTOCAP:TOTAL - CRYPTOCAP:TOTALES` (top-125 index coverage).
- **B: USD-pegged stablecoin circulating USD** (DefiLlama data via Aethereal daily historical CSV).
  Download: https://dataset.aethereal.top/files/stablecoin-market-cap-history.csv
- **Historical B series:** 2017 onward, including all of 2022–2026. Historical data is used to warm up the indicators.

**A is not invented from B.** To enable A: export both **1D** charts from TradingView as CSV, with column `time` (or `date`) and `close` (capitalization in USD). Upload them to:

- `data/crypto_cash/TV_TOTAL_1D.csv` (CRYPTOCAP:TOTAL)
- `data/crypto_cash/TV_TOTALES_1D.csv` (CRYPTOCAP:TOTALES)

Both must exist. If neither exists, B will run alone and A stays **MISSING**.

## Indicator rules

- 6D and 12D custom bars restart on **1 January 00:00 UTC** each year.
- Latest source date in a bar is its CLOSE. Bars with missing daily data are discarded.
- Only **fully closed** bars count as CLOSED indicators. Running bars are not used as trade signals.
- `CCI(18, Close)` uses rolling mean absolute deviation / (0.015 * MAD), then `WMA(6)` of the **CCI**.
- `flow_bn` is the change in nominal stablecoin capitalization in US$ billions **between closed candles**, not verified fiat bank withdrawals.
- `dwma` = current WMA6 - previous WMA6.
- `d2wma` = current dwma - prior dwma.
- `angle` = degrees(atan(dwma / 20)); this is a normalized indicator slope, not a geometric chart angle.
- `cross` = CCI18 crossing its WMA6.
- Graph window: **last 4 months**, historical CSV covers all eligible CLOSED candles.

## Daily automated update

GitHub Actions workflow: [Crypto Cash A/B CCI18 WMA6 Radar](../.github/workflows/crypto_cash_daily.yml)

Schedule: **02:30 UTC = 09:30 WIB daily** (GitHub scheduled jobs may run late).
Manual: Actions > Crypto Cash A/B CCI18 WMA6 Radar > Run workflow.

Outputs under `data/crypto_cash/`:
- `B_DAILY_HISTORY.csv` — complete daily B series
- `B_6D_HISTORY.csv`, `B_12D_HISTORY.csv` — full CLOSED calculation histories
- `B_6D_VISUAL.png`, `B_12D_VISUAL.png` — 4-month visual charts
- `A_6D_HISTORY.csv`, `A_12D_HISTORY.csv`, corresponding visuals — once TV exports exist
- `RADAR_SUMMARY.csv` — latest validated CLOSED 6D and 12D summary
- `STATUS.json` — live source availability; if A is missing, A never appears as a fabricated zero

## Run locally

```bash
python -m pip install pandas numpy matplotlib
python crypto_cash/build_crypto_cash.py
```

This module is exploratory and does not place trades. Changes in capitalization are not equivalent to verified flows from crypto into fiat banking.
