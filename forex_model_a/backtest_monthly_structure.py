"""Pure monthly structure Forex backtest: exactly one entry at first trading D1 open
of each completed UTC calendar month. Last two CLOSED months only.
No CCI, WMA, sweep, mean reversion, or breakout filters.
Source Dukascopy BID D1 (not OANDA). Backtest only; no orders.
"""
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import backtest_model_a_forex as base

base.START = "2017-01-01"
START_YEAR = 2019
PIP = 0.0001
ASSUMED_COST_PIPS = 1.5
BUFFER_PCT = 0.10
RR_TARGETS = (1.5, 2.0)
RESULTS = Path("monthly_structure_results")
RESULTS.mkdir(exist_ok=True)

def clean_daily(source):
    d=source.copy()
    d["date"]=pd.to_datetime(d["date"],utc=True)
    d=d.sort_values("date").drop_duplicates("date")
    d=d[(d.date.dt.dayofweek<5)&(d.date<pd.Timestamp.now(tz="UTC").normalize())].copy()
    d["month"]=d.date.dt.tz_localize(None).dt.to_period("M")
    if d.empty: raise ValueError("No valid D1 prices")
    if d[["open","high","low","close"]].isna().any().any():
        raise ValueError("Missing daily OHLC values")
    if not ((d.high>=d[["open","close","low"]].max(axis=1))&
            (d.low<=d[["open","close"]].min(axis=1))).all():
        raise ValueError("Daily OHLC inconsistency")
    return d

def monthly(d):
    m=d.groupby("month",sort=True).agg(
        open=("open","first"),high=("high","max"),low=("low","min"),
        close=("close","last"),sessions=("close","size"),
        first_session=("date","first"),last_session=("date","last")
    )
    # Avoid mistaken monthly candles from patchy data.
    m["expected_weekdays"]=[
        sum((p.start_time+pd.Timedelta(days=i)).weekday()<5
            for i in range(p.days_in_month)) for p in m.index
    ]
    m["valid"]=(m.sessions>=np.ceil(0.7*m.expected_weekdays))
    return m

def direction(last,prior):
    if last.high>prior.high and last.low>prior.low:
        return 1,"HH_HL"
    if last.high<prior.high and last.low<prior.low:
        return -1,"LH_LL"
    if last.close>prior.close:
        return 1,"MIXED_CLOSE_HIGHER"
    if last.close<prior.close:
        return -1,"MIXED_CLOSE_LOWER"
    return (1,"MIXED_TIE_BULLISH_BODY") if last.close>=last.open else (-1,"MIXED_TIE_BEARISH_BODY")

def simulate_month(day_rows, prev, prevprev, month, rr):
    sign,reason=direction(prev,prevprev)
    entry_day=day_rows.iloc[0]
    entry=float(entry_day.open)
    width=float(prev.high-prev.low)
    if not np.isfinite(width) or width<=0: raise ValueError("Zero monthly range")
    # Monthly prior extreme is the anchor. Secondary gap protection ensures
    # stop is always on the correct side of the month-start entry.
    stop=(min(float(prev.low),entry-0.35*width)-BUFFER_PCT*width
          if sign==1 else
          max(float(prev.high),entry+0.35*width)+BUFFER_PCT*width)
    risk=(entry-stop)*sign
    if risk<=0: raise ValueError("Nonpositive initial risk")
    tp=entry+sign*rr*risk
    fill=float(day_rows.iloc[-1].close)
    exit_time=day_rows.iloc[-1].date
    exit_kind="MONTH_END"
    for _,day in day_rows.iterrows():
        if sign==1:
            hit_stop=(float(day.low)<=stop)
            hit_tp=(float(day.high)>=tp)
            crossed_at_open=(float(day.open)<stop)
        else:
            hit_stop=(float(day.high)>=stop)
            hit_tp=(float(day.low)<=tp)
            crossed_at_open=(float(day.open)>stop)
        # Same-day stop and target: pessimistically assume SL touched first.
        if hit_stop:
            fill=float(day.open) if crossed_at_open else stop
            exit_time=day.date; exit_kind="STOP"
            break
        if hit_tp:
            fill=tp; exit_time=day.date; exit_kind="TARGET"
            break
    gross=(fill-entry)*sign/risk
    net=gross-ASSUMED_COST_PIPS*PIP/risk
    return dict(year=month.year,month=str(month),
       previous_closed_month=str(month-1),structure=reason,
       direction="LONG" if sign==1 else "SHORT",rr_target=rr,
       prev_month_high=float(prev.high),prev_month_low=float(prev.low),
       prev_month_close=float(prev.close),
       entry_date=str(entry_day.date),entry=entry,sl=stop,tp=tp,
       initial_risk_pips=risk/PIP,
       exit_date=str(exit_time),exit=fill,exit_reason=exit_kind,
       net_R=float(net))

