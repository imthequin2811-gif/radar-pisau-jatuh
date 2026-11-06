"""
Model A Forex + MONTHLY CCI(20, Close) / WMA(5) on CCI.
Daily Price Action, Liquidity Sweep + Mean Reversion and Strong Breakout.
Dukascopy BID D1 feed (NOT OANDA). No orders executed.
Calendar UTC months. Only the PREVIOUS fully closed month is known at entry.
Keep original Model A script and reports intact for comparison.
"""
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import backtest_model_a_forex as base

# Include sufficient monthly warm-up; report trades only since 2019.
base.START = "2015-01-01"
EVALUATE_FROM = "2019-01-01"
RESULTS = Path("model_a_monthly_results")
RESULTS.mkdir(parents=True, exist_ok=True)
KINDS = ("ALL", "SWEEP_MEAN_REVERSION", "STRONG_BREAKOUT")


def closed_monthly_indicators(daily):
    """Build true UTC calendar months; exclude the current incomplete month."""
    d = daily.copy()
    d["month"] = d["date"].dt.tz_convert("UTC").dt.tz_localize(None).dt.to_period("M")
    m = d.groupby("month", sort=True).agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        sessions=("close", "size"),
    )
    current_month = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None).to_period("M")
    m = m.loc[m.index < current_month].copy()
    # Missing or unusually incomplete months cannot be used as valid input.
    m.loc[m.sessions < 12, "close"] = np.nan

    close = m["close"]
    sma20 = close.rolling(20, min_periods=20).mean()
    mad20 = close.rolling(20, min_periods=20).apply(
        lambda a: float(np.abs(a - a.mean()).mean()), raw=True
    )
    m["cci20"] = (close - sma20) / (0.015 * mad20.replace(0, np.nan))
    weights = np.arange(1, 6, dtype=float)
    m["wma5_cci"] = m["cci20"].rolling(5, min_periods=5).apply(
        lambda a: float(np.dot(a, weights) / weights.sum()), raw=True
    )
    m["slope"] = m["wma5_cci"].diff()
    m["acceleration"] = m["slope"].diff()
    m["closed_utc"] = (m.index + 1).to_timestamp().tz_localize("UTC").astype(str)
    return m


def tag_candidates(candidates, monthly, daily_len):
    enriched = []
    for s in candidates:
        if s["entry_date"] < EVALUATE_FROM:
            continue
        # Never label a position that cannot be observed for the full HOLD window.
        if s["idx"] + base.HOLD > daily_len:
            continue
        # Entry month's monthly candle is RUNNING; use previous CLOSED month.
        previous_month = pd.Period(s["entry_date"], freq="M") - 1
        if previous_month not in monthly.index:
            continue
        m = monthly.loc[previous_month]
        fields = ["cci20", "wma5_cci", "slope", "acceleration"]
        if not np.isfinite(m[fields].to_numpy(dtype=float)).all():
            continue
        s = dict(s)
        s.update({
            "monthly_closed": str(previous_month),
            "monthly_cci20": float(m.cci20),
            "monthly_wma5_cci": float(m.wma5_cci),
            "monthly_slope": float(m.slope),
            "monthly_acceleration": float(m.acceleration),
        })
        # Experimental filter, not a claim of profitability:
        # Reversals = acceleration bends toward intended direction.
        # Breakouts = monthly WMA5 slope agrees with breakout direction.
        if s["setup"] == "SWEEP_MEAN_REVERSION":
            keep = s["sign"] * float(m.acceleration) > 0
        else:
            keep = s["sign"] * float(m.slope) > 0
        s["monthly_filter_pass"] = bool(keep)
        enriched.append(s)
    return enriched


def report_row(pair, variant, period, setup, trades):
    t = trades
    if setup != "ALL":
        t = t[t["setup"] == setup] if not t.empty else t
    return {
        "pair": pair.upper(),
        "variant": variant,
        "year": period,
        "setup": setup,
        **base.stats(t),
    }


def write_reports(pair, monthly, d1):
    candidates = tag_candidates(base.signals(d1), monthly, len(d1))
    baseline = base.simulate(d1, candidates)
    filtered = base.simulate(
        d1, [c for c in candidates if c["monthly_filter_pass"]]
    )
    monthly.to_csv(RESULTS / f"{pair}_monthly_cci_wma.csv", index_label="month")
    baseline.to_csv(RESULTS / f"{pair}_baseline_trades.csv", index=False)
    filtered.to_csv(RESULTS / f"{pair}_monthly_filtered_trades.csv", index=False)

    all_rows, yearly_rows = [], []
    for variant, trades in (("BASELINE", baseline), ("MONTHLY_FILTER", filtered)):
        for setup in KINDS:
            all_rows.append(report_row(pair, variant, "ALL", setup, trades))
        for year in range(2019, datetime.now(timezone.utc).year + 1):
            if trades.empty:
                year_trades = trades
            else:
                year_trades = trades[trades.entry_date.str[:4] == str(year)]
            for setup in KINDS:
                yearly_rows.append(
                    report_row(pair, variant, year, setup, year_trades)
                )
    print(
        f"{pair.upper()}: candidates={len(candidates)} "
        f"filter_allowed={sum(c['monthly_filter_pass'] for c in candidates)} "
        f"baseline_trades={len(baseline)} filtered_trades={len(filtered)}",
        flush=True,
    )
    return all_rows, yearly_rows


def main():
    summary, yearly = [], []
    for pair in base.SYMBOLS:
        daily = base.get_data(pair)
        monthly = closed_monthly_indicators(daily)
        if monthly["wma5_cci"].notna().sum() < 30:
            raise ValueError(f"{pair}: insufficient valid CLOSED monthly history")
        overall, annual = write_reports(pair, monthly, daily)
        summary.extend(overall)
        yearly.extend(annual)
    pd.DataFrame(summary).to_csv(RESULTS / "summary.csv", index=False)
    pd.DataFrame(yearly).to_csv(RESULTS / "yearly_results.csv", index=False)
    print(pd.DataFrame(summary).to_string(index=False), flush=True)
    print("Finished: monthly CCI20 Close / WMA5 on CCI; only CLOSED months.")
    print("All three Model A components evaluated; sweep and breakout are alternative setups.")
    print("Dukascopy BID D1; assumed roundtrip friction 1.5 pip; not OANDA.")
    print("Backtest only, no order execution. Check historical bias and slippage.")


if __name__ == "__main__":
    main()
