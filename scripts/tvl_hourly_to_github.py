#!/usr/bin/env python3
"""Collect real, timestamped DeFiLlama snapshots to GitHub, with Binance Spot 1H.
Hourly TVL is an OBSERVED SUM-OF-CHAINS PROXY, not official TOTAL_TVL.
No backfill, interpolation, synthetic candles, or trading signals.
"""
import csv, io, json, math, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "tvl"
HOURLY = OUT / "hourly_observed.csv"
DAILY = OUT / "daily_official.csv"
COINS = OUT / "crypto_1h_cache.json"
STATUS = OUT / "state_status.json"
FIELDS = ["observed_utc","observed_unix_ms","observed_hour_utc","sum_chain_usd","chains_count",
          "official_daily_latest_usd","official_daily_date_utc","gap_vs_official_pct","proxy_quality","source"]
HOUR = 3600000

def ts(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fetch(url):
    err = None
    for i in range(3):
        try:
            request = Request(url, headers={"User-Agent":"RadarTVLResearch/1.0", "Accept":"application/json", "Cache-Control":"no-cache"})
            with urlopen(request, timeout=35) as response:
                return json.load(response)
        except Exception as e:
            err = e
            if i < 2: time.sleep(2+3*i)
    raise RuntimeError(f"Could not fetch {url}: {err}")

def save_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    s = io.StringIO(newline="")
    writer = csv.DictWriter(s, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(s.getvalue(), encoding="utf-8")
    os.replace(tmp,path)

def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, separators=(",",":"))+"\n", encoding="utf-8")
    os.replace(tmp,path)

def existing(path):
    if not path.exists(): return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def capture_tvl(now_ms):
    chains = fetch("https://api.llama.fi/v2/chains")
    history = fetch("https://api.llama.fi/v2/historicalChainTvl")
    if not isinstance(chains,list) or not isinstance(history,list):
        raise ValueError("Unexpected DeFiLlama schema")
    values = [float(c["tvl"]) for c in chains
              if isinstance(c,dict) and str(c.get("name","")).lower() not in ("total","all")
              and isinstance(c.get("tvl"),(int,float)) and not isinstance(c["tvl"],bool)
              and math.isfinite(c["tvl"]) and c["tvl"] >= 0]
    if len(values)<20: raise ValueError("Insufficient chain TVL records")
    hist = []
    for r in history:
        if not isinstance(r,dict): continue
        d,v = r.get("date"),r.get("tvl")
        if isinstance(d,(int,float)) and isinstance(v,(int,float)) and math.isfinite(v) and v>0:
            hist.append({"source_date_utc":ts(d), "tvl_usd":f"{v:.8f}", "source_unix_s":int(d)})
    if len(hist)<100: raise ValueError("Insufficient historical daily TVL")
    hist.sort(key=lambda r:r["source_unix_s"])
    last=hist[-1]; total=sum(values); gap=100*(total/float(last["tvl_usd"])-1)
    row={"observed_utc":ts(now_ms/1000), "observed_unix_ms":str(now_ms),
         "observed_hour_utc":ts(now_ms//HOUR*HOUR/1000), "sum_chain_usd":f"{total:.8f}",
         "chains_count":str(len(values)), "official_daily_latest_usd":last["tvl_usd"],
         "official_daily_date_utc":last["source_date_utc"],"gap_vs_official_pct":f"{gap:.5f}",
         "proxy_quality":"PROXY_CLOSE_5PCT" if abs(gap)<=5 else "PROXY_DIFFERENT_GT5PCT",
         "source":"https://api.llama.fi/v2/chains;https://api.llama.fi/v2/historicalChainTvl"}
    by_hour={r["observed_hour_utc"]:r for r in existing(HOURLY) if r.get("observed_hour_utc")}
    by_hour[row["observed_hour_utc"]]=row
    save_csv(HOURLY,FIELDS,[by_hour[k] for k in sorted(by_hour)])
    save_csv(DAILY,["source_date_utc","tvl_usd","source_unix_s"],hist)
    return row,len(by_hour)

def capture_coins(now_ms):
    cached={}
    if COINS.exists():
        try:cached=json.loads(COINS.read_text(encoding="utf-8"))
        except (ValueError,OSError):pass
    output={};errors={}
    for asset in ["BTC","ETH","SOL","BNB"]:
        pair=asset+"USDT"
        paths=[f"https://data-api.binance.vision/api/v3/klines?{urlencode(dict(symbol=pair,interval='1h',limit=1000))}",
               f"https://api.binance.com/api/v3/klines?{urlencode(dict(symbol=pair,interval='1h',limit=1000))}"]
        new=None;source=None
        for url in paths:
            try:
                data=fetch(url)
                if isinstance(data,list) and len(data)>200:
                    new=data;source=url;break
            except Exception as exc:
                errors[asset]=str(exc)
        prior=cached.get(asset,{}).get("rows",[])
        merged={int(x[0]):[int(x[0]),float(x[1])] for x in prior if isinstance(x,list) and len(x)==2}
        if new:
            for k in new:
                try:
                    start,close,end=int(k[0]),float(k[4]),int(k[6])
                    if end+1<=now_ms and close>0 and math.isfinite(close):
                        merged[start]=[start,close]
                except (TypeError,ValueError,IndexError):continue
        cutoff=now_ms-60*86400000
        records=[v for t,v in sorted(merged.items()) if t>=cutoff]
        if len(records)<100:
            errors[asset]="Insufficient valid 1H candles"
            continue
        output[asset]={"rows":records,"source":source or cached.get(asset,{}).get("source","GITHUB_CACHE"),
                       "latest_close_utc":ts((records[-1][0]+HOUR)/1000),
                       "quality":"BINANCE_PUBLIC_1H" if new else "STALE_GITHUB_CACHE"}
    if output:save_json(COINS,output)
    return output,errors

def main():
    now=int(time.time()*1000)
    status={"observed_utc":ts(now/1000),"producer":"github_actions","tvl":{"success":False},"crypto":{}}
    try:
        row,n=capture_tvl(now)
        status["tvl"]={"success":True,"observed_utc":row["observed_utc"],"snapshot_count":n,
                       "latest_daily_date":row["official_daily_date_utc"],
                       "proxy_vs_daily_pct":row["gap_vs_official_pct"],"proxy_quality":row["proxy_quality"]}
        print("Observed chain-sum TVL USD billions:",round(float(row["sum_chain_usd"])/1e9,4),"count:",n)
    except Exception as exc:
        status["tvl"]={"success":False,"error":str(exc)}
        print("TVL capture failed:",exc,file=sys.stderr)
    try:
        coins,errors=capture_coins(int(time.time()*1000))
        status["crypto"]={"updated":list(coins),"errors":errors}
    except Exception as exc:
        status["crypto"]={"updated":[],"error":str(exc)}
    save_json(STATUS,status)
    if not status["tvl"]["success"]:sys.exit(1)

if __name__=="__main__":
    main()
