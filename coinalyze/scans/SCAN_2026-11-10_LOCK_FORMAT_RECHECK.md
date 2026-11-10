# SCAN + SAVE + LOCK FORMAT — COINALYZE OI/FUNDING
**User request:** "scan, save, lock format"
**Scan date:** 2026-11-10 WIB
**Status:** saved scan snapshot; existing USER-LOCKED visual and decision SOPs unchanged.

## VERIFIED DATA provenance
- GitHub `data/coinalyze/metadata.json` fetched UTC **2026-11-09T10:05:42.226852+00:00** = WIB **2026-11-09 17:05:42**. Coinalyze run 42598294533 was successful. No subsequent Coinalyze bridge run found among latest repository Actions at this scan.
- `data/coinalyze/RADAR_OI_FUNDING_CCI18_WMA6.csv` 120 rows, 95 CLOSED and 25 INSUFFICIENT_HISTORY.
- Data uses selected single perpetual contract for BTC/ETH/SOL/BNB, not globally aggregated OI across exchanges.
- `data/binance/{BTC,ETH,SOL,BNB}USDT_1D_source.csv`: latest CLOSED spot row 2026-11-09 00:00 UTC → closes **2026-11-10 07:00 WIB**; exclude RUNNING 2026-11-10 00:00 UTC.
- Latest OI/funding CLOSED **4D, 6D, 12D: 2026-11-09 07:00 WIB**; **18D: 2026-11-03 07:00 WIB**. Next closes 4D 13 Nov; 6D 15 Nov; 12D and 18D 21 Nov 2026, 07:00 WIB.
- Raw funding units are native to API, not assumed to be 8H percent. Metrics below are WMA6-on-CCI18 indicator units, NOT raw OI USD or funding %.

## 01 — NAVY INTERACTIVE GRAPH
**Render exactly as in existing MASTER LOCK** `coinalyze/MASTER_LOCK_VISUAL_6D_OI_FUNDING_2026-11-09.md`: #101b2b background, #142239 panel, BTC #fbbf24, ETH #38bdf8, SOL #34d399, BNB #d8b4fe. Six-day closed OI WMA6 four lines combined; dates, hover/click synced four asset cards, crosses, three angles, TOP/TENGAH/BOTTOM +200 +100 0 -100 -200, date chips 24 Jun /16 Sep /22 Sep / 09 Nov. Chart historical Jun 06 to Nov 09 2026 unchanged. This Markdown file archives data/format references; interactive widget is rendered in chat, not in Markdown file.
  
## 02 — 6D CLOSED ONE-VIEW OI / FUNDING
|Asset|OI CCI18|OI WMA prev→last|OI Δ|OI Δ²|OI θ|OI 3 θ samples|Funding CCI18|Funding WMA prev→last|Funding Δ|Funding Δ²|Funding θ|Funding 3 θ samples|
|---|---:|---|---:|---:|---:|---|---:|---|---:|---:|---:|---|
|BTC|74.69|104.32→95.61|-8.71|-10.06|-23.53°|-33.64°→+3.85°→-23.53°|-70.64|-11.69→-20.09|-8.40|-49.91|-22.78°|+66.14°→+64.28°→-22.78°|
|ETH|-38.42|4.12→-12.02|-16.14|-2.12|-38.90°|-27.78°→-35.03°→-38.90°|-245.15|53.66→-27.39|-81.05|-99.90|-76.14°|+45.73°→+43.30°→-76.14°|
|SOL|-1.13|55.24→36.02|-19.21|-7.95|-43.85°|-41.81°→-29.38°→-43.85°|-76.39|50.75→17.79|-32.96|-44.08|-58.75°|+43.03°→+29.07°→-58.75°|
|BNB|-102.45|74.65→19.61|-55.05|-37.43|-70.03°|-31.92°→-41.38°→-70.03°|-174.08|30.40→-28.89|-59.29|-58.27|-71.36°|+18.46°→-2.92°→-71.36°|

**CCI/WMA fresh CROSS DOWN on Nov9 CLOSED:** BTC OI 4D and 6D; BTC funding 6D; ETH OI 4D and funding 6D; SOL OI 4D and funding 6D; BNB funding 6D. Other "below WMA" conditions are *not* new crossing.

## 03 — 4D/12D/18D CONTEXT (OI WMA6 + Δ)
|Asset|4D|6D|12D|18D|
|---|---|---|---|---|
|BTC|99.79 / -12.22|95.61 / -8.71|70.35 / +3.61|55.65 / +30.87|
|ETH|-40.74 / -9.34|-12.02 / -16.14|23.65 / -16.81|0.13 / +6.30|
|SOL|-13.05 / -21.55|36.02 / -19.21|100.72 / -33.92|56.67 / +19.29|
|BNB|-52.61 / -67.04|19.61 / -55.05|68.10 / -49.22|19.38 / +12.28|

## 04 — INDEPENDENT DIRECTION/TIMING (as-of available confirmed data)
**PRIMARY DIRECTION: SHORT SOL/USDT** (bearish bias; confidence MEDIUM).
**TIMING STATUS: LATE / NO MARKET ENTRY RIGHT AT VERIFIED LOW.** Wait for independently verified failed rebound rather than chasing market down at prior 6D low.
- 4D OI WMA +8.49→-13.05 (Δ-21.55), fresh OI CCI/WMA CROSS DOWN. 6D OI +55.24→+36.02 (Δ-19.21). 12D OI +134.63→+100.72 (Δ-33.92). 6D funding +50.75→+17.79 (Δ-32.96), CCI -76.39 below WMA after fresh CROSS DOWN.
- Counterevidence: 18D OI +37.37→+56.67 (positive Δ+19.29), so higher-TF reversal/short squeeze risk remains.
- Latest Binance Spot **CLOSED 2026-11-10 07:00 WIB** SOL $86.74. 6D Nov9 CLOSED low **$85.02**. Proposed retest watch zone **$91–93** (hypothetical future, not observed fill). Thesis loses strength after sustained return above **$98.14** (Nov9 complete 6D high).
- Conditional objective $85.02 prior low and $80 only on later verified bearish continuation; not a promise of future price.
- BTC has positive 12D/18D OI slopes; ETH/BTC funding reversal pressure can produce squeeze; BNB OI declines steeply and may likewise snap back. Directional choice is relative, not certain.
- Never claim order was executed.

## 05 — NEXT MONTH CANDLE DATES
All closes 07 WIB:
- 13 November: 4D check early improvement/failure.
- 15 November: 6D decision refresh (12D/18D next on 21 November).
- 21 November: 6D + 12D + 18D major closed confluence.
- 27 November, 3 December, 9 December: 6D continuation/failed thesis; no invented future indicator numbers.
   
## LOCK VALIDATION
Three prior LOCK files preserved exactly without modification:
1. `coinalyze/MASTER_LOCK_VISUAL_6D_OI_FUNDING_2026-11-09.md`
2. `coinalyze/LOCK_FORCED_DIRECTIONAL_DECISION_2026-11-10.md` (autonomous decision every scan)
3. `coinalyze/MASTER_LOCK_TIMING_EARLY_LATE_KESIMPULAN_FORMAT_2026-11-10.md`
Cross references the early-vs-late timing research in `coinalyze/research/TIMING_STUDY_EARLY_VS_LATE_2026-11-10.md`.

**Do not reinterpret "scan" as an authorization to alter indicator settings, colors, assets, source, visual format, threshold, or trading rules. No empirical validation claimed from selective historical examples.**
