# SCAN COINALYZE — 10 NOVEMBER 2026
**Status:** User-LOCKED dashboard preserved. Separate additive scan report; no change to scanner/workflow.

## Sources and timestamp
- Original Coinalyze data snapshot: **2026-11-09 10:05:42 UTC = 2026-11-09 17:05:42 WIB** from `data/coinalyze/metadata.json`; includes **10 selected futures contracts** (not exchange-wide aggregate).
- Binance Spot price: `data/binance/{BTC,ETH,SOL,BNB}USDT_1D_source.csv`; latest **CLOSED** opening **2026-11-09 00:00 UTC**, closed 2026-11-10 00:00 UTC (07:00 WIB). Exclude RUNNING opening 2026-11-10 00:00 UTC from signals.
- Timeframes custom anchor Jan 1 00:00 UTC; 4D/6D/12D CLOSED: Nov 9 07:00 WIB, 18D CLOSED Nov 3 07:00 WIB.
- Next 4D CLOSED Nov 13, 6D CLOSED Nov 15, 12D/18D CLOSED Nov 21; all 07:00 WIB.
- CCI(18, close of OI or funding); WMA(6) on CCI, not price; angle=degrees(atan(ΔWMA/20)).
- Visual unchanged per `coinalyze/MASTER_LOCK_VISUAL_6D_OI_FUNDING_2026-11-09.md`.
- Decision autonomously produced per `coinalyze/LOCK_FORCED_DIRECTIONAL_DECISION_2026-11-10.md`.

## OI 6D CLOSED 9 Nov 2026

| Asset | CCI18 | Previous WMA6 | Latest WMA6 | ΔWMA | Δ²WMA | θ previous 3 candles | CCI/WMA crossing on latest CLOSED |
|---|---:|---:|---:|---:|---:|---|---|
| BTC | 74.69 | 104.32 | 95.61 | -8.71 | -10.06 | -33.64° → +3.85° → -23.53° | DOWN |
| ETH | -38.42 | 4.12 | -12.02 | -16.14 | -2.12 | -27.78° → -35.03° → -38.90° | No fresh cross |
| SOL | -1.13 | 55.24 | 36.02 | -19.21 | -7.95 | -41.81° → -29.38° → -43.85° | No fresh cross |
| BNB | -102.45 | 74.65 | 19.61 | -55.05 | -37.43 | -31.92° → -41.38° → -70.03° | No fresh cross |

## Funding 6D CLOSED 9 Nov 2026

| Asset | CCI18 | Previous WMA6 | Latest WMA6 | ΔWMA | Δ²WMA | θ previous 3 candles | CCI/WMA crossing on latest CLOSED |
|---|---:|---:|---:|---:|---:|---|---|
| BTC | -70.64 | -11.69 | -20.09 | -8.40 | -49.91 | +66.14° → +64.28° → -22.78° | DOWN |
| ETH | -245.15 | 53.66 | -27.39 | -81.05 | -99.90 | +45.73° → +43.30° → -76.14° | DOWN |
| SOL | -76.39 | 50.75 | 17.79 | -32.96 | -44.08 | +43.03° → +29.07° → -58.75° | DOWN |
| BNB | -174.08 | 30.40 | -28.89 | -59.29 | -58.27 | +18.46° → -2.92° → -71.36° | DOWN |

The funding-unit is native to Coinalyze and should never be silently interpreted as 8-hour %; the values above are indicator CCI/WMA scale, not actual raw funding.

## OI multi-timeframe

| Asset | OI 4D WMA6 / Δ | OI 6D WMA6 / Δ | OI 12D WMA6 / Δ | OI 18D WMA6 / Δ |
|---|---|---|---|---|
| BTC | 99.79 / -12.22 | 95.61 / -8.71 | 70.35 / +3.61 | 55.65 / +30.87 |
| ETH | -40.74 / -9.34 | -12.02 / -16.14 | 23.65 / -16.81 | 0.13 / +6.30 |
| SOL | -13.05 / -21.55 | 36.02 / -19.21 | 100.72 / -33.92 | 56.67 / +19.29 |
| BNB | -52.61 / -67.04 | 19.61 / -55.05 | 68.10 / -49.22 | 19.38 / +12.28 |

