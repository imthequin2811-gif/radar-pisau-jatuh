"""12D Forex: ACTUAL three-way backtest, no indicator theorizing.
Identical eligible CLOSED 12-calendar-day liquidity-sweep signals for all:
  A: signal -> target fixed 2R, max 36 calendar days
  B: signal -> prior 60D high/low midpoint, max 36 calendar days
  C: signal -> no TP, close after 24 calendar days
Stop under/above sweep candle by 2 pips; each candidate must have B midpoint >=2R.
Execution: next D1 open after signal 12D close; D1 stops inspected every
trading session; if stop and target hit on same D1, stop assumed first.
No overlapping live-equivalent trades in independent portfolios. Also
matched-signal diagnostic with each opportunity simulated independently.
Cost model: roundtrip 1.5 pip; no swap/slippage, no orders.
Dukascopy BID D1, 12D reset on January 1 00:00 UTC each year.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import backtest_model_a_6d12d as base
from datetime import datetime, timezone

OUT=Path("forex_12d_three_models_results")
OUT.mkdir(exist_ok=True,parents=True)
PAIRS=("eurusd","gbpusd","usdchf")
MODELS=(("A_TP_2R",36),("B_TP_RANGE_MID",36),("C_EXIT_24D",24))
PIP=0.0001
FEE=1.5*PIP
FIRST_TRADE=pd.Timestamp("2019-01-01",tz="UTC")


def eligible_events(d,b):
    all_events=base.find_setups(b,12)
    eligible=[]
    horizon=d.date.iloc[-1]+pd.Timedelta(days=1)
    for s in all_events:
        if s["kind"]!="SWEEP_MEAN_REVERSION": continue
        if s["signal_closed"] < FIRST_TRADE: continue
        future=d[d.date>=s["signal_closed"]]
        if future.empty: continue
        entry_day=future.iloc[0]
        if entry_day.date+pd.Timedelta(days=36)>horizon: continue
        entry=float(entry_day.open)
        risk=(entry-s["stop"])*s["side"]
        if risk<=0: continue
        if (s["mid"]-entry)*s["side"]<2*risk: continue
        eligible.append(dict(s,entry_date=entry_day.date,entry=entry,risk=risk))
    return eligible


def trade_simulate(d,s,name,hold_days):
    entry=s["entry"]
    risk=s["risk"]
    side=s["side"]
    stop=s["stop"]
    if name=="A_TP_2R":
        target=entry+side*2*risk
    elif name=="B_TP_RANGE_MID":
        target=s["mid"]
    else:
        target=np.nan
    expiry=s["entry_date"]+pd.Timedelta(days=hold_days)
    window=d[(d.date>=s["entry_date"])&(d.date<expiry)]
    if window.empty: raise ValueError("No D1 bars within trade duration")
    exit_day=window.date.iloc[-1]
    exit_price=float(window.close.iloc[-1])
    exit_reason="TIME_EXIT"
    for _,bar in window.iterrows():
        hit_stop=(float(bar.low)<=stop) if side>0 else (float(bar.high)>=stop)
        crossed_stop=(float(bar.open)<stop) if side>0 else (float(bar.open)>stop)
        hit_target=(np.isfinite(target) and
            ((float(bar.high)>=target) if side>0 else (float(bar.low)<=target)))
        if hit_stop:
            exit_day=bar.date
            exit_price=float(bar.open) if crossed_stop else float(stop)
            exit_reason="STOP"
            break
        if hit_target:
            exit_day=bar.date
            exit_price=float(target)
            exit_reason="TARGET"
            break
    net=((exit_price-entry)*side-FEE)/risk
    return dict(
        signal_start=str(s["signal_start"]),signal_closed=str(s["signal_closed"]),
        entry_date=str(s["entry_date"]),exit_date=str(exit_day),
        year=int(s["entry_date"].year),
        side="LONG" if side>0 else "SHORT",
        entry=entry,stop=stop,target=target,
        exit=exit_price,exit_reason=exit_reason,net_R=float(net),
        initial_risk_pips=risk/PIP,
        reference_mid=s["mid"],hold_limit_days=hold_days,
        model=name,
    )


def calc(rows):
    if not rows:
        return dict(trades=0,winrate_pct=np.nan,stop_pct=np.nan,
                    total_R=0.0,avg_R=np.nan,profit_factor=np.nan,
                    max_drawdown_R=0.0)
    values=np.array([x["net_R"] for x in rows],dtype=float)
    gains=values[values>0].sum(); losses=-values[values<0].sum()
    equity=np.r_[0,values.cumsum()]
    return dict(trades=len(rows),
                winrate_pct=round(float((values>0).mean()*100),1),
                stop_pct=round(float(np.mean([x["exit_reason"]=="STOP" for x in rows])*100),1),
                total_R=round(float(values.sum()),2),avg_R=round(float(values.mean()),3),
                profit_factor=round(float(gains/losses),3) if losses>0 else np.nan,
                max_drawdown_R=round(float(np.min(equity-np.maximum.accumulate(equity))),2))


def main():
    summary=[];yearly=[];audits=[]
    for pair in PAIRS:
        d=base.daily_data(base.base.get_data(pair))
        b=base.calendar_bars(d,12)
        events=eligible_events(d,b)
        bench=base.backtest(d,base.find_setups(b,12))
        old=bench[bench.setup=="SWEEP_MEAN_REVERSION"]
        old_r=float(old.net_R.sum()) if not old.empty else 0
        audits.append(dict(pair=pair.upper(),total_valid_closed_12d=int(b.valid.sum()),
                           first_D1=str(d.date.iloc[0]),last_D1=str(d.date.iloc[-1]),
                           qualified_sweep_events=len(events),
                           original_combined_benchmark_n=len(old),
                           original_combined_benchmark_R=round(old_r,2)))
        for mode in ("INDEPENDENT","MATCHED_SIGNALS"):
            for name,days in MODELS:
                rows=[]
                free=pd.Timestamp("2010-01-01",tz="UTC")
                for event in events:
                    if mode=="INDEPENDENT" and event["entry_date"]<free: continue
                    trade=trade_simulate(d,event,name,days)
                    rows.append(trade)
                    if mode=="INDEPENDENT":
                        free=pd.Timestamp(trade["exit_date"])+pd.Timedelta(seconds=1)
                t=pd.DataFrame(rows)
                t.to_csv(OUT/f"{pair.lower()}_{mode.lower()}_{name.lower()}_trades.csv",index=False)
                metrics=calc(rows)
                summary.append(dict(pair=pair.upper(),mode=mode,model=name,**metrics))
                for y in range(2019,datetime.now(timezone.utc).year+1):
                    year_rows=[x for x in rows if x["year"]==y]
                    yearly.append(dict(pair=pair.upper(),mode=mode,model=name,year=y,**calc(year_rows)))
                print(f"{pair.upper()} {mode} {name}: {metrics['trades']} trades "
                      f"{metrics['total_R']}R PF={metrics['profit_factor']}",flush=True)
    pd.DataFrame(summary).to_csv(OUT/"summary.csv",index=False)
    pd.DataFrame(yearly).to_csv(OUT/"yearly_results.csv",index=False)
    pd.DataFrame(audits).to_csv(OUT/"data_audit.csv",index=False)
    holdout=pd.DataFrame(yearly)
    holdout=holdout[holdout.year>=2024].groupby(["pair","mode","model"],as_index=False).agg(
         trades=("trades","sum"),total_R=("total_R","sum"))
    holdout.to_csv(OUT/"holdout_2024_on.csv",index=False)
    print("Done 12D three-model experiment; all outputs under", OUT,flush=True)
    print("Earlier original EURUSD 12D sweep benchmark +5.96R/12 trades was "
          "selected from a combined sweep+breakout strategy. This sweep-only "
          "test may execute different events.",flush=True)
    print("Dukascopy BID D1; no orders; fixed 1.5pip roundtrip; "
          "swap and realistic slippage not modeled.",flush=True)

if __name__=="__main__":
    main()
