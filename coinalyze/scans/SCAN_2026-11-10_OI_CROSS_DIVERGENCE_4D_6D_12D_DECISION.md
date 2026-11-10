# SCAN — OI CCI18/WMA6 4D 6D 12D CROSSING & DIVERGENSI
**Date prepared:** 10 November 2026 · Closed candle cut-off: 9 November 2026 07.00 WIB
**Source:** Binance spot only for price secondary context; PRIMARY indicators are on selected-contract **Coinalyze Open Interest** snapshots, fetched 10 Nov 2026 11.04 WIB.
**Lock reference:** `coinalyze/MASTER_LOCK_AREA_EKSTREM_CCI_GELombang_CROSSING_TAMBAHAN_2026-11-10.md`
**Interactive plot:** `coinalyze/visuals/MASTER_LOCK_OI_CCI18_WMA6_4D_6D_12D_CROSS_DIVERGENCE.html`

## Indicator contract
- Four assets BTC, ETH, SOL, BNB. Annual candle anchor Jan1 00:00 UTC; TF 4D/6D/12D; CLOSED only.
- Compute CCI18 on **close of OI series** then WMA6 on CCI18; not a price-based indicator. Crossing means CCI OI versus WMA6 OI only.
- Divergence means OI-vs-CCI(OI) confirmed pivot mismatch, not price-vs-price-CCI.
- Synthetic 30–60 day dashed branches are **illustrative mathematical scenarios**, not real OI projections, calibrated forecasts, confidence intervals, or future candles.
- For prices (entry/invalidations), use separate Binance spot candles; futures contract OI and spot prices are not interchangeable.

## 1. 4D CLOSED 9 Nov
|Asset|CCI18 on OI|WMA6 on OI|WMA6 prev→new|ΔWMA|Cross latest|
|---|---:|---:|---|---:|---|
|BTC|+58.45|+99.79|112.01→99.79|-12.22|CROSS DOWN|
|ETH|-75.01|-40.74|-31.40→-40.74|-9.34|CROSS DOWN|
|SOL|-67.54|-13.05|8.49→-13.05|-21.55|CROSS DOWN|
|BNB|-207.49|-52.61|14.44→-52.61|-67.04|No fresh cross; remains below WMA6|

## 2. 6D CLOSED 9 Nov
|Asset|CCI18 on OI|WMA6 on OI|WMA6 prev→new|ΔWMA|Last 6D CROSS DOWN|
|---|---:|---:|---|---:|---|
|BTC|+74.69|+95.61|104.32→95.61|-8.71|9 Nov|
|ETH|-38.42|-12.02|4.12→-12.02|-16.14|3 Nov|
|SOL|-1.13|+36.02|55.24→36.02|-19.21|4 Oct|
|BNB|-102.45|+19.61|74.65→19.61|-55.05|28 Oct|

## 3. 12D CLOSED 9 Nov
|Asset|CCI18 on OI|WMA6 on OI|WMA6 prev→new|ΔWMA|
|---|---:|---:|---|---:|
|BTC|+72.88|+70.35|66.74→70.35|+3.61|
|ETH|-9.74|+23.65|40.46→23.65|-16.81|
|SOL|+41.18|+100.72|134.63→100.72|-33.92|
|BNB|-56.92|+68.10|117.32→68.10|-49.22|

## 4. Divergence evidence — only OI versus CCI(OI)
- **SOL 6D bearish:** 29 Aug OI 336.46M USD with CCI +293.50 → 28 Sep OI 384.77M with CCI +190.26. Both OI price-series pivot highs confirmed.
- **SOL 12D bearish:** 29 Aug OI 336.46M / CCI +267.94 → 22 Sep OI 371.33M / CCI +244.70. Confirmed local OI pivot highs.
- **BTC 6D bearish:** 22 Sep OI 2,552.92M / CCI +218.47 → 3 Nov OI 2,611.35M / CCI +110.46. Confirmed OI pivot highs, but 12D WMA still rising.
- **ETH 4D bearish:** 22 Sep OI 1,710.42M / CCI +187.03 → 8 Oct OI 1,720.10M / CCI +146.36. Confirmed local OI pivot highs.
- These are **historical early-warning setups** from weeks earlier, not a claim of a new fresh divergence on 9 Nov. Confirmed OI divergence does NOT prove directional price move; OI can decrease via long and short deleveraging.

## 5. Autonomous directional pick and timing
**Selected single directional bias: SHORT SOL/USDT; confidence medium as combined historical OI + spot context, lower if looking at OI alone.**

Rationale:
1. SOL 12D OI WMA6 from +134.63 to +100.72 (Δ -33.92); previously formed bearish OI/CCI divergence and WMA momentum declining from TOP.
2. SOL OI 6D WMA6 from 55.24 to 36.02 (Δ -19.21); CCI -1.13 beneath WMA (not a fresh Nov9 crossing).
3. SOL OI 4D CCI -67.54 vs WMA -13.05 (fresh CROSS DOWN 9 Nov); 6D funding WMA6 50.75→17.79 and CCI funding crosses down; spot price lower also supports, but is secondary validation.

**STATUS ENTRY: NOT MARKET SHORT AT VERIFIED SPOT $86.74 (10 Nov 07 WIB).** Under the user's zone-first master lock, SOL OI CCI 4D -67.54 is **not a TOP entry**; OI 12D WMA remains around +100.72 while CCI OI +41.18. Therefore the bearish *bias* does not automatically authorize a fresh SHORT.
**User-discussed $91–93 SHORT LIMIT** is a **conditional price-watch/retest zone**, not proof a new 4D OI top/failure has formed; a resting SELL LIMIT could fill before confirmation. If an order is already placed, only the user can manage it; this document neither creates nor cancels it.
- Before considering hypothetical entry: check newly CLOSED 4D OI near TOP/failed rebound + weakening CCI relative to WMA6, 6D still under pressure, and price failed recovery rather than strong breakout.
- Previous conditional resistance invalidation reference: spot above $98.14 (6D high from previous scan), but requires refresh; no executable SL created.
- Risks: 18D SOL OI WMA still rising (+37.37→+56.67, Δ+19.29), short squeeze; OI shrinking could mean existing positions closing, not fresh directional shorts; Coinalyze single contract.
- If user asks what position one would choose on the evidence: **SHORT SOL directional setup; NO ENTRY now (zone/timing not qualified)**. Never rewrite "no entry" as no directional opinion.

## 6. Next CLOSED schedule
- **13 Nov 2026 07.00 WIB**: 4D OI reversal/false-cross and price location.
- **15 Nov 2026 07.00 WIB**: 6D OI/CCI/WMA crossing and acceleration reassessment.
- **21 Nov 2026 07.00 WIB**: 6D+12D+18D context.
- After that: 6D Nov27, Dec3, Dec9. 30–60 day scenario lines are intentionally conditional, not quantitative predictions.

## Preservation
The existing 6D navy four-asset OI WMA interactive chart, prior master lock format, 18D context, and prior research remain UNCHANGED. This scan and an additional detailed OI chart are supplementary.
