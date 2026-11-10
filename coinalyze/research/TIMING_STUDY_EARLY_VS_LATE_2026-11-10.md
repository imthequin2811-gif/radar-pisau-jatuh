# COINALYZE RESEARCH NOTE — TIMING EARLY VS LATE
Research date: 2026-11-10. User request: study circled dates on LOCKED 6D OI navy chart and improve autonomous decisions without waiting for late confirmations.
Status: **Research reference, NOT a change to USER-LOCKED indicators/visual/automatic trading triggers.** Any implementation changes require explicit user approval.

## Source and point-in-time caveat
- Coinalyze one selected individual perpetual contract per asset from `data/coinalyze/history/*` as collected on **2026-11-09 10:05:42 UTC**, with annual Jan 1 00:00 UTC custom bars and daily complete CLOSED data.
- Binance Spot daily CLOSED OHLCV from `data/binance/{BTC,ETH,SOL,BNB}USDT_1D_source.csv`; never use RUNNING or mix spot price into OI indicator calculations.
- CCI(18, Close of OI/funding metric), then WMA(6) on CCI18; angle = degrees(atan(delta WMA6/20)).
- **Hindsight safeguard:** "blind" reasoning below reconstructs information available by candle close without *using* later bars for the decision. But source history was downloaded on 9 Nov and is **not archived point-in-time snapshots captured on each historical decision date**; historical source revisions cannot be ruled out. Later returns are separate evaluations, not decision inputs.
- All reference close dates are 07:00 WIB; 4D and 6D close dates should not be swapped. Buttons below original chart (24 Jun, 16 Sep, 22 Sep, 09 Nov) are navigation shortcuts, NOT signals.

## Case 1: 24 Jun 2026 / early bottom phase
**Autonomous choice if making a directional decision as of 24 Jun 07 WIB: LONG SOL (anticipative small position, not large confirmation).**
- Last 4D CLOSED 22 Jun: SOL OI WMA6 -111.4, delta +16.5, delta^2 +22.8; 4D OI CCI cross UP occurred 18 Jun (CCI -115.8 versus WMA -127.8), but WMA slope was still negative then.
- At 6D CLOSED 24 Jun: SOL OI WMA6 -113.8 → -101.7, delta **+12.1**, delta^2 **+42.2**, CCI -36.9 > WMA -101.7 => **CROSS UP**. FUNDING 6D WMA -69.1, delta -26.1, crossing DOWN. This is early bottom pressure exhaustion, not a guaranteed immediate reversal.
- At that moment last 12D OI WMA was -82.8 with delta -6.7 (18 Jun) and 18D -87.1 with delta +1.0 (12 Jun): higher-TF mixed, hence limited size.
- Binance Spot 24 Jun close SOL **$69.71**. 30 Jun close **$75.16** (+7.82% after 6d); 6 Jul close **$81.59** (+17.04% after 12d). Prices are post-decision evaluation, not executable fills.
- A 4D SOL cross alone on 18 Jun at $72.05 would have been early and experienced a decline to 24 Jun close $69.71 (~-3.25%); hence 4D alerts must be sized/validated.

## Case 2: 16 Sep 2026 / early upward rotation (before large 6D crossing)
**Autonomous choice as of 16 Sep 07 WIB: LONG ETH as momentum-follow-through; consider BTC on later 4D confirmation.**
- Last 4D CLOSED 14 Sep: ETH OI WMA6 126.7 (+4.8), CCI145.4 > WMA126.7 => fresh CROSS UP.
- 6D CLOSED 16 Sep ETH OI WMA6 80.5 → **92.5**, delta **+11.9**, CCI 98.4 > WMA; 12D CLOSED 10 Sep WMA 14.3 (+16.2), 18D CLOSED 10 Sep WMA -38.9 (+18.6). Multiple timeframe slopes upward, 18D lower-zone recovery.
- 6D ETH funding WMA 34.4 delta -31.0, risk/positioning divergence, not a guarantee of immediate price upside.
- Spot ETH 16 Sep close **$2,398.26**; 22 Sep close **$2,776.19** (+15.76% in next 6d). If waiting until 22 Sep to LONG, already paying +15.76% more; subsequent 28 Sep price $2,688.65 (-3.15% over next 6d).
- **False-signal counterexample**: 4D ETH OI crossed DOWN 18 Sep at spot $2,447.28, yet 22 Sep spot was $2,776.19 (+13.44% next 4d). Hence NEVER auto-reverse direction from a lone 4D cross against positive 6D+12D slope.

## Case 3: 18 Sep 4D vs 22 Sep 6D / BTC early cross
**Autonomous choice as of 18 Sep 07 WIB: anticipative LONG BTC SHOT 1, with 6D confirmation later.**
- BTC 4D OI at 18 Sep: WMA6 55.8, CCI68.7 => CROSS UP; 4D funding WMA6 7.3, CCI53 => CROSS UP.
- Previous 6D CLOSED 16 Sep: BTC OI WMA6 **52.1**, delta +0.5 (flattening); 12D Sep10 OI WMA -5.2 delta +4.6; 18D Sep10 -37.4 delta +6.6. Still early, not all-TF confirmation.
- Spot BTC 18 Sep close **$76,417.01**; 22 Sep close **$86,620.00**, +13.35% in just 4 days. BTC 6D CCI/WMA CROSS UP only CLOSED 22 Sep, when price had moved significantly. Thus "wait for 6D CROSS" alone risks late entry.
- 22 Sep BTC OI 6D WMA **52.1 → 100.5**, delta +48.4 and CCI218.5, **CROSS UP**; BTC 12D also CROSS UP. The move was already largely under way.

