"""Model A Forex independent research backtest. Run: pip install pandas numpy requests; python backtest_model_a_forex.py
Data: Stooq D1, not TradingView OANDA. Daily sessions depend on provider; 4D custom not inferred.
Rules fixed before testing. Results are exploratory, not verified trading advice.
"""
import io
from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import requests

START='2019-01-01'; END=(datetime.now(timezone.utc)-timedelta(days=1)).strftime('%Y-%m-%d')
SYMBOLS=('eurusd','gbpusd','usdchf')
FEE_PIPS=1.5   # all-in assumed roundtrip spread/slippage; sensitivity test this
PIP=0.0001
HOLD=12
SWEEP_LOOKBACK=10
BREAKOUT_LOOKBACK=20
REPORT_DIR=Path('model_a_results')
REPORT_DIR.mkdir(exist_ok=True)

def get_data(symbol):
    url='https://stooq.com/q/d/l/'
    params={'s':symbol,'i':'d','d1':START.replace('-',''),'d2':END.replace('-','')}
    r=requests.get(url,params=params,timeout=40,headers={'User-Agent':'Mozilla/5.0'})
    r.raise_for_status()
    if not r.text.startswith('Date,'):
        raise ValueError(f'{symbol}: feed not valid CSV: {r.text[:120]}')
    df=pd.read_csv(io.StringIO(r.text))
    df.columns=[c.lower() for c in df.columns]
    df['date']=pd.to_datetime(df['date'],utc=True)
    df=df.sort_values('date').drop_duplicates('date').reset_index(drop=True)
    for c in ['open','high','low','close']:
        df[c]=pd.to_numeric(df[c],errors='raise')
    assert df[['open','high','low','close']].notna().all().all()
    assert ((df.high>=df[['open','close','low']].max(axis=1)) & (df.low<=df[['open','close']].min(axis=1))).all()
    if len(df)<200: raise ValueError('Insufficient history')
    return df

def signals(df):
    d=df.copy()
    for n in (SWEEP_LOOKBACK,BREAKOUT_LOOKBACK):
        d[f'hi{n}']=d.high.shift(1).rolling(n).max()
        d[f'lo{n}']=d.low.shift(1).rolling(n).min()
    d['body']=(d.close-d.open).abs()/(d.high-d.low).replace(0,np.nan)
    d['mid10']=(d.hi10+d.lo10)/2
    out=[]
    for i in range(21,len(d)-1):
        b=d.iloc[i]; nxt=d.iloc[i+1]
        if pd.isna(b.hi20) or pd.isna(b.lo20): continue
        kind=None; side=0; stop=None; target=None
        # Reclaim prior 10-session liquidity and expect reversion to prior range midpoint.
        if b.low < b.lo10 and b.close > b.lo10 and b.close < b.mid10:
            kind='SWEEP_MEAN_REVERSION';side=1;stop=b.low-2*PIP
        elif b.high > b.hi10 and b.close < b.hi10 and b.close > b.mid10:
            kind='SWEEP_MEAN_REVERSION';side=-1;stop=b.high+2*PIP
        # Strong breakout defined by close outside previous 20-day range and candle body >=60% range.
        elif b.close > b.hi20 and b.body >= .60 and b.close>b.open:
            kind='STRONG_BREAKOUT';side=1;stop=b.low-2*PIP
        elif b.close < b.lo20 and b.body >= .60 and b.close<b.open:
            kind='STRONG_BREAKOUT';side=-1;stop=b.high+2*PIP
        if kind is None:continue
        entry=float(nxt.open)
        risk=(entry-stop)*side
        if risk<=0:continue
        if kind=='SWEEP_MEAN_REVERSION':
            target=float(b.mid10)
            if (target-entry)*side < 2*risk:continue  # 2R min for actual midpoint target
        else:
            target=entry+side*2*risk
        out.append({'idx':i+1,'signal_date':str(b.date.date()),'entry_date':str(nxt.date.date()),
                    'setup':kind,'side':'LONG' if side>0 else 'SHORT','sign':side,
                    'entry':entry,'stop':float(stop),'target':float(target),'risk':risk})
    return out

