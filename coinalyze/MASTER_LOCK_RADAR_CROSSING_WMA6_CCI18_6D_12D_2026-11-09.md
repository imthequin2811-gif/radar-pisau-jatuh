# MASTER LOCK — RADAR OI & FUNDING: WMA6 ONLY + CCI18 × WMA6 CROSSING
**Approved:** 2026-11-09 (user said "lock, save" immediately after latest interactive crossing visualization).
**Status:** USER-LOCKED, immutable by assistant unless explicit user approval.
**Project:** imthequin2811-gif/radar-pisau-jatuh — Coinalyze derivatives.
**Usage trigger:** User says "scan" in this OI/Funding radar context. Repeat the exact user-approved layout, and REFRESH VERIFIED DATA; never replace a chart with prose-only tables.

## Two separate visual sections — in this order; don't combine/reorder
1. **SECTION 01 · WMA6 ONLY / FOUR ASSETS**
   - Metric selector: `Open Interest | Funding Rate`, preserving both metrics independently.
   - Two separate stacked charts: `WMA6 ONLY — 6D` followed by `WMA6 ONLY — 12D`.
   - Each chart overlays four WMA6-on-CCI18 curves of the selected metric: **BTC, ETH, SOL, BNB** (not the raw metric or price WMA).
   - Render CCI/WMA crossing event **circles directly on the WMA curve**: green = CROSS UP and red = CROSS DOWN on verified CLOSED candle date. Semi-subdued rings, never drown out line colors.
   - Legend, values and chronological date axis. Hover/click individual points must show exact candle end date, asset and WMA6 value; the most recent CLOSED point must be conspicuous. Keep 6D and 12D separate.
2. **SECTION 02 · CCI18 × WMA6 / SELECTED ASSET**
   - Asset selector `BTC | ETH | SOL | BNB`.
   - Two separate stacked charts: `CCI18 × WMA6 — 6D`, then `CCI18 × WMA6 — 12D`.
   - CCI18 shown as light-blue **dashed** line (`#95b9ee`); WMA6 as **solid thicker line** in selected asset's color. Never mislabel CCI18 as raw price/spot.
   - Mark and label **CROSS UP ↑ green / CROSS DOWN ↓ red** on each affected CLOSED candle; show recent cross DATE chips beneath the charts and hover/click readout of date/CCI18/WMA6/cross type.
   - 6D and 12D each have their own date axis, latest CLOSED badge, date tooltips, reference zones and dots.

## Visual exact defaults from last approved response
- Dark/navy background `#0e1929`; inner chart `#142239`, slim borders `#304663`; high-contrast legible text and chart.
- Asset colors: BTC `#ffcb45` (yellow), ETH `#42bafd` (cyan), SOL `#32e5b0` (green), BNB `#cba3ff` (lavender).
- Use horizontal reference guides at **-200, -100, 0, +100, +200**, and visually legible calendar-date labels.
- Four-asset WMA lines ~3px; detail WMA line ~3.7px; detail CCI dashed ~2px. Interactive points and LAST CLOSED points emphasized; CROSS red/green markers.
- Default metric `Open Interest`; default detail asset `BTC` when user has not selected another.
- Title is `Radar OI Funding — WMA6 & CCI Crossing`. Status CLOSED and latest UTC end converted to WIB (+07:00), not simply current date.
- In the last approved screenshot/chart, charts showed ~22 six-day samples from 2026-07-06 to 2026-11-09 and ~14 twelve-day samples from 2026-06-06 to 2026-11-09. Keep comparable readable historical span; do not silently replace with only two points.
- Data tables may accompany visuals, but **must never replace the actual charts**.

## Indicator and source rules (strict)
- Source: Coinalyze official API, stored in `data/coinalyze/history/{symbol}_{metric}_daily.csv`, selecting per-exchange futures contracts documented in `data/coinalyze/catalog/selected-markets.csv`. Distinguish one exchange from the coin-wide aggregate.
- For OI read `open-interest-history`; for Funding read `funding-rate-history`. Funding rates use API native unit for CSV, and MUST NOT silently be construed as % or an 8-hour rate.
- Custom **6D and 12D** candle boundaries reset **Jan 1 00:00 UTC** each year; source is the daily **Close** of OI/funding metric. The 4D/18D underlying radar settings are not deleted, merely not the two headline visual panels here.
- CCI(18, Close of the metric's CLOSED custom candles); WMA(6) on CCI18 (last CCI has highest weight 6).
- `ΔWMA = WMA(t)-WMA(t-1)`; `Δ²WMA = Δ(t)-Δ(t-1)`; `angle = degrees(atan(ΔWMA/20))`. Display three angle samples in a scan summary when user needs momentum.
- CROSS UP on custom CLOSED bar `t` iff `CCI(t-1) <= WMA(t-1)` and `CCI(t) > WMA(t)`; CROSS DOWN iff `CCI(t-1) >= WMA(t-1)` and `CCI(t) < WMA(t)`. Show the date of candle END in WIB; no intrabar cross claimed as CLOSED.
- ONLY FULLY CLOSED candles with all constituent daily records; mark insufficient data. If RUNNING or forecasts are ever added, visibly segregate, never imply verified.
- Do not invent lines, crosses or metric levels for assets not backfilled.
- Historical example from 2026-11-09 00:00 UTC CLOSED: BTC, ETH, SOL, BNB all show 6D and 12D **funding CCI18 below WMA6 CROSS DOWN** on 2026-11-09. Treat this as an observation on old snapshots, not a perpetual assertion/price trading recommendation.

## Supplemental watchlist, do not fabricate
- `PUMP` = pump.fun, and `PENGU` = Pudgy Penguins. Both verifiably have Coinalyze derivative OI and funding pages; keep on watchlist; only add WMA6/CCI18 history after actual complete backfill and explicit approval to expand six-asset combined chart.
- `QTC` = Quantus, separate project/spot watchlist unless actual derivatives source/history becomes verifiable; do not fabricate derivatives data.
- Primary combined chart assets remain BTC/ETH/SOL/BNB unchanged without permission.
- Historical source `data/coinalyze/metadata.json` controls last fetched time; verify latest before every scan. No pretending a stored snapshot is live.

## Relation to prior lock
- Preserve existing `coinalyze/MASTER_LOCK_VISUAL_6D_OI_FUNDING_2026-11-09.md` unchanged as a historical user-approved **single 6D OI chart** reference.
- This is a **new additional locked visualization/report contract**, directly matching the user's latest approval of separate WMA-only and CCI-vs-WMA 6D/12D charts. It does not modify the scanner, source CSVs, GitHub Action, the older lock, other radar projects, or scheduled tasks.
- If conflicting old and new formats are requested simultaneously, show them as separate independent panels, or ask the user before changing either.

**Non-negotiable:** Every `scan` of this extended radar includes both visual sections and verified crossing dates. Never answer with a table-only report in place of charts.
