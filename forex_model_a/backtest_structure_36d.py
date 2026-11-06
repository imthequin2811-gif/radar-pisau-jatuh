"""Compare forced monthly structural entries with true 36-calendar-day candles.
SOURCE: Dukascopy BID 1D, not OANDA. No orders, backtest only.

36D anchoring: each Jan 1 00:00 UTC; 10 full 36-day candles each year.
Year-end leftover 5/6 calendar days are NOT treated as a 36D candle.
1 position per FULL eligible 36D candle, entering next block's first D1 open.
Signal: HH/HL -> LONG; LH/LL -> SHORT; mixed -> last two closes.
SL: previous CLOSED 36D extreme ± 10% its range, with gap safety floor.
TP: alternative 1.5R / 2R, close after current 36D interval if neither hit.
Data quality: missing OHLC never fabricated; requires 90% weekday coverage,
last two CLOSED bars valid, and fully CLOSED current 36D block.
"""
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import backtest_monthly_structure as monthly_model
import backtest_model_a_forex as base

base.START = "2017-01-01"
REPORT = Path("structure_36d_results")
REPORT.mkdir(exist_ok=True)
RR_TARGETS = (1.5, 2.0)
FIRST_YEAR = 2019
DAYS_PER_CANDLE = 36
CANDLES_PER_YEAR = 10
PIP = 0.0001
COST_PIPS = 1.5
SL_BUFFER = 0.10

def build_36d_bars(d):
    today = pd.Timestamp.now(tz="UTC").normalize()
    rows = []
    for year in range(int(d.date.dt.year.min()), int(d.date.dt.year.max()) + 1):
        anchor = pd.Timestamp(f"{year}-01-01", tz="UTC")
        for block_index in range(CANDLES_PER_YEAR):
            start = anchor + pd.Timedelta(days=DAYS_PER_CANDLE * block_index)
            end = start + pd.Timedelta(days=DAYS_PER_CANDLE)
            # Does not extend beyond Dec 31 because 10*36=360 <365/366.
            observed = d[(d.date >= start) & (d.date < end)]
            expected = int(np.busday_count(start.date(), end.date()))
            sufficient = (len(observed) >= int(np.ceil(expected * 0.90)))
            fully_closed = end <= today
            valid = bool(fully_closed and sufficient and len(observed)>0)
            rows.append({
                "year": year, "block": block_index + 1,
                "start": start, "end": end,
                "expected_weekdays": expected,
                "observed_sessions": len(observed),
                "valid": valid,
                "open": float(observed.open.iloc[0]) if valid else np.nan,
                "high": float(observed.high.max()) if valid else np.nan,
                "low": float(observed.low.min()) if valid else np.nan,
                "close": float(observed.close.iloc[-1]) if valid else np.nan,
            })
    return pd.DataFrame(rows)

def simulate_period(prices, previous, prior, current, rr):
    side, struct = monthly_model.direction(previous, prior)
    initial = prices.iloc[0]
    entry = float(initial.open)
    span = float(previous.high - previous.low)
    if not np.isfinite(span) or span <= 0:
        raise ValueError("Invalid prior candle range")
    stop = (
        min(float(previous.low), entry - 0.35 * span) - SL_BUFFER * span
        if side > 0 else
        max(float(previous.high), entry + 0.35 * span) + SL_BUFFER * span
    )
    risk = (entry - stop) * side
    if risk <= 0:
        raise ValueError("Invalid SL direction")
    target = entry + side * rr * risk
    fill = float(prices.close.iloc[-1])
    exit_day = prices.date.iloc[-1]
    exit_reason = "PERIOD_END"
    for _, bar in prices.iterrows():
        if side > 0:
            stop_hit = float(bar.low) <= stop
            target_hit = float(bar.high) >= target
            gap = float(bar.open) < stop
        else:
            stop_hit = float(bar.high) >= stop
            target_hit = float(bar.low) <= target
            gap = float(bar.open) > stop
        if stop_hit:
            fill = float(bar.open) if gap else stop
            exit_day = bar.date
            exit_reason = "STOP"
            break
        if target_hit:
            fill = target
            exit_day = bar.date
            exit_reason = "TARGET"
            break
    net_R = (fill - entry) * side / risk - COST_PIPS * PIP / risk
    return {
        "year": int(current.year), "block": int(current.block),
        "start_utc": str(current.start), "end_utc": str(current.end),
        "previous_closed": str(previous.end),
        "structure": struct,
        "direction": "LONG" if side>0 else "SHORT",
        "rr_target": rr, "previous_high": float(previous.high),
        "previous_low": float(previous.low), "previous_close": float(previous.close),
        "entry_date": str(initial.date), "entry": entry, "sl": stop,
        "tp": target, "risk_pips": risk/PIP,
        "exit_date": str(exit_day), "exit_price": fill,
        "exit_reason": exit_reason, "net_R": float(net_R),
    }

