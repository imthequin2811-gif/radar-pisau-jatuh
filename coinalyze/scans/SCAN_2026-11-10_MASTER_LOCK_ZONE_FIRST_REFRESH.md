# SCAN COINALYZE × BINANCE SPOT — 10 NOVEMBER 2026 — MASTER LOCK ZONE-FIRST
**User request:** "update master lock save, scan"
**Status:** VERIFIED historical CLOSED snapshot. Additive scan report, does not change locked indicators or navy interactive visual.
**Repo source:** https://github.com/imthequin2811-gif/radar-pisau-jatuh

## Data/time integrity
- Coinalyze `data/coinalyze/metadata.json`: **2026-11-10T04:04:29.253137+00:00** = **2026-11-10 11:04:29 WIB**; 10 selected contracts, 120 output rows, of which 95 CLOSED and 25 INSUFFICIENT_HISTORY. No later complete custom 6D candle: latest 6D CLOSED **2026-11-09 07:00 WIB**.
- Binance Spot `data/binance/*USDT_1D_source.csv`: latest daily CLOSED **2026-11-10 07:00 WIB**; row with `2026-11-10T00:00:00Z` is RUNNING, exclude from confirmation.
- Custom TF anchor Jan 1 00:00 UTC; latest **4D/6D/12D CLOSED 9 Nov 07 WIB**; **18D CLOSED 3 Nov 07 WIB**. Next close 4D 13 Nov, 6D 15 Nov, 12D/18D 21 Nov, all 07 WIB.
- Price-CCI18/WMA6 computed on **Binance Spot 4D/6D/12D/18D CLOSE**. Derivative OI/funding-CCI18/WMA6 computed separately on **Coinalyze per-contract data**. Never mix data or present as aggregated exchange-wide OI. Angle degrees = atan(ΔWMA/20).
- This scan follows updated `coinalyze/MASTER_LOCK_AREA_EKSTREM_CCI_GELombang_CROSSING_TAMBAHAN_2026-11-10.md`, also the prior MASTER LOCK visual and conclusion format.

## 01 — Price 4D: ENTRY ZONE FIRST
| Asset | Price CCI18 4D | WMA6 prev→latest | ΔWMA | Δ²WMA | θ last | Zona | Price CCI/WMA fresh cross at Nov9? |
|---|---:|---|---:|---:|---:|---|---|
| BTC | -145.07 | -11.09→-54.46 | -43.37 | -33.81 | -65.24° | BOTTOM | No (below already) |
| ETH | -197.82 | -77.66→-116.91 | -39.25 | -39.45 | -63.00° | BOTTOM | **DOWN**, following UP Nov5 |
| SOL | -160.42 | -63.56→-97.92 | -34.37 | -9.26 | -59.80° | BOTTOM | No |
| BNB | -141.31 | -28.80→-65.60 | -36.81 | -19.75 | -61.48° | BOTTOM | No |

All four are at **price CCI 4D BOTTOM**, but WMA6 4D angles are steeply negative. The user's trade zone currently suggests **watching for potential LONG reversal**, not opening fresh SHORT at depressed prices. No 4D WMA reversal yet. No confirmation from price higher-low on most recent two 4D bars.

## 02 — Price 6D CLOSED
| Asset | Price WMA6 6D prev→latest | Δ | Δ² | three angles (older→last) | Price CCI18 latest | Fresh CROSS |
|---|---|---:|---:|---|---:|---|
| BTC |49.68→25.38|-24.30|-2.03| -39.18°→-48.08°→-50.54° | -21.17 | No |
| ETH |22.04→-6.18|-28.23|-5.35| -46.67°→-48.84°→-54.68° | -59.47 | No |
| SOL |28.16→-2.78|-30.94|-0.58| -50.00°→-56.62°→-57.12° | -58.67 | No |
| BNB |45.69→22.73|-22.96|-1.31| -33.44°→-47.26°→-48.94° | -20.64 | No |

**6D is still declining for all four.** SOL Δ² nearly flat but not positive and price 4D still bearish: this is NOT a confirmed LONG signal.

## 03 — OI + Funding Coinalyze 6D CLOSED (indicator units, not raw native USD/%)
|Asset|OI WMA6 prev→latest|OI Δ|OI Δ²|Funding WMA6 prev→latest|Funding Δ|Funding Δ²|
|---|---|---:|---:|---|---:|---:|
|BTC|104.32→95.61|-8.71|-10.06|-11.69→-20.09|-8.40|-49.91|
|ETH|4.12→-12.02|-16.14|-2.12|53.66→-27.39|-81.05|-99.90|
|SOL|55.24→36.02|-19.21|-7.95|50.75→17.79|-32.96|-44.08|
|BNB|74.65→19.61|-55.05|-37.43|30.40→-28.89|-59.29|-58.27|