def simulate(df,candidates):
    trades=[]; free_idx=0
    for s in candidates:
        i=s['idx']
        if i<=free_idx:continue
        outcome='TIME_EXIT'; exit_idx=min(i+HOLD-1,len(df)-1)
        exit_px=float(df.iloc[exit_idx].close)
        for k in range(i, min(i+HOLD,len(df))):
            bar=df.iloc[k]
            stop_hit=bar.low<=s['stop'] if s['sign']==1 else bar.high>=s['stop']
            tp_hit=bar.high>=s['target'] if s['sign']==1 else bar.low<=s['target']
            if stop_hit or tp_hit:
                # Daily OHLC can't resolve intrabar order: if both hit, pessimistically record STOP.
                outcome='STOP' if stop_hit else 'TARGET'
                exit_px=s['stop'] if stop_hit else s['target']
                # If a gap opens beyond stop, use worse open fill; target assumes target-only fill.
                if stop_hit and (float(bar.open)-s['stop'])*s['sign']<0: exit_px=float(bar.open)
                exit_idx=k
                break
        gross_r=(exit_px-s['entry'])*s['sign']/s['risk']
        net_r=gross_r-FEE_PIPS*PIP/s['risk']
        trades.append({**{k:v for k,v in s.items() if k not in ('idx','sign')},
                       'exit_date':str(df.iloc[exit_idx].date.date()),'exit':exit_px,
                       'exit_reason':outcome,'gross_R':gross_r,'net_R':net_r})
        free_idx=exit_idx
    return pd.DataFrame(trades)

def stats(t):
    if t.empty:return {'trades':0,'winrate_pct':np.nan,'avg_R':np.nan,'total_R':np.nan,'max_drawdown_R':np.nan,'profit_factor':np.nan}
    r=t.net_R
    equity=r.cumsum(); dd=equity-equity.cummax().clip(lower=0)
    wins=r[r>0].sum(); loss=-r[r<0].sum()
    return {'trades':len(t),'winrate_pct':round((r>0).mean()*100,1),'avg_R':round(r.mean(),3),
            'total_R':round(r.sum(),2),'max_drawdown_R':round(dd.min(),2),
            'profit_factor':round(wins/loss,3) if loss>0 else np.nan}

def main():
    summary=[]
    for symbol in SYMBOLS:
        d=get_data(symbol)
        print(f'{symbol}: {len(d)} bars, {d.date.iloc[0].date()} through {d.date.iloc[-1].date()}')
        tr=simulate(d,signals(d));tr.insert(0,'symbol',symbol.upper()) if not tr.empty else None
        tr.to_csv(REPORT_DIR/f'{symbol}_trades.csv',index=False)
        for segment,mask in [('ALL',pd.Series(True,index=tr.index)),
                              ('TRAIN_TO_2023',tr.entry_date<'2024-01-01' if not tr.empty else pd.Series(dtype=bool)),
                              ('HOLDOUT_2024_ON',tr.entry_date>='2024-01-01' if not tr.empty else pd.Series(dtype=bool))]:
            sub=tr[mask]; rec={'pair':symbol.upper(),'sample':segment,'setup':'ALL',**stats(sub)};summary.append(rec)
            if not sub.empty:
                for setup,one in sub.groupby('setup'):
                    summary.append({'pair':symbol.upper(),'sample':segment,'setup':setup,**stats(one)})
    pd.DataFrame(summary).to_csv(REPORT_DIR/'summary.csv',index=False)
    print(pd.DataFrame(summary).to_string(index=False))
    print('Results saved to',REPORT_DIR.resolve())
    print('CAVEATS: D1 Stooq (not OANDA); fixed 1.5-pip costs; daily OHLC ambiguous bar pessimistic; no swap; no position sizing; provider bar timezone may differ.')

if __name__=='__main__':main()