def main():
    summary, annual, last, audit = [], [], [], []
    for pair in base.SYMBOLS:
        data = monthly_model.clean_daily(base.get_data(pair))
        bars = build_36d_bars(data)
        bars.to_csv(REPORT / f"{pair}_36d_candles.csv", index=False)
        valid_by_year = bars.groupby("year").valid.sum().to_dict()
        audit.append({
            "pair": pair.upper(),
            "first_D1": str(data.date.iloc[0]),
            "last_D1": str(data.date.iloc[-1]),
            "valid_36D_bars_by_year": str(valid_by_year),
            "invalid_36D_bars": int((~bars.valid).sum()),
            "year_end_days_omitted": "5 regular / 6 leap",
        })
        for rr in RR_TARGETS:
            trades = []
            for k in range(2, len(bars)):
                current, previous, prior = bars.iloc[k], bars.iloc[k-1], bars.iloc[k-2]
                if current.year < FIRST_YEAR:
                    continue
                if not (current.valid and previous.valid and prior.valid):
                    continue
                block_prices = data[(data.date >= current.start)&(data.date < current.end)]
                if block_prices.empty:
                    continue
                trades.append(simulate_period(block_prices, previous, prior, current, rr))
            t = pd.DataFrame(trades)
            t.to_csv(REPORT / f"{pair}_36d_tp{str(rr).replace('.','_')}_trades.csv", index=False)
            summary.append({"pair": pair.upper(), "tf": "36D", "rr_target": rr,
                            **monthly_model.performance(t)})
            for year in range(FIRST_YEAR, datetime.now(timezone.utc).year+1):
                subset = t[t.year == year] if not t.empty else t
                annual.append({"pair": pair.upper(), "tf": "36D", "rr_target": rr,
                               "year": year, **monthly_model.performance(subset)})
            if not t.empty:
                last.append({"pair": pair.upper(), **t.iloc[-1].to_dict()})
            print(f"{pair.upper()} 36D TP={rr}R valid_periods={len(t)} "
                  f"total_R={monthly_model.performance(t)['total_R']}", flush=True)

    pd.DataFrame(summary).to_csv(REPORT / "summary.csv", index=False)
    pd.DataFrame(annual).to_csv(REPORT / "yearly_results.csv", index=False)
    pd.DataFrame(last).to_csv(REPORT / "last_completed_36d.csv", index=False)
    pd.DataFrame(audit).to_csv(REPORT / "data_audit.csv", index=False)

    old = Path("monthly_structure_results/summary.csv")
    if old.exists():
        month = pd.read_csv(old)
        month["tf"] = "1M"
        compare = pd.concat([month, pd.DataFrame(summary)], ignore_index=True)
        compare.to_csv(REPORT / "comparison_1m_vs_36d.csv", index=False)
    print(pd.DataFrame(summary).to_string(index=False), flush=True)
    print("SOURCE Dukascopy BID D1, not OANDA. 36 calendar UTC days, reset each Jan 1; "
          "remaining 5/6 year-end days omitted, NEVER treated as full 36D. "
          "Trade/SL/TP fixed at each eligible 36D OPEN; exit by period end. "
          "No orders. Costs 1.5pip assumed; swap/slippage excluded.", flush=True)

if __name__ == "__main__":
    main()
