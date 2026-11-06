"""Experimental GBPUSD 6D inversion of Liquidity Sweep + Mean Reversion.
Original: sweep-low => LONG toward mean; sweep-high => SHORT toward mean.
Inverse: sweep-low => SHORT continuation; sweep-high => LONG continuation.
Both draw on the same eligible events and use same 36-calendar-day expiry.
Inverse: stop beyond opposite side of sweep 6D bar; target fixed 2R.
Dukascopy BID D1, no OANDA. No broker execution.
"""
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import backtest_model_a_6d12d as test

RESULTS=Path("model_a_inverted_gbpusd_6d_results")
RESULTS.mkdir(exist_ok=True)

def valid_sweep_candidates(daily,bars):
    s=test.find_setups(bars,6)
    candidates=[]
    for event in s:
        if event["kind"] != "SWEEP_MEAN_REVERSION":
            continue
        after=daily[daily.date>=event["signal_closed"]]
        if after.empty: continue
        entry=float(after.open.iloc[0])
        original_risk=(entry-event["stop"])*event["side"]
        if original_risk<=0: continue
        # Eligibility of original mean reversion, preserved so all comparisons
        # start from the same exact signal setup, not a different signal sample.
        if (event["mid"]-entry)*event["side"] < 2*original_risk: continue
        # Skip outcomes without full historical window.
        if after.date.iloc[0]+pd.Timedelta(days=test.HOLD_DAYS)>daily.date.iloc[-1]+pd.Timedelta(days=1): continue
        bar=bars[bars.start==event["signal_start"]]
        if len(bar)!=1: raise ValueError("Candle lookup mismatch")
        candle=bar.iloc[0]
        reversed_side=-event["side"]
        reversed_stop=float(candle.low-2*test.PIP) if reversed_side==1 else float(candle.high+2*test.PIP)
        reversed_risk=(entry-reversed_stop)*reversed_side
        if reversed_risk<=0: continue
        rev=dict(event,kind="INVERTED_SWEEP_CONTINUATION",side=reversed_side,
                 stop=reversed_stop,mid=np.nan)
        candidates.append((event,rev))
    return candidates

def normalize(trades, strategy):
    d=trades.copy()
    if not d.empty: d["strategy"]=strategy
    return d

def annual(t, label):
    rows=[]
    for y in ["ALL", *list(range(2019,datetime.now(timezone.utc).year+1))]:
        sub=t if y=="ALL" or t.empty else t[t.entry_date.dt.year==y]
        rows.append(dict(strategy=label,year=y,**test.stats(sub)))
    return rows

def main():
    test.base.START="2017-01-01"
    d=test.daily_data(test.base.get_data("gbpusd"))
    b=test.calendar_bars(d,6)
    pairs=valid_sweep_candidates(d,b)
    orig_signals=[a for a,_ in pairs]
    reversed_signals=[z for _,z in pairs]
    original=normalize(test.backtest(d,orig_signals),"ORIGINAL_SWEEP_MEAN_REVERSION")
    inverted=normalize(test.backtest(d,reversed_signals),"INVERTED_SWEEP_CONTINUATION")
    if not len(original):
        raise ValueError("Original GBPUSD 6D sweep signals missing")
    if abs(original.net_R.sum()-(-8))>0.1:
        raise ValueError(f"Failed benchmark reproduction: {original.net_R.sum():.4f}R, expected -8R")
    # Separate non-overlap portfolios can enter different event subsets
    # because profit targets and exits differ. This is NOT paired-trade evidence.
    original.to_csv(RESULTS/"original_trades.csv",index=False)
    inverted.to_csv(RESULTS/"inverted_trades.csv",index=False)
    summary=annual(original,"ORIGINAL_SWEEP_MEAN_REVERSION")+annual(inverted,"INVERTED_SWEEP_CONTINUATION")
    pd.DataFrame(summary).to_csv(RESULTS/"yearly_comparison.csv",index=False)
    pd.DataFrame([dict(strategy=x,**test.stats(t))
                  for x,t in [("ORIGINAL",original),("INVERTED",inverted)]]).to_csv(
                  RESULTS/"summary.csv",index=False)
    print("Eligible common signal events:",len(pairs))
    print("Independent non-overlap portfolios (different executed subsets):")
    print(pd.read_csv(RESULTS/"summary.csv").to_string(index=False),flush=True)
    print("Dukascopy BID D1; calendar UTC 6D; up to 36 calendar days; flat 1.5pip fee")
    print("This reverses direction AND changes the exit objective to continuation 2R.")
    print("Simulated outcomes are NOT trading recommendations.")

if __name__=="__main__": main()
