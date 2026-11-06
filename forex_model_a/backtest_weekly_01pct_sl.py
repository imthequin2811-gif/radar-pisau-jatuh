"""Forex model: weekly 1W structure, mandatory entry when flat, 0.1% PRICE stop.
At the first D1 open of ISO week W enter using W-1/W-2 fully CLOSED weekly
structure. Stop at 0.1% from entry. No fixed-price take profit. Otherwise
exit at the last D1 CLOSE of week W+1. If stopped, only reenter at next
week's first D1 open. One position at a time per pair.
Dukascopy BID D1 data, NOT OANDA. Research/backtest ONLY.
"""
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import backtest_model_a_forex as base
import backtest_monthly_structure as monthly_base

base.START = "2017-01-01"
PAIRS = ("eurusd", "gbpusd", "usdchf")
FIRST_YEAR = 2019
STOP_FRAC = 0.001    # 0.1% of ENTRY PRICE, NOT 0.1% of capital
INITIAL_CAPITAL_USD = 10000.
RISK_USD_PER_TRADE = 100.    # 1% of fixed initial capital
MAX_LEVERAGE = 10.
ROUND_TRIP_PIPS = 1.5
PIP = 0.0001
OUT = Path("weekly_01pct_sl_results")
OUT.mkdir(parents=True, exist_ok=True)


def utc_week_start(ts):
    t = pd.Timestamp(ts)
    return t.normalize() - pd.Timedelta(days=t.weekday())


def prep_data(raw):
    d = monthly_base.clean_daily(raw).copy()
    d["week"] = d.date.apply(utc_week_start)
    return d


def weekly_candles(d):
    weeks = d.groupby("week", sort=True).agg(
        open=("open","first"), high=("high","max"),low=("low","min"),
        close=("close","last"),sessions=("close","size"),
        first_day=("date","first"),last_day=("date","last"))
    current_week = utc_week_start(pd.Timestamp.now(tz="UTC"))
    weeks = weeks[weeks.index < current_week].copy()
    weeks["valid"] = weeks.sessions >= 4
    return weeks


def sizing(pair, entry, stop):
    """Fixed $100 risk, cap 10x margin. CHF conversion approximated at entry."""
    price_distance = abs(entry - stop)
    conversion = (1/entry if pair == "usdchf" else 1.)
    risk_dollars_per_unit = price_distance*conversion
    units_for_risk = RISK_USD_PER_TRADE / risk_dollars_per_unit
    notional_dollars_per_unit = (1. if pair == "usdchf" else entry)
    max_units = INITIAL_CAPITAL_USD * MAX_LEVERAGE / notional_dollars_per_unit
    units = min(units_for_risk, max_units)
    actual_usd_risk = units * risk_dollars_per_unit
    margin_usd = units * notional_dollars_per_unit / MAX_LEVERAGE
    return units, actual_usd_risk, margin_usd


def trade(d, weekly, pair, w):
    previous = weekly.loc[w-pd.Timedelta(days=7)]
    prior = weekly.loc[w-pd.Timedelta(days=14)]
    side, label = monthly_base.direction(previous, prior)
    following = w+pd.Timedelta(days=7)
    rows = d[(d.week == w)|(d.week == following)]
    if rows.empty: raise ValueError("No daily OHLC in tested week")
    entry_candle = rows.iloc[0]
    entry = float(entry_candle.open)
    stop = entry*(1-STOP_FRAC) if side > 0 else entry*(1+STOP_FRAC)
    risk = abs(entry-stop)
    units, risk_usd, margin = sizing(pair, entry, stop)
    exit_px = float(rows.iloc[-1].close)
    exit_date = rows.iloc[-1].date
    why = "NEXT_WEEK_CLOSE"

    for _,bar in rows.iterrows():
        if side > 0:
            sl_hit = float(bar.low)<=stop
            adverse_gap = float(bar.open)<stop
        else:
            sl_hit = float(bar.high)>=stop
            adverse_gap = float(bar.open)>stop
        if sl_hit:
            exit_px = float(bar.open) if adverse_gap else stop
            exit_date = bar.date
            why = "STOP"
            break

    gross_r = (exit_px-entry)*side/risk
    net_r = gross_r - ROUND_TRIP_PIPS*PIP/risk
    return {
        "pair":pair.upper(), "week_open_utc":str(w),
        "structure":label, "side":"LONG" if side>0 else "SHORT",
        "prev_1w_high":float(previous.high),"prev_1w_low":float(previous.low),
        "prev_1w_close":float(previous.close),
        "entry_date_utc":str(entry_candle.date),"entry":entry,
        "sl":stop,"sl_price_pct":STOP_FRAC*100,
        "fixed_tp":"NONE","planned_exit_week":str(following),
        "exit_date_utc":str(exit_date),"exit":exit_px,
        "exit_reason":why,"net_R":net_r,
        "stop_pips":risk/PIP, "units":units,
        "initial_risk_usd":risk_usd,
        "margin_usd":margin,
        "pnl_usd_estimate":net_r*risk_usd,
    }


