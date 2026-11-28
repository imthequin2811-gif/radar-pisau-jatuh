"""Free-only LAB15 data collector. No trading, no paid API. Raw downloads stay local."""
import argparse, datetime as dt, io, json, math, os, tempfile, urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd

ROOT = Path(__file__).resolve().parent
START = '2015-01-01'
AUDIT_START = '2018-01-01'
NY = ZoneInfo('America/New_York')
OWN = 'https://raw.githubusercontent.com/imthequin2811-gif/radar-pisau-jatuh/main/data/tqqq_radar/market-data.json'
MEMBERS = 'https://raw.githubusercontent.com/floyds1995/Auto-Index-Constituents-Tracker/main/NDX100/Nasdaq%20100%20Historical%20Components%20%26%20Changes.csv'
FRED = {'NDXE':'NASDAQNDXE','VXN':'VXNCLS','VIX_FRED':'VIXCLS','NDX':'NASDAQ100'}
OHLC = ['open','high','low','close']

def get(url):
    req = urllib.request.Request(url,headers={'User-Agent':'LAB15 personal research'})
    with urllib.request.urlopen(req, timeout=35) as r: return r.read().decode('utf-8-sig')

def atomic(path, text):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='') as f: f.write(text)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def normalize(df, ohlc=False, breadth=False):
    df=df.copy()
    df.index=pd.DatetimeIndex(pd.to_datetime(df.index,errors='raise')).tz_localize(None).normalize()
    if df.index.has_duplicates: raise ValueError('duplicate date')
    df=df.sort_index()
    cols=OHLC if ohlc else ['close']
    for c in cols: df[c]=pd.to_numeric(df[c],errors='raise')
    if df.empty or not df[cols].map(math.isfinite).all().all(): raise ValueError('empty/non-finite price')
    if breadth:
        if ((df[cols]<0)|(df[cols]>100)).any().any(): raise ValueError('breadth outside 0..100')
    elif (df[cols]<=0).any().any(): raise ValueError('nonpositive price')
    if ohlc and ((df.high+1e-8<df[['open','low','close']].max(axis=1))|(df.low-1e-8>df[['open','high','close']].min(axis=1))).any(): raise ValueError('invalid OHLC')
    df.index.name='date'
    return df

def sessions(now):
    import pandas_market_calendars as mcal
    cal=mcal.get_calendar('NASDAQ')
    sched=cal.schedule(start_date=START,end_date=now.astimezone(NY).date())
    return pd.DatetimeIndex(sched.index[sched.market_close<=pd.Timestamp(now)-pd.Timedelta(minutes=15)]).tz_localize(None)

def coverage(df, days):
    target=days[days>=AUDIT_START]
    missing=target.difference(df.index)
    extra=df.index[df.index>=AUDIT_START].difference(target)
    return {'rows':len(df),'first':str(df.index.min().date()),'last':str(df.index.max().date()),'expected':len(target),'missing':len(missing),'missing_recent':[str(x.date()) for x in missing[-8:]],'extra':len(extra),'coverage_complete':not len(missing),'calendar':'NASDAQ regular sessions, provider availability still needs audit'}

def persist(path, df, ohlc=False, breadth=False):
    df=normalize(df,ohlc,breadth)
    if path.exists():
        old=normalize(pd.read_csv(path,index_col='date'),ohlc,breadth)
        if len(old.index.difference(df.index)):
            raise ValueError('new snapshot drops existing dates; old file retained')
        shared=old.index.intersection(df.index)
        cols=OHLC if ohlc else ['close']
        den=old.loc[shared,cols].abs().clip(lower=0.01)
        delta=((df.loc[shared,cols]-old.loc[shared,cols]).abs()/den).max().max()
        if delta>0.02:
            atomic(path.with_suffix('.candidate.csv'),df.to_csv())
            raise ValueError('material revisions >2%; review candidate; old file retained')
    atomic(path,df.to_csv())
    return df

def yahoo(ticker,days):
    import yfinance as yf
    end=(days[-1]+pd.Timedelta(days=1)).date().isoformat()
    df=yf.download(ticker,start=START,end=end,interval='1d',auto_adjust=False,actions=True,threads=False,progress=False,multi_level_index=False,timeout=20)
    if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
    df=df.rename(columns=lambda x:str(x).lower().replace(' ','_'))
    cols=OHLC+['adj_close','volume','dividends','stock_splits']
    if any(c not in df for c in cols): raise ValueError('required price/action fields missing')
    df=df[cols]; df.index=pd.DatetimeIndex(df.index).tz_localize(None).normalize()
    return normalize(df.loc[df.index.intersection(days)],True)

def fred(series,days):
    df=pd.read_csv(io.StringIO(get('https://fred.stlouisfed.org/graph/fredgraph.csv?id='+series)),index_col=0,na_values=['.'])
    if series not in df: raise ValueError('unexpected FRED series')
    df=df[[series]].rename(columns={series:'close'}).dropna();df.index=pd.to_datetime(df.index)
    return normalize(df.loc[df.index.intersection(days)])

def own_ndth(days):
    checkout=ROOT.parents[1]/'data/tqqq_radar/market-data.json' if len(ROOT.parents)>1 else Path('missing')
    j=json.loads(checkout.read_text(encoding='utf-8') if checkout.is_file() else get(OWN)); a=j['assets']['NDTH']
    if a.get('isProxy') is not False or not a.get('historyArchive'): raise ValueError('NDTH provenance not verified')
    df=normalize(pd.DataFrame(a['rows']).set_index('date'),True,True)
    return df.loc[df.index.intersection(days)]

