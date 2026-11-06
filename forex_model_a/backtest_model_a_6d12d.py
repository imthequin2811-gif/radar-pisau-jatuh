"""Model A Forex: compare CLOSED 6D vs 12D calendar-UTC candles, no CCI.
Dukascopy BID D1 source; not OANDA. Research only: NO orders.
60-calendar-day sweep, 120-calendar-day breakout reference, 36-day max hold.
"""
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import backtest_model_a_forex as base

base.START = '2017-01-01'
RESULTS = Path('model_a_6d12d_results')
RESULTS.mkdir(exist_ok=True)
FIRST_TRADE = pd.Timestamp('2019-01-01', tz='UTC')
TF_LIST = (6, 12)
KINDS = ('ALL', 'SWEEP_MEAN_REVERSION', 'STRONG_BREAKOUT')
HOLD_DAYS = 36
PIP = 0.0001
COST_PIPS = 1.5

def daily_data(raw):
    d = raw.copy()
    d['date'] = pd.to_datetime(d.date, utc=True)
    d = d.sort_values('date').drop_duplicates('date').reset_index(drop=True)
    cols = ['open', 'high', 'low', 'close']
    for c in cols: d[c] = pd.to_numeric(d[c], errors='raise')
    if d[cols].isna().any().any():
        raise ValueError('Missing OHLC')
    if not ((d.high >= d[cols].max(axis=1)) & (d.low <= d[cols].min(axis=1))).all():
        raise ValueError('Invalid OHLC')
    # Exclude weekend D1 rows; never invent or interpolate missing days.
    d = d[(d.date.dt.weekday < 5) & (d.date < pd.Timestamp.now(tz='UTC').normalize())]
    d = d.reset_index(drop=True)
    if len(d) < 400: raise ValueError('Insufficient history')
    return d

def calendar_bars(d, tf):
    last_day = d.date.max().normalize()
    all_bars = []
    for year in range(int(d.date.dt.year.min()), int(d.date.dt.year.max()) + 1):
        start = pd.Timestamp(f'{year}-01-01', tz='UTC')
        new_year = pd.Timestamp(f'{year+1}-01-01', tz='UTC')
        while start < new_year:
            end = min(start + pd.Timedelta(days=tf), new_year)
            block = d[(d.date >= start) & (d.date < end)]
            expected = sum((start + pd.Timedelta(days=i)).weekday() < 5
                           for i in range((end-start).days))
            valid = (end <= last_day + pd.Timedelta(days=1)
                     and len(block) >= max(1, int(np.ceil(0.65 * expected))))
            o,h,l,c = ((float(block.open.iloc[0]), float(block.high.max()),
                        float(block.low.min()), float(block.close.iloc[-1]))
                       if valid else (np.nan,)*4)
            all_bars.append(dict(start=start, end=end, valid=valid,
                                 sessions=len(block), expected_weekdays=expected,
                                 open=o, high=h, low=l, close=c))
            start = end
    b = pd.DataFrame(all_bars)
    for kind, span in [('sweep',60), ('breakout',120)]:
        n = span//tf
        b[f'hi_{kind}'] = b.high.shift(1).rolling(n, min_periods=n).max()
        b[f'lo_{kind}'] = b.low.shift(1).rolling(n, min_periods=n).min()
    return b

def find_setups(b, tf):
    candidates = []
    for _,r in b.iterrows():
        if not r.valid or r.end < FIRST_TRADE: continue
        keys=['hi_sweep','lo_sweep','hi_breakout','lo_breakout']
        if not np.isfinite(r[keys].to_numpy(dtype=float)).all(): continue
        span = float(r.high - r.low)
        if span <= 0: continue
        mid = (r.hi_sweep + r.lo_sweep)/2
        body = abs(r.close-r.open)/span
        kind,side,stop = None,0,None
        if r.low < r.lo_sweep and r.close > r.lo_sweep and r.close < mid:
            kind,side,stop = 'SWEEP_MEAN_REVERSION',1,r.low-2*PIP
        elif r.high > r.hi_sweep and r.close < r.hi_sweep and r.close > mid:
            kind,side,stop = 'SWEEP_MEAN_REVERSION',-1,r.high+2*PIP
        elif r.close > r.hi_breakout and body >= .60 and r.close > r.open:
            kind,side,stop = 'STRONG_BREAKOUT',1,r.low-2*PIP
        elif r.close < r.lo_breakout and body >= .60 and r.close < r.open:
            kind,side,stop = 'STRONG_BREAKOUT',-1,r.high+2*PIP
        if kind:
            candidates.append(dict(kind=kind, side=side, stop=float(stop),
                                   mid=float(mid), signal_closed=r.end,
                                   signal_start=r.start, tf=f'{tf}D'))
    return candidates

