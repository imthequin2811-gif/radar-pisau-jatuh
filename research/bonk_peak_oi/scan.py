import os,json,csv,time,datetime as dt,urllib.request as U,urllib.parse as P,urllib.error as E
from collections import defaultdict
from pathlib import Path
O=Path('research/bonk_peak_oi');O.mkdir(parents=True,exist_ok=True)
START=dt.datetime(2026,3,1,tzinfo=dt.timezone.utc); NOW=dt.datetime.now(dt.timezone.utc)
KEY=os.environ.get('COINALYZE_API_KEY','');ERR=[];DETAIL={}
def req(base,params={},auth=False):
 url=base+'?'+P.urlencode(params)
 headers={'Accept':'application/json','User-Agent':'ResearchScan/1.0'}
 if auth:headers['api_key']=KEY
 for i in range(6):
  try:
   with U.urlopen(U.Request(url,headers=headers),timeout=50) as r:return json.load(r)
  except E.HTTPError as e:
   if e.code==429 and i<5:time.sleep(min(60,int(e.headers.get('Retry-After') or 2**i+3)));continue
   if e.code>=500 and i<4:time.sleep(2**i+2);continue
   raise
  except Exception:
   if i<3:time.sleep(2**i+2);continue
   raise
def quote(x):
 q=x.get('quote') or {}
 return next((v for v in q if v.get('symbol')=='USD'),q[0] if q else {}) if isinstance(q,list) else q.get('USD',q)
cmc=[]
try:
 data=req('https://pro-api.coinmarketcap.com/public-api/v3/cryptocurrency/listings/latest',{'start':1,'limit':2000,'convert':'USD'});cmc=data.get('data',[])
except Exception as e:ERR.append('CMC: '+str(e)[:200])
by=defaultdict(list);C=[]
for x in cmc:
 s=str(x.get('symbol') or '').upper();by[s].append(x)
 d=str(x.get('date_added') or '')[:10];q=quote(x)
 if '2026-03-01'<=d<=NOW.strftime('%Y-%m-%d') and float(q.get('volume_24h') or 0)>=500000 and float(q.get('market_cap') or 0)<3e9 and s not in ('USDT','USDC','DAI','FDUSD'):C.append(x)
C.sort(key=lambda x:float(quote(x).get('volume_24h') or 0),reverse=True)
coins={str(x['symbol']).upper():x for x in C[:55]}
for s in ['PONS','CASHCAT','MARSCOIN','BTW']:
 if by[s]:coins[s]=max(by[s],key=lambda x:float(quote(x).get('volume_24h') or 0))
markets=[]
try:markets=req('https://api.coinalyze.net/v1/future-markets',auth=True)
except Exception as e:ERR.append('Coinalyze market catalogue: '+str(e)[:200])
if not cmc:
 for s in ['PONS','CASHCAT','MARSCOIN','BTW']:coins.setdefault(s,{'symbol':s,'name':s})
M=defaultdict(list)
for m in markets:
 s=str(m.get('base_asset') or '').upper()
 if s in coins and m.get('is_perpetual') and str(m.get('quote_asset')).upper() in ('USD','USDT','USDC','BUSD'):M[s].append(m)
selected=[]
for s,ls in M.items():
 ls.sort(key=lambda m: {'3':0,'A':1,'B':2}.get(str(m.get('exchange')),3))
 selected+=ls[:8]
S={};froms=int(START.timestamp());tos=int(NOW.timestamp())
for i in range(0,len(selected),15):
 chunk=selected[i:i+15];codes=[m['symbol'] for m in chunk]
 try:
  d=req('https://api.coinalyze.net/v1/open-interest-history',{'symbols':','.join(codes),'interval':'6hour','from':froms,'to':tos,'convert_to_usd':'true'},auth=True)
  for item in d:S[item['symbol']]={int(p['t']):p for p in item.get('history',[]) if p.get('c') is not None}
 except Exception as e:ERR.append('OI '+','.join(codes[:3])+': '+str(e)[:140])
 time.sleep(27)