## Case 4: 22 Sep → 26 Sep → 28 Sep / early short instead of chase
**Autonomous judgement as of 22 Sep:** Do not chase LONG after the impulse; **bias SHORT ETH** only as a conditional mean-reversion/failure scenario, NOT an executable short without price confirmation.
- 22 Sep ETH OI 6D WMA 92.5 → 131.4, delta +38.9, CCI209.9; 4D funding CCI/WMA fresh CROSS DOWN, 6D funding WMA14.4 (delta -20). ETH spot +15.76% compared with 16 Sep. Classic late-entry/squeeze risk with conflicting funding momentum.
- 26 Sep ETH 4D OI: CCI91.8 < WMA115.3 => **CROSS DOWN**; spot close **$2,691.61**. This is a stronger anticipative short trigger than immediately fading the 22 Sep pump.
- 28 Sep ETH 6D OI: CCI128.6 < WMA136.2 => **CROSS DOWN**; spot close $2,688.65. 6D WMA still slightly rose (+4.8), so this is CCI/WMA crossing, NOT 6D WMA bearish slope yet; 6D WMA slope went negative by 4 Oct.
- ETH spot 16 Oct close **$2,442.08**, -9.27% vs 26 Sep close. Outcome analysis only, not backfilled justification.
- DO NOT claim every 4D DOWN is a valid SHORT; 18 Sep ETH false down was followed by +13.44% in four days.

## Case 5: 09 Nov 2026 / late-downtrend decision
**Autonomous current bias: SHORT SOL; timing: NO IMMEDIATE MARKET SHORT near the 6D low.**
- SOL 4D OI CROSS DOWN at Nov9, WMA 8.5 → -13.1, delta -21.5; 6D OI 55.2 → 36.0, delta -19.2, CCI -1.1 below WMA; 12D OI 134.6 → 100.7, delta -33.9; 18D last Nov3 OI 37.4 → 56.7, delta +19.3, still conflicted.
- 6D SOL funding WMA 50.7 → 17.8, delta -33.0, CCI -76.4 < WMA17.8 => CROSS DOWN.
- Binance Spot latest 9 Nov 6D CLOSED close $86.54 and LOW $85.02. 10 Nov 07 WIB daily CLOSED close $86.74. Not enough future data to evaluate this direction. Do not use future candles, fabricate performance, or claim fill.
- Example timing: avoid shorting near $85 low; reassess a **failed rebound** near earlier price structure $91–93, invalidate after sustained recovery above $98.14 (6D Nov9 high); conditional illustrative plan only, not an actual order.

## Proposed timing heuristic to examine (NOT an approved automatic rule)
1. **EARLY 4D:** OI CCI/WMA CROSS UP or DOWN near meaningful zones, plus WMA delta^2 easing/turning; check prior 6D slope and 12D/18D context. Treat as SHOT 1/alert if price hasn't already exploded.
2. **CONFIRM 6D:** CCI/WMA CROSS plus slope and structure. A 6D CROSS can lag by a whole impulse; compare **spot % movement from prior 6D CLOSED** to current price to avoid chasing.
3. **AFTER PARABOLIC MOVE:** price rose ~10%+ from prior 6D (context-specific, a descriptive threshold needing statistical validation), 6D WMA/OI CCI high or WMA near TOP, funding diverges, then prioritize **taking profit / watching 4D failure**, rather than automatically opening another LONG. Confirm SHORT with 4D cross DOWN and structure, then 6D cross DOWN.
4. **FALSE CROSS FILTER:** 4D cross is not enough for a full reversal when 6D and 12D slope oppose it (ETH 18 Sep false downside); 6D CROSS alone is not enough to buy if price already ran sharply (ETH 22 Sep).
5. **DECISION != ENTRY TIMING:** each scan autonomously chooses directional bias and declares whether entry is justified at verified price, with level-based invalidation. No future leakage, no interpretation of stale OI as intraday live.

## Conclusions and limits
- Key historical candidates: **LONG SOL 24 Jun**, **LONG ETH 16 Sep**, **LONG BTC 18 Sep** (4D early), **SHORT ETH 26 Sep** (4D early / 6D follow through 28 Sep), **SHORT SOL bias 9 Nov with entry timing on failed retest**.
- Results cited are selective case studies, **NOT** a comprehensive quantitative backtest. Transaction costs, fees, funding payments, adverse excursion, intraday fills, and survivorship effects are not modeled. Some potential 4D crosses demonstrably fail.
- Leave two USER LOCK files unchanged: `coinalyze/MASTER_LOCK_VISUAL_6D_OI_FUNDING_2026-11-09.md` and `coinalyze/LOCK_FORCED_DIRECTIONAL_DECISION_2026-11-10.md`.