**Fresh 6D cross:** BTC OI CCI/WMA CROSS DOWN; BTC/ETH/SOL/BNB funding CCI/WMA CROSS DOWN. ETH/SOL/BNB OI were already below WMA (do not claim new cross). OI and funding describe positioning dynamics, **not price direction by themselves**.

## 04 — Price 12D/18D and OI 12D context
|Asset|Price WMA 12D prev→last / Δ|Price WMA18D prev→last / Δ|OI WMA12D prev→last / Δ|
|---|---|---|---|
|BTC|101.60→74.60 / -27.00|25.93→32.82 / +6.89|66.74→70.35 / +3.61|
|ETH|101.26→66.08 / -35.17|17.88→20.03 / +2.15|40.46→23.65 / -16.81|
|SOL|128.78→82.34 / -46.44|27.12→26.82 / -0.30|134.63→100.72 / -33.92|
|BNB|144.57→106.85 / -37.72|16.11→23.92 / +7.81|117.32→68.10 / -49.22|

Price-CCI 18D **CROSS DOWN** at 3 Nov on all four assets while WMA18D slope still positive for BTC, ETH, BNB. Therefore cross itself leads slope changes and cannot be conflated.

## 05 — Price checks from latest Spot CLOSED (Nov10 07 WIB)
|Asset|Latest CLOSED price|Nov9 complete 6D low|Nov9 complete 6D high|
|---|---:|---:|---:|
|BTC|$75,368.41|$73,510.00|$81,196.01|
|ETH|$2,135.24|$2,060.00|$2,450.00|
|SOL|$86.74|$85.02|$98.14|
|BNB|$691.44|$678.37|$723.42|

Never equate stale price with executable real-time market quote.

## 06 — AUTONOMOUS DECISION & USER ENTRY CONSTRAINT
- **Directional bias:** BEARISH / **SHORT SOL** on continuation because spot price and Coinalyze OI/funding 6D/12D broadly weaken.
- **Entry judgment per USER-LOCKED AREA EXTREME:** **NO NEW SHORT** with price-CCI 4D SOL -160.42 (BOTTOM). **NO LONG either** while both 4D WMA & 6D WMA are declining and no fresh bullish turn/cross with supportive price structure. Thus the proper trading status is **BOTTOM WATCH / NO ENTRY**. This is a decisive timing rejection, not an ambiguous long/short call.
- Older **$91–93 SOL SHORT LIMIT plan**: historical conditional retest scenario, not automatic permission under this latest zone-first rule. The limit could fill before the failure of price rebound; its compatibility with strict zone-only trading must be checked when price arrives. If already placed, the user controls it; assistant has not placed or cancelled any order. Prior $98.14 structure high is a contextual invalidation idea, not executable automatic stop.
- **3 reasons bearish bias:** price WMA 4D/6D/12D down; OI 6D/12D down; funding 6D CROSS DOWN. **2 reasons not to short now:** price CCI 4D already BOTTOM; short covering/mean reversion risk near recent lows.
- **Potential early LONG criteria at BOTTOM** (not currently met): price CCI 4D forms a higher low / WMA Δ² turns positive or at least decreases in magnitude, price low stops declining, then 6D WMA slope starts stabilizing, funding and OI no longer contradict. Fresh crossing is a helpful BONUS, not an absolute prerequisite; risk of false cross remains (ETH price 4D cross UP Nov5 then DOWN Nov9).
- Confidence: **medium bearish directional bias**, **low confidence in any immediate entry**. No claim of order fill or guaranteed returns.

## 07 — NEXT CANDLE CHECKS
- **Nov13 07 WIB (4D):** inspect bottom HL/LL, price-CCI vs WMA6, WMA Δ² and spot low confirmation; differentiate EARLY / FALSE-CROSS.
- **Nov15 07 WIB (6D):** examine whether slope WMA6 price & OI stabilizes / funding improves. Only then reconsider early LONG.
- **Nov21 07 WIB (6D+12D+18D):** confirm larger wave regime.
- Further 6D closes **Nov27, Dec3, Dec9** (WIB 07). No invented future prices/indicator values.

## 08 — LOCKED VISUAL REFERENCE
Preserve exactly the established **navy four-asset 6D OI WMA6 interactive chart** with BTC yellow / ETH cyan / SOL green / BNB lavender, +200/+100/0/-100/-200 grid, crossing rings, hover date, four synced cards of prev→latest/Δ/Δ²/three-angle/CCI, date chips 24 Jun /16 Sep /22 Sep /09 Nov, and same panel order. Source and formulas unchanged.
