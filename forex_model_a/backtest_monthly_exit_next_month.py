"""FOREX 1M: enter at first trading day of month M; exit at CLOSE of M+1
if stop-loss has not triggered earlier. After SL, wait until NEXT month open.
ONE position per pair, never overlap. Direction: two previous CLOSED months.
No fixed-price TP. Monthly time-exit can be PROFIT OR LOSS.
Backtest only. Dukascopy BID D1 (not TradingView OANDA).
"""
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import backtest_monthly_structure as model
import backtest_model_a_forex as base

base.START = "2017-01-01"
OUT = Path("monthly_next_month_exit_results")
OUT.mkdir(parents=True, exist_ok=True)
FIRST_YEAR = 2019
START_CAPITAL_USD = 10000.0
RISK_FRACTION = 0.01
MAX_LEVERAGE = 10.0
BUFFER_FRACTION = 0.10
COST_PIPS = 1.5
PIP = 0.0001


def valid_months(d):
    m = model.monthly(d)
    # The incomplete current UTC month is NOT an eligible completed month.
    now = pd.Timestamp.now(tz="UTC").tz_localize(None).to_period("M")
    m = m.loc[m.index < now].copy()
    # Strict calendar coverage check: at least 90% weekday D1 rows.
    m["valid"] = m.sessions >= np.ceil(m.expected_weekdays * 0.90)
    return m


def position_size(pair, entry, stop):
    """Illustration: fixed $100 risk, at most $100k entry notional (10x).
    USDCHF risk conversion uses entry rate, so USD realized PnL is approximate.
    """
    distance = abs(entry - stop)
    quote_to_usd = (1.0 / entry) if pair == "usdchf" else 1.0
    per_unit_usd = distance * quote_to_usd
    units_for_risk = (START_CAPITAL_USD * RISK_FRACTION) / per_unit_usd
    notional_usd_per_unit = 1.0 if pair == "usdchf" else entry
    units_for_leverage = START_CAPITAL_USD * MAX_LEVERAGE / notional_usd_per_unit
    units = min(units_for_risk, units_for_leverage)
    actual_risk = units * per_unit_usd
    return units, actual_risk, units * notional_usd_per_unit / MAX_LEVERAGE


def run_trade(d, pair, month, prev, prior):
    """Enter at month M open; check SL day by day through end of month M+1."""
    side, structure = model.direction(prev, prior)
    future_month = month + 1
    prices = d[(d.month == month) | (d.month == future_month)]
    entry_candle = prices.iloc[0]
    entry = float(entry_candle.open)
    prev_range = float(prev.high - prev.low)
    if not np.isfinite(prev_range) or prev_range <= 0:
        raise ValueError(f"{pair}: invalid previous month range {month-1}")
    stop = (
        min(float(prev.low), entry - 0.35 * prev_range)
        - BUFFER_FRACTION * prev_range if side > 0 else
        max(float(prev.high), entry + 0.35 * prev_range)
        + BUFFER_FRACTION * prev_range
    )
    risk = (entry-stop) * side
    if risk <= 0: raise ValueError(f"{pair}: invalid stop {month}")

    # No fixed TP. Position is forcibly closed on LAST D1 CLOSE of M+1.
    price_exit = float(prices.iloc[-1].close)
    date_exit = prices.iloc[-1].date
    why = "NEXT_MONTH_CLOSE"
    for _, candle in prices.iterrows():
        hit = (float(candle.low) <= stop if side > 0
               else float(candle.high) >= stop)
        gap = (float(candle.open) < stop if side > 0
               else float(candle.open) > stop)
        if hit:
            price_exit = float(candle.open) if gap else stop
            date_exit = candle.date
            why = "STOP"
            break

    gross_r = (price_exit-entry)*side/risk
    net_r = gross_r - COST_PIPS * PIP / risk
    units, dollar_risk, margin = position_size(pair, entry, stop)
    return {
        "pair": pair.upper(), "entry_month": str(month),
        "structure": structure, "direction": "LONG" if side > 0 else "SHORT",
        "previous_closed_month": str(month-1),
        "previous_high": float(prev.high), "previous_low": float(prev.low),
        "entry_date_utc": str(entry_candle.date),
        "entry": entry, "sl": float(stop), "tp": "CLOSE_NEXT_MONTH",
        "planned_exit_month": str(future_month),
        "exit_date_utc": str(date_exit), "exit": price_exit,
        "exit_reason": why, "net_R": float(net_r),
        "risk_pips": float(risk / PIP),
        "illustrative_units": float(units),
        "illustrative_initial_risk_usd": float(dollar_risk),
        "illustrative_initial_margin_usd": float(margin),
        "illustrative_pnl_usd": float(net_r * dollar_risk)
    }