def summary(t):
    if t.empty:
        return dict(trades=0,win_rate_pct=np.nan,stop_rate_pct=np.nan,
                    total_R=0.,net_pnl_usd=0.,max_drawdown_R=0.,
                    profit_factor=np.nan)
    r=t.net_R.reset_index(drop=True)
    equity=np.r_[0, r.cumsum().to_numpy()]
    profits=float(r[r>0].sum()); losses=-float(r[r<0].sum())
    return dict(
        trades=int(len(t)),
        win_rate_pct=round(float((r>0).mean()*100),1),
        stop_rate_pct=round(float((t.exit_reason=="STOP").mean()*100),1),
        total_R=round(float(r.sum()),2),
        net_pnl_usd=round(float(t.pnl_usd_estimate.sum()),2),
        max_drawdown_R=round(float((equity-np.maximum.accumulate(equity)).min()),2),
        profit_factor=(round(profits/losses,3) if losses>0 else np.nan),
    )


def main():
    all_rows=[];year_rows=[];latest=[];audits=[]
    for pair in PAIRS:
        d=prep_data(base.get_data(pair))
        w=weekly_candles(d)
        next_allowed=pd.Timestamp(f"{FIRST_YEAR}-01-01",tz="UTC")
        trades=[]
        for week in w.index:
            if week.year<FIRST_YEAR or week<next_allowed:
                continue
            previous=week-pd.Timedelta(days=7)
            prior=week-pd.Timedelta(days=14)
            following=week+pd.Timedelta(days=7)
            if any(v not in w.index for v in (prior,previous,following)):
                continue
            if not all(bool(w.loc[v,"valid"]) for v in
                       (prior,previous,week,following)):
                continue
            result=trade(d,w,pair,week)
            trades.append(result)
            last_exit_week=utc_week_start(pd.Timestamp(result["exit_date_utc"]))
            # Re-entry at NEXT weekly OPEN only. No overlapping positions.
            next_allowed=last_exit_week+pd.Timedelta(days=7)

        t=pd.DataFrame(trades)
        t.to_csv(OUT/f"{pair}_trades.csv",index=False)
        all_rows.append(dict(pair=pair.upper(),**summary(t)))
        if not t.empty:
            t["entry_year"]=pd.to_datetime(t.week_open_utc,utc=True).dt.year
        for yr in range(FIRST_YEAR,datetime.now(timezone.utc).year+1):
            yr_t=t[t.entry_year==yr] if not t.empty else t
            year_rows.append(dict(pair=pair.upper(),year=yr,**summary(yr_t)))
        if not t.empty: latest.append(t.iloc[-1].to_dict())
        audits.append(dict(pair=pair.upper(),raw_week_count=len(w),
                           valid_weeks=int(w.valid.sum()),
                           start_D1=str(d.date.min()),
                           last_D1=str(d.date.max()),
                           last_closed_week=str(w.index[-1])))
        print(f"{pair.upper()}: trades={len(t)} total_R={summary(t)['total_R']} "
              f"stop_rate={summary(t)['stop_rate_pct']}%",flush=True)
    pd.DataFrame(all_rows).to_csv(OUT/"summary.csv",index=False)
    pd.DataFrame(year_rows).to_csv(OUT/"yearly_results.csv",index=False)
    pd.DataFrame(latest).to_csv(OUT/"latest_completed_trades.csv",index=False)
    pd.DataFrame(audits).to_csv(OUT/"data_audit.csv",index=False)
    print(pd.DataFrame(all_rows).to_string(index=False),flush=True)
    print("Backtest: 1W CLOSED structure; weekly open when FLAT; SL=0.1% price; "
          "no fixed TP; exit next-week CLOSE unless SL hit; after SL "
          "reenter next week; capital $10k, risk about $100/trade, cap leverage 10x. "
          "Fees 1.5 pip estimate; no swaps or dynamic slippage. "
          "Dukascopy BID D1, not OANDA. No live orders.", flush=True)


if __name__=="__main__":
    main()