def breadth_candidate(prices,membership,days,window):
    valid=prices.notna().rolling(window,min_periods=window).sum()==window
    above=(prices>prices.rolling(window,min_periods=window).mean())&valid
    out=[]
    for day in days:
        if day<membership.index[0] or day>membership.index[-1]: continue
        effective=membership.index[membership.index.searchsorted(day,side='right')-1]
        members=membership.loc[effective]; n=len(members)
        if day not in valid.index or not n: continue
        v=valid.reindex(columns=members,fill_value=False).loc[day]; count=int(v.sum())
        result=float(100*above.reindex(columns=members,fill_value=False).loc[day].sum()/n) if count==n else None
        out.append({'date':day.date().isoformat(),'membership_effective':effective.date().isoformat(),'n':n,'valid':count,'candidate_close':result})
    return pd.DataFrame(out)

def reconstruct(cache,days):
    raw=pd.read_csv(io.StringIO(get(MEMBERS))); raw['date']=pd.to_datetime(raw.date)
    if raw.date.duplicated().any(): raise ValueError('duplicate membership dates')
    members=raw.set_index('date').sort_index().tickers.map(lambda x:sorted(set(str(x).split(','))))
    members=members.loc[members.index>=members.index[members.index.searchsorted(pd.Timestamp(START),side='right')-1]]
    union=sorted(set().union(*members)); prices={}; failures={}
    for ticker in union:
        if not ticker or not all(c.isalnum() or c in '.-' for c in ticker): continue
        try: prices[ticker]=persist(cache/'members'/f'{ticker}.csv',yahoo(ticker,days),True).close.reindex(days)
        except Exception as e: failures[ticker]=str(e)[:240]
    p=pd.DataFrame(prices,index=days); result={}
    for window,name in [(50,'NDFI_RECON'),(100,'NDOH_RECON'),(200,'NDTH_RECON')]:
        b=breadth_candidate(p,members,days[days>=AUDIT_START],window)
        atomic(cache/f'{name}.csv',b.to_csv(index=False)); result[name]={'rows':len(b),'fully_covered':int(b.candidate_close.notna().sum()) if len(b) else 0,'status':'RESEARCH_ONLY_MEMBERSHIP_UNVERIFIED','membership_last':str(members.index[-1].date()),'missing_tickers':len(failures),'source':MEMBERS}
    return result

def run(args):
    now=dt.datetime.now(dt.timezone.utc); days=sessions(now); cache=Path(args.cache)
    report={'version':'C002E','generated_utc':now.isoformat(),'latest_expected_session':str(days[-1].date()),'assets':{},'backtest':'BLOCKED_NO_PROFIT_CLAIM','calendar_lock':'C002C unchanged; exchange sessions only validate source data, not indicator anchors'}
    def record(name,loader,ohlc=False,breadth=False,source=''):
        path=cache/f'{name}.csv'
        try:
            df=persist(path,loader(),ohlc,breadth); c=coverage(df,days); c['status']='COVERAGE_OK' if c['coverage_complete'] else 'GAPS_OR_STALE'
        except Exception as e:
            c={'status':'ERROR_OLD_DATA_RETAINED','error':str(e)[:300]}
            if path.exists():
                try:c.update(coverage(normalize(pd.read_csv(path,index_col='date'),ohlc,breadth),days))
                except Exception:pass
        report['assets'][name]={**c,'type':'OHLC' if ohlc else 'CLOSE_ONLY','source':source}
    record('NDTH',lambda:own_ndth(days),True,True,OWN)
    for t in ('TQQQ','SQQQ','QQQ'): record(t,lambda t=t:yahoo(t,days),True,False,'Yahoo Finance via yfinance')
    for t,s in FRED.items():record(t,lambda s=s:fred(s,days),source='FRED '+s)
    if args.reconstruct:
        try:report['assets'].update(reconstruct(cache,days))
        except Exception as e:report['reconstruction_error']=str(e)[:300]
    else:report['reconstruction_status']='manual optional --reconstruct; not validated'
    atomic(Path(args.status),json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps(report,indent=2,ensure_ascii=False))

def self_test():
    d=pd.date_range('2020-01-01',periods=5); p=pd.DataFrame({'A':[1,2,3,4,5],'B':[2,3,4,None,5]},index=d)
    m=pd.Series([['A'],['A','B']],index=[d[0],d[3]])
    b=breadth_candidate(p,m,d,2)
    assert list(b.valid)==[0,1,1,1]
    assert b.candidate_close.iloc[1]==100 and pd.isna(b.candidate_close.iloc[-1])
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'test.csv'; a=pd.DataFrame({'close':[1.,2.]},index=d[:2]); persist(path,a)
        try:persist(path,a.iloc[1:]);raise AssertionError('truncation not rejected')
        except ValueError:pass
        assert len(pd.read_csv(path))==2
        try:normalize(pd.DataFrame({'open':[5],'high':[4],'low':[1],'close':[2]},index=d[:1]),True);raise AssertionError('OHLC not rejected')
        except ValueError:pass
    print('PASS: candidate membership, missing prices, no future extrapolation, preserve history, OHLC')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--cache',default=str(ROOT/'local_data'));ap.add_argument('--status',default=str(ROOT/'status.json'));ap.add_argument('--reconstruct',action='store_true');ap.add_argument('--self-test',action='store_true');a=ap.parse_args()
    self_test() if a.self_test else run(a)