rows=[]
for s,x in coins.items():
 q=quote(x);p=defaultdict(float);upper=defaultdict(float);one=0
 for m in M.get(s,[])[:8]:
  for t,b in S.get(m['symbol'],{}).items():
   p[t]+=float(b.get('c') or 0);upper[t]+=float(b.get('h') or 0);one=max(one,float(b.get('h') or 0))
 top=max(p,key=p.get) if p else None;val=p.get(top,0);hi=max(upper.values()) if upper else 0
 d=str(x.get('date_added') or '')[:10]
 status='PASS_PEAK_100M' if max(one,val)>=1e8 else ('POSSIBLE_INTRABAR' if hi>=1e8 else 'NOT_PROVEN')
 if not d or d<'2026-03-01':status='DATE_UNVERIFIED'
 rows.append({'symbol':s,'name':x.get('name',''),'cmc_date_added':d,'cmc_slug':x.get('slug',''),
 'market_cap_usd':round(float(q.get('market_cap') or 0)), 'volume24h_usd':round(float(q.get('volume_24h') or 0)),
 'peak_6h_close_aggregated_usd':round(val),'peak_6h_utc':dt.datetime.fromtimestamp(top,dt.timezone.utc).isoformat() if top else '',
 'sum_6h_contract_high_upper_bound_usd':round(hi),'single_contract_peak_high_usd':round(one),
 'contracts_with_history':sum(m['symbol'] in S for m in M.get(s,[])[:8]),'contracts_selected':min(8,len(M.get(s,[]))), 'status':status})
rows.sort(key=lambda x:(x['status']!='PASS_PEAK_100M',-x['peak_6h_close_aggregated_usd']))
with open(O/'results.csv','w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['symbol','status']);w.writeheader();w.writerows(rows)
fmt=lambda n: '%.1fM'%(n/1e6)
lines=['# Calon BONK sejak Maret 2026 — peak OI historis','',f'Generated: {NOW.isoformat()}',
 'Sumber: CoinMarketCap keyless listings + Coinalyze open-interest-history 6hour USD.',
 '**PASS** hanya untuk puncak OI yang dibuktikan oleh snapshot penutupan 6H agregat, atau high 6H satu kontrak.',
 '**POSSIBLE_INTRABAR** adalah jumlah high tiap kontrak tanpa sinkronisasi menit, sehingga belum terbukti.',
 'Tanggal CMC date_added tidak selalu sama dengan tanggal launch sebenarnya.',
 'Cakupan maksimal 8 kontrak per token dan 55 token dengan volume tertinggi; hasil negatif bukan bukti belum pernah mencapai ambang.',
 '', '| Token | Date CMC | Cap | Vol24h | Max OI close 6H | Tanggal Peak | Status |','|---|---|---:|---:|---:|---|---|']
for r in rows[:60]:
 url='https://coinmarketcap.com/currencies/'+str(r['cmc_slug'] or r['symbol'].lower())+'/'
 lines.append('| [{symbol}]({url}) | {date} | {cap} | {vol} | {peak} | {when} | {status} |'.format(symbol=r['symbol'],url=url,date=r['cmc_date_added'],cap=fmt(r['market_cap_usd']),vol=fmt(r['volume24h_usd']),peak=fmt(r['peak_6h_close_aggregated_usd']),when=r['peak_6h_utc'][:10],status=r['status']))
if ERR:lines+=['','## Data issues']+['- '+e for e in ERR]
(O/'results.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
d={'utc':NOW.isoformat(),'cmc_count':len(cmc),'cmc_candidates':len(C),'scan_assets':len(coins),'contracts_selected':len(selected),'contracts_returned':len(S),'passes':sum(r['status']=='PASS_PEAK_100M' for r in rows),'errors':ERR}
(O/'diagnostics.json').write_text(json.dumps(d,indent=2),encoding='utf8');print(json.dumps(d,indent=2))