def summary_metrics(t):
    r = t.net_R.to_numpy(dtype=float) if not t.empty else np.array([])
    if len(r) == 0:
        return {"trades":0,"stop_rate_pct":np.nan,"win_rate_pct":np.nan,
                "total_R":0.0,"total_pnl_usd":0.0,
                "profit_factor":np.nan,"max_drawdown_R":0.0}
    wins = float(r[r > 0].sum())
    losses = float(-r[r < 0].sum())
    curve = np.r_[0, np.cumsum(r)]
    return {
        "trades": int(len(t)),
        "stop_rate_pct": round(100*(t.exit_reason=="STOP").mean(), 1),
        "win_rate_pct": round(100*np.mean(r > 0), 1),
        "total_R": round(float(r.sum()), 2),
        "total_pnl_usd": round(float(t.illustrative_pnl_usd.sum()), 2),
        "profit_factor": round(wins/losses,3) if losses > 0 else np.nan,
        "max_drawdown_R": round(float(np.min(curve-np.maximum.accumulate(curve))),2)
    }


def main():
    combined = []; yearly = []; recent = []; audit = []
    today = pd.Timestamp.now(tz="UTC").tz_localize(None).to_period("M")
    for pair in base.SYMBOLS:
        raw = base.get_data(pair)
        d = model.clean_daily(raw)
        m = valid_months(d)
        first_allowed = pd.Period(f"{FIRST_YEAR}-01",freq="M")
        next_allowed = first_allowed
        trades = []
        for current in m.index:
            if current < next_allowed or current < first_allowed: continue
            if current+1 >= today: continue
            previous, prior, follow = current-1,current-2,current+1
            if not all(x in m.index for x in (previous,prior,follow)): continue
            if not all(bool(m.loc[x,"valid"]) for x in (prior,previous,current,follow)):
                continue
            t = run_trade(d,pair,current,m.loc[previous],m.loc[prior])
            trades.append(t)
            exit_month = pd.Timestamp(t["exit_date_utc"]).to_period("M")
            # Reenter at next month's OPEN following exit, NEVER within same month.
            next_allowed = exit_month+1

        t = pd.DataFrame(trades)
        t.to_csv(OUT/f"{pair}_trades.csv", index=False)
        combined.append({"pair":pair.upper(),**summary_metrics(t)})
        for year in range(FIRST_YEAR,datetime.now(timezone.utc).year+1):
            subset = (t[t.entry_month.str[:4]==str(year)] if not t.empty else t)
            yearly.append({"pair":pair.upper(),"entry_year":year,**summary_metrics(subset)})
        if not t.empty: recent.append(t.iloc[-1].to_dict())
        audit.append({"pair":pair.upper(),"first_daily_utc":str(d.date.iloc[0]),
                      "last_daily_utc":str(d.date.iloc[-1]),
                      "months_with_daily_data":int(len(m)),
                      "valid_completed_months":int(m.valid.sum()),
                      "simulated_trades":len(t)})
        print(f"{pair.upper()} trades={len(t)} total_R={summary_metrics(t)['total_R']}",flush=True)

    pd.DataFrame(combined).to_csv(OUT/"summary.csv",index=False)
    pd.DataFrame(yearly).to_csv(OUT/"yearly_results.csv",index=False)
    pd.DataFrame(recent).to_csv(OUT/"latest_completed_trade.csv",index=False)
    pd.DataFrame(audit).to_csv(OUT/"data_audit.csv",index=False)
    print(pd.DataFrame(combined).to_string(index=False), flush=True)
    print("RULES: enter first D1 open each eligible month when FLAT; SL previous-month "
          "high/low plus 10% range; no price TP; forced exit at next-month last D1 CLOSE. "
          "If SL hit, no reentry until next month. Never overlapping trades. "
          "Fixed initial USD risk ~1%, leverage capped 10x; USDCHF USD-PnL approximated "
          "at entry rate. Assumed cost 1.5pip; swap and real slippage excluded. "
          "Dukascopy BID data, NOT OANDA. Not investment advice or live trading.",flush=True)


if __name__ == "__main__":
    main()