OI 4D CCI/WMA at Nov 9: BTC DOWN, ETH DOWN, SOL DOWN, BNB not a new crossing (CCI already below WMA). Funding 4D CCI/WMA: ETH DOWN, SOL DOWN; BTC and BNB below WMA but no fresh cross.

## Latest Binance Spot CLOSED price (Nov 10 07 WIB)

| Asset | Close USDT | Latest complete 6D (Nov 9) high | Latest complete 6D low | 12D OI implication |
|---|---:|---:|---:|---|
| BTC | 75,368.41 | 81,196.01 | 73,510.00 | 12D OI +3.61, conflict with 6D decline |
| ETH | 2,135.24 | 2,450.00 | 2,060.00 | OI 12D declining; funding very negative |
| SOL | 86.74 | 98.14 | 85.02 | OI 12D +100.72 but declining -33.92 |
| BNB | 691.44 | 723.42 | 678.37 | OI 4D and 6D strongly negative change, high squeeze risk |

Spot and Coinalyze perpetual contract are different sources. No claim of live or executable quote.

## PROACTIVE DECISION — PRIMARY PICK

**Direction: SHORT SOL/USDT (directional bias).**
**Timing: NOT AN IMMEDIATE MARKET SHORT at spot close $86.74.** Reason: already trading near the verified 6D low $85.02; avoid poor asymmetry, crowded continuation or short-covering squeeze. The most defensible *hypothetical* entry is a **failed relief-rally/retest in $91–93 area**, only if price stalls below $95.61 with 4D OI and funding remaining weak. Alternatively, re-evaluate only after a new 4D CLOSED breakdown through $85.02; do not equate an intrabar wick with confirmation. These are conditional future scenarios, not executed orders.

- Potential structural invalidation for the rebound-entry scenario: acceptance/recovery and price holding above **$98.14**, the high on the latest complete 6D 9 Nov (Binance Spot).
- Reference price source: spot CLOSED Nov 10 07 WIB $86.74; the $91–93 band is a **proposed future retest area**, not a current price or observed fill.
- Preliminary objective for a confirmed short: previous low $85.02, then illustrative extension $80 **only if subsequently confirmed**, not a guaranteed target.
- Confidence: **MEDIUM for bearish directional bias, LOW for immediate entry timing**.
- Confluence pro-SHORT: (1) OI 4D/6D/12D down; 4D OI fresh CROSS DOWN; (2) funding 6D abrupt DOWN crossing; (3) SOL Binance Spot 6D CLOSED slid from $91.98 on Nov 3 to $86.54 Nov 9.
- Contradictions/risks: OI 18D remains rising; price now at/near prior 6D lows; funding pressure may cause position cleanup and a strong short-covering rebound; futures metrics represent one market, not aggregated exchange data.
- BTC is less suitable short due to stronger OI 12D/18D; ETH and BNB already show extreme negative CCI funding/OI, increasing snapback/squeeze risk.
- Do not imply order execution or profitable forecast. The decision must not use future data to claim certainty.

## Scenario timetable (all WIB)
- **13 Nov 2026 07:00**: 4D CLOSED — check whether OI CCI remains under WMA6, slopes Δ/Δ², price failure of retest/close.
- **15 Nov 2026 07:00**: 6D CLOSED — key confirmation. If OI/funding WMA slopes turn upward, downgrade SHORT thesis rather than averaging blindly.
- **21 Nov 2026 07:00**: 12D and 18D CLOSED — evaluate upper-timeframe conflict and zone rotation.
- **27 Nov / 3 Dec / 9 Dec**: further 6D CLOSe milestones, conditional scenarios only, not numeric forecasts.

## Historical crossing examples
- 22 Jun 2026 4D CLOSED BTC OI CROSS UP in negative zone (CCI -110.97, WMA -134.80).
- 18 Sep 2026 4D CLOSED BTC OI CROSS UP (CCI 68.67, WMA 55.78); ETH OI CROSS DOWN. On 6D, closest later CLOSED Sep 22.
- Historical crossing dates require exact original TF, not retrospective relabeling.

## Archive integrity
This report preserves LOCKED navy 6D four-asset interactive chart and associated fields. It is a written snapshot of externally verified data, not the interactive dashboard source file. No change to `coinalyze/collect.py`, `.github/workflows/coinalyze_bridge.yml`, or previous master lock.
