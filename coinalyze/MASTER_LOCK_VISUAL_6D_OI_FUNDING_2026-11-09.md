# MASTER LOCK — COINALYZE OI/FUNDING 6D VISUAL

**Approved by user:** 2026-11-09, after the navy four-asset hover chart was shown.
**Status:** USER-LOCKED. Do not modify its visual composition, parameters, palette, data sources, calculation method, or panel order unless the user explicitly authorizes a change.
**Purpose:** Render the same exact interactive chart each time user says `scan`, `lock`, `save` or `scan format visual`. A scan means refresh verified data, never redesign a dashboard.

## Visual contract — MUST preserve

1. One wide navy chart on background **#101b2b**, chart panel **#142239**, thin borders **#344860**. Match user-provided VIX/TQQQ/SQQQ/NDTH example; no white-background line chart.
2. Heading **01 · WMA6 6D — FOUR ASSETS / OI**, badge `CLOSED <latest date> · 07.00 WIB`.
3. **Four overlaid WMA6 lines for Open Interest** in a single chart, in order and color: **BTC #fbbf24 (yellow), ETH #38bdf8 (cyan), SOL #34d399 (green), BNB #d8b4fe (lavender)**. Keep legend above chart. Lines solid, ~2.7px, and clear dot markers.
4. Y-axis reference horizontal grid at **+200, +100, 0, -100, -200**; labels **TOP ≥+100**, **TENGAH**, **BOTTOM ≤−100**. X axis must show absolute calendar dates, not arbitrary index positions.
5. On mouse hover or click/touch, vertical dashed crosshair, highlight circles for all four assets, **exact date** in a header, and **four synchronized numeric cards** directly beneath the plot. Cards update together and must stay readable, including mobile 2x2 layout.
6. Each of the four cards shows ticker, zone label, current WMA6 (large), previous WMA6, **ΔWMA, Δ²WMA, angle** and current **CCI18**. Preserve previous -> latest values, not just direction.
7. Show **three angle samples** (oldest → previous → latest) and status color:
   - red (🔴): downward slope is getting more negative, increasing downside pressure;
   - black/neutral (⚫): downward slope still negative but less negative, pressure easing;
   - green (🟢): WMA positive slope, strengthening upward slope;
   - **orange** (🟠): WMA positive slope but its upward speed is slowing. Never call a declining slope "green".
8. **Crossing circles** placed on each asset's **WMA6 line at the CLOSED candle where CCI18 crosses WMA6**; emphasize dot/ring and show `CROSS UP` or `CROSS DOWN` on the hover card for that candle. Keep crossing rings subdued/semitransparent, not overpowering data lines. Date of crossing must be exact.
9. Provide fast date selection chips **24 June 2026 (6D), 16 September 2026 (6D), 22 September 2026 (6D), 9 November 2026 (current reference)** with hover/click support; shift latest chip when newer verified CLOSED data arrives. 22 June and 18 September 2026 are **4D CLOSED**, so if user studies them, display their exact 4D analysis separately and do not mislabel them 6D closes.
10. Footnote source, metric, per-exchange contract scope, timeframe, UTC anchor, calculated degrees, and next candle close WIB. No fabricated RUNNING data.
11. The primary locked visual is **6D OI 4-asset combined chart**, exactly this panel. Funding is an *additional separate scan/table* and must not displace/reformat the OI visual. Keep existing radar product formats independent.

## Math/source contract — MUST preserve

- Data: Coinalyze official API snapshots/historical daily OHLC for **selected individual contracts**, pulled by GitHub Action to `data/coinalyze/history/*_open-interest-history_daily.csv`, and current snapshots `data/coinalyze/current/`. Original project `imthequin2811-gif/radar-pisau-jatuh`.
- Scope: BTCUSDT_PERP.3, ETHUSDT_PERP.3, SOLUSDT_PERP.3, BNBUSDT_PERP.3, as recorded in `data/coinalyze/catalog/selected-markets.csv`. Never mislabel a single exchange as aggregate/global OI.
- Build custom 4D/6D/12D/18D candles on daily **Close** of the **OI data series** with annual reset Jan 1 **00:00 UTC**. Only mark bar `CLOSED` when *every constituent calendar day is present* and the bar's end is fully in the past. Incomplete bars must be marked separately as RUNNING, with no confirmation or crossing.
- **CCI(18, Close of OI candles)**. **WMA(6) computed on CCI**, not on price nor directly on OI.
- WMA6(t)=sum_{j=1..6}(j * CCI18(t-6+j)) / 21, where last/most recent CCI receives weight 6.
- ΔWMA(t)=WMA(t)-WMA(t-1), Δ²WMA(t)=ΔWMA(t)-ΔWMA(t-1), angle(t)=degrees(atan(ΔWMA(t)/20)); three angles from three consecutive CLOSED bars.
- CROSS UP iff CCI(t-1) ≤ WMA(t-1) and CCI(t)>WMA(t). CROSS DOWN iff CCI(t-1) ≥ WMA(t-1) and CCI(t)<WMA(t), both CLOSED. Crossing of CCI/WMA is distinct from zero crossing of WMA or a change in WMA slope.
- Follow the existing date boundaries and show UTC end converted to WIB (+07:00). In 2026, latest 6D verified CLOSED in the initial scan is **09 Nov 07:00 WIB**; next 6D close **15 Nov 07:00 WIB**.
- Never claim "real-time" if reading a stored CSV. Display `last fetched UTC` from `data/coinalyze/metadata.json`.
- Angle speed is comparison of the latest three samples; green/orange above rule applies to **slope**, not a positive raw WMA value.

## Required output on each scan

A. **The exact navy interactive 6D four-asset OI chart** with crosshair + date-linked four cards + crossing rings.
B. A compact 6D CLOSED data table for OI and funding with previous/latest WMA, Δ, Δ², angle (and 3-sample angles), with CCI crossings explicitly labeled only on real CLOSED bars.
C. Historical cross dates when requested, plus 12D/18D contextual table and scenarios only when there is enough data.
D. Clear distinction `CLOSED / RUNNING / PROJECTION / INSUFFICIENT_HISTORY`; do not fill gaps or fabricate OI/funding values.
E. Do not add, remove, or reorder assets, indicators, colors, headings, card fields, or layout in future scans without asking and obtaining user permission.

## Integrity / implementation

The last user-approved visible layout is the authoritative reference. This file is a *specification* to reproduce it; it does not authorize modification of the working scanner or existing automated GitHub workflow. Store changes in additive files only unless the user gives permission.
