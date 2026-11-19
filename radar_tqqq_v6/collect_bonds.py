"""Daily Treasury par yields. Preserve missing tenors; never synthesize yields."""
import argparse, concurrent.futures, csv, datetime as dt, io, json, math, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo
KEYS=['2Y','3Y','5Y','7Y','10Y','20Y','30Y']
NS={'m':'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'}
URL='https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value='
SOURCE='https://home.treasury.gov/treasury-daily-interest-rate-xml-feed'
UTC=dt.timezone.utc

def parse(text,year,now):
    local=now.astimezone(ZoneInfo('America/New_York'));out=[]
    for p in ET.fromstring(text).findall('.//m:properties',NS):
        fields={c.tag.split('}')[-1]:c.text for c in p};date=dt.date.fromisoformat(fields['NEW_DATE'][:10])
        if date.year!=year:raise ValueError('Unexpected year in Treasury response')
        if date>local.date() or (date==local.date() and local.hour<18):continue
        vals=[]
        for k in KEYS:
            raw=fields.get('BC_'+k[:-1]+'YEAR')
            value=None if raw is None or raw.strip()=='' else float(raw)
            if value is not None and (not math.isfinite(value) or not 0<=value<=100):raise ValueError('Invalid Treasury yield')
            vals.append(value)
        if any(v is not None for v in vals):out.append([date.isoformat(),*vals])
    if not out:raise ValueError('No completed Treasury observations')
    if len({r[0] for r in out})!=len(out):raise ValueError('Duplicate Treasury dates')
    return sorted(out)

def fetch(year,now):
    req=urllib.request.Request(URL+str(year),headers={'User-Agent':'RadarTQQQ public Treasury research'})
    with urllib.request.urlopen(req,timeout=25) as r:return parse(r.read(),year,now)

def seed_csv(path):
    return [[r['date'],*[None if r[k]=='' else float(r[k]) for k in KEYS]] for r in csv.DictReader(path.open())]

def collect(path,full=False,seed=None):
    now=dt.datetime.now(UTC)
    previous=json.loads(path.read_text()) if path.exists() else {}
    old=previous.get('rows',[]) or (seed_csv(seed) if seed else [])
    rows={r[0]:r for r in old};errors=[];verified=set(previous.get('officialYears',[]));checks=[]
    years=list(range(1990,now.year+1)) if full else [now.year-1,now.year]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(fetch,y,now):y for y in years}
        for f in concurrent.futures.as_completed(futures):
            y=futures[f]
            try:
                values=f.result();overlap=0;diff=0
                for r in values:
                    if r[0] in rows:
                        overlap+=1;diff+=any((a is None)!=(b is None) or (a is not None and b is not None and abs(a-b)>1e-8) for a,b in zip(rows[r[0]][1:],r[1:]))
                    rows[r[0]]=r
                verified.add(y);checks.append({'year':y,'observations':len(values),'priorOverlap':overlap,'revisedRows':diff})
            except Exception as e:errors.append(str(y)+': '+str(e))
    ordered=sorted(rows.values());last=ordered[-1][0]
    if previous.get('lastDate','')>last:raise ValueError('History regressed')
    nxt=dt.date.fromisoformat(last)+dt.timedelta(days=1)
    while nxt.weekday()>4:nxt+=dt.timedelta(days=1)
    coverage=min(now,dt.datetime.combine(nxt,dt.time(),UTC)).isoformat()
    data={'schemaVersion':1,'generatedAt':now.isoformat(),'source':'U.S. Treasury · Daily Par Yield Curve','sourceUrl':SOURCE,'unit':'yield_pct','keys':KEYS,'rows':ordered,'firstDate':ordered[0][0],'lastDate':last,'dataThroughAt':coverage,'officialYears':sorted(verified),'validation':sorted(checks,key=lambda c:c['year']),'health':'degraded' if errors else 'ok','errors':errors,'notes':['Nilai null tetap kosong ketika Treasury tidak menerbitkan tenor tersebut.','Yield bukan harga obligasi; CCI dihitung dari seri yield.','Kalender libur diperlakukan konservatif; tanggal terakhir sumber selalu ditampilkan.']}
    path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')));temp.replace(path)
    print(json.dumps({'rows':len(ordered),'first':ordered[0][0],'last':last,'verifiedYears':len(verified),'errors':errors,'revisedRows':sum(c['revisedRows'] for c in checks)}))
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--path',type=Path,default=Path(__file__).resolve().parents[1]/'data/tqqq_radar/bonds.json');p.add_argument('--full',action='store_true');p.add_argument('--seed',type=Path);a=p.parse_args();collect(a.path,a.full,a.seed)