def backtest(d, candidates):
    rows = []
    free = pd.Timestamp('2010-01-01',tz='UTC')
    horizon = d.date.iloc[-1]+pd.Timedelta(days=1)
    for s in candidates:
        future = d[d.date>=s['signal_closed']]
        if future.empty: continue
        enter_day = future.date.iloc[0]
        if enter_day < free: continue
        expiry = enter_day + pd.Timedelta(days=HOLD_DAYS)
        if expiry > horizon: continue # no right-censored outcomes
        entry = float(future.open.iloc[0])
        risk = (entry-s['stop'])*s['side']
        if risk<=0: continue
        if s['kind']=='SWEEP_MEAN_REVERSION':
            target=s['mid']
            if (target-entry)*s['side'] < 2*risk: continue
        else: target=entry+s['side']*2*risk
        window=d[(d.date>=enter_day)&(d.date<expiry)]
        if window.empty: continue
        exit_date=window.date.iloc[-1]
        exit_px=float(window.close.iloc[-1])
        reason='TIME_EXIT'
        for _,q in window.iterrows():
            if s['side']==1:
                sl=q.low<=s['stop']
                tp=q.high>=target
                gap=q.open<s['stop']
            else:
                sl=q.high>=s['stop']
                tp=q.low<=target
                gap=q.open>s['stop']
            if sl: # conservatively stop first if both touch
                exit_px=float(q.open) if gap else s['stop']
                exit_date=q.date
                reason='STOP'
                break
            if tp:
                exit_px=target
                exit_date=q.date
                reason='TARGET'
                break
        net_r=(exit_px-entry)*s['side']/risk-COST_PIPS*PIP/risk
        rows.append(dict(tf=s['tf'],setup=s['kind'],side='LONG' if s['side']>0 else 'SHORT',
                         signal_start=s['signal_start'],signal_closed=s['signal_closed'],
                         entry_date=enter_day,entry=entry,stop=s['stop'],target=target,
                         exit_date=exit_date,exit=exit_px,exit_reason=reason,
                         risk=risk,net_R=float(net_r)))
        free=exit_date+pd.Timedelta(seconds=1)
    return pd.DataFrame(rows)

def stats(t):
    if t.empty:
        return dict(trades=0,winrate_pct=np.nan,avg_R=np.nan,total_R=0,
                    profit_factor=np.nan,max_drawdown_R=0)
    r=t.net_R
    win=float(r[r>0].sum())
    loss=float(-r[r<0].sum())
    eq=pd.concat([pd.Series([0.0]),r.cumsum().reset_index(drop=True)],
                 ignore_index=True)
    return dict(trades=len(t), winrate_pct=round(float((r>0).mean()*100),1),
                avg_R=round(float(r.mean()),3),total_R=round(float(r.sum()),2),
                profit_factor=round(win/loss,3) if loss>0 else np.nan,
                max_drawdown_R=round(float((eq-eq.cummax()).min()),2))

def main():
    summary=[]; yearly=[]; audit=[]
    for symbol in base.SYMBOLS:
        d=daily_data(base.get_data(symbol))
        audit.append(dict(pair=symbol.upper(),first_daily=str(d.date.iloc[0]),
                          last_daily=str(d.date.iloc[-1]),weekday_bars=len(d)))
        for tf in TF_LIST:
            b=calendar_bars(d,tf)
            b.to_csv(RESULTS/f'{symbol}_{tf}d_bars.csv',index=False)
            c=find_setups(b,tf)
            t=backtest(d,c)
            t.to_csv(RESULTS/f'{symbol}_{tf}d_trades.csv',index=False)
            for kind in KINDS:
                subset=t if kind=='ALL' or t.empty else t[t.setup==kind]
                summary.append(dict(pair=symbol.upper(),tf=f'{tf}D',setup=kind,
                                    **stats(subset)))
                for y in range(2019,datetime.now(timezone.utc).year+1):
                    yy=subset if subset.empty else subset[subset.entry_date.dt.year==y]
                    yearly.append(dict(pair=symbol.upper(),tf=f'{tf}D',
                                       year=y,setup=kind,**stats(yy)))
            print(f'{symbol.upper()} {tf}D bars={len(b)} valid={b.valid.sum()} '
                  f'candidates={len(c)} trades={len(t)}',flush=True)
    pd.DataFrame(summary).to_csv(RESULTS/'summary.csv',index=False)
    pd.DataFrame(yearly).to_csv(RESULTS/'yearly_results.csv',index=False)
    pd.DataFrame(audit).to_csv(RESULTS/'data_audit.csv',index=False)
    print(pd.DataFrame(summary).to_string(index=False),flush=True)
    print('Dukascopy BID D1; 6D/12D calendar UTC reset Jan1, CLOSED bars only. '
          'Backtest, not trade signal. Fee assumption 1.5 pips.',flush=True)

if __name__=='__main__': main()