def performance(df):
    if df.empty:
        return dict(trades=0,winrate_pct=np.nan,total_R=0.0,
                    avg_R=np.nan,profit_factor=np.nan,max_drawdown_R=0.0)
    r=df.net_R.reset_index(drop=True)
    profit=float(r[r>0].sum())
    loss=float(-r[r<0].sum())
    equity=pd.concat([pd.Series([0.0]),r.cumsum()],ignore_index=True)
    return dict(trades=len(r),winrate_pct=round((r>0).mean()*100,1),
                total_R=round(r.sum(),2),avg_R=round(r.mean(),3),
                profit_factor=round(profit/loss,3) if loss>0 else np.nan,
                max_drawdown_R=round((equity-equity.cummax()).min(),2))

def main():
    summary=[];annual=[];latest=[];audit=[]
    this_month=pd.Timestamp.now(tz="UTC").tz_localize(None).to_period("M")
    for pair in base.SYMBOLS:
        d=clean_daily(base.get_data(pair))
        m=monthly(d)
        audit.append(dict(pair=pair.upper(),first_d1=str(d.date.iloc[0]),
                          last_d1=str(d.date.iloc[-1]),
                          months=len(m),invalid_months=int((~m.valid).sum())))
        for rr in RR_TARGETS:
            trades=[]
            for mo in m.index:
                if mo.year<START_YEAR or mo>=this_month: continue
                if mo-1 not in m.index or mo-2 not in m.index:
                    continue
                if not (m.loc[mo,"valid"] and m.loc[mo-1,"valid"]
                        and m.loc[mo-2,"valid"]):
                    # Strictly refuse month with missing OHLC history.
                    continue
                rows=d[d.month==mo]
                trades.append(simulate_month(rows,m.loc[mo-1],m.loc[mo-2],mo,rr))
            t=pd.DataFrame(trades)
            t.to_csv(RESULTS/f"{pair}_tp{str(rr).replace('.','_')}_trades.csv",index=False)
            summary.append(dict(pair=pair.upper(),rr_target=rr,**performance(t)))
            for y in range(START_YEAR,datetime.now(timezone.utc).year+1):
                yy=t[t.year==y] if not t.empty else t
                annual.append(dict(pair=pair.upper(),rr_target=rr,year=y,
                                   **performance(yy)))
            if not t.empty:
                last=t.iloc[-1].to_dict()
                latest.append(dict(pair=pair.upper(),rr_target=rr,**last))
            print(f"{pair.upper()} target={rr}R months={len(t)} "
                  f"total={performance(t)['total_R']}R",flush=True)
    pd.DataFrame(summary).to_csv(RESULTS/"summary.csv",index=False)
    pd.DataFrame(annual).to_csv(RESULTS/"yearly_results.csv",index=False)
    pd.DataFrame(latest).to_csv(RESULTS/"last_completed_month.csv",index=False)
    pd.DataFrame(audit).to_csv(RESULTS/"data_audit.csv",index=False)
    print(pd.DataFrame(summary).to_string(index=False))
    print("Dukascopy BID D1; 1 trade every VALID completed UTC calendar month; "
          "structure from 2 previous CLOSED months; SL prior-month extremum + 10% range; "
          "fixed TP 1.5R or 2R; end-of-month time exit. "
          "Assumed cost 1.5pip; swap/slippage not modeled; NOT orders.",flush=True)

if __name__=="__main__":
    main()
