#!/usr/bin/env python3
"""LOCK SEMENTARA: single combined 6D B+C chart, 2022 onward, yearly views.
B = GAP = CCI(18,Close)-WMA6(CCI18); C = WMA6(CCI18).
POI candidate labels: ACCUM? when cross up & WMA<=-100, EXIT? when cross down & WMA>=80.
These are EXPERIMENTAL LIQUIDITY labels, not verified BTC buy/sell instructions.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"crypto_cash"

def main():
    path=OUT/"B_6D_HISTORY.csv"
    if not path.exists(): raise SystemExit("Missing B_6D_HISTORY.csv; run build_crypto_cash.py first")
    x=pd.read_csv(path,parse_dates=["close_utc","start"]).sort_values("close_utc")
    x=x[(x.start >= pd.Timestamp("2022-01-01")) & x.cci18.notna() & x.wma6.notna()].copy()
    if x.empty: raise ValueError("No validated 6D closed data since 2022")
    x["source_year"]=x.start.dt.year
    x["gap"]=x.cci18-x.wma6
    x["poi_label"]=np.where((x.cross=="CCI_CROSS_UP")&(x.wma6<=-100),"AKUMULASI?",
                   np.where((x.cross=="CCI_CROSS_DOWN")&(x.wma6>=80),"EXIT?",""))
    x["close_wib"]=(x.close_utc+pd.Timedelta(hours=7)).dt.strftime("%Y-%m-%d 07:00 WIB")
    cols=["close_utc","close_wib","start","source_year","cap","flow_bn","cci18","wma6","gap",
          "dwma","d2wma","angle","delta_angle","cross","poi_label"]
    x[cols].to_csv(OUT/"B_6D_BC_ALL_2022_NOW.csv",index=False,float_format="%.5f")
    x.loc[x.poi_label!="",cols].to_csv(OUT/"B_6D_BC_POI_2022_NOW.csv",index=False,float_format="%.5f")
    for yr, d in x.groupby("source_year"):
        fig,ax=plt.subplots(figsize=(16,5.5))
        ax.plot(d.close_utc,d.gap,lw=2.15,marker=".",markersize=5,color="#2563eb",label="B · GAP (CCI18−WMA6)")
        ax.plot(d.close_utc,d.wma6,lw=2.5,marker="o",markersize=3.5,color="#d97706",label="C · WMA6(CCI18)")
        ax.axhline(0,color="#64748b",ls="--",lw=.85,alpha=.65)
        ax.axhline(-100,color="#16a34a",ls=":",lw=.8,alpha=.55)
        ax.axhline(80,color="#dc2626",ls=":",lw=.8,alpha=.55)
        b=d[d.poi_label=="AKUMULASI?"]
        e=d[d.poi_label=="EXIT?"]
        ax.scatter(b.close_utc,b.gap,s=112,marker="^",color="#15803d",zorder=6,label="Kandidat akumulasi")
        ax.scatter(e.close_utc,e.gap,s=112,marker="v",color="#dc2626",zorder=6,label="Kandidat exit")
        if len(b)+len(e) <= 6:
            for _,p in pd.concat([b,e]).iterrows():
                ax.annotate(p.close_utc.strftime("%d %b"),(p.close_utc,p.gap),xytext=(0,12 if p.poi_label=="AKUMULASI?" else -16),
                    textcoords="offset points",ha="center",fontsize=9,
                    color="#15803d" if p.poi_label=="AKUMULASI?" else "#dc2626")
        ax.set_title(f"CRYPTO CASH B+C | {yr} | 6D CLOSED · CCI18→WMA6",loc="left",fontweight="bold",fontsize=14,pad=14)
        ax.set_ylabel("CCI units")
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1 if yr==x.source_year.max() else 2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.set_xlim(d.close_utc.min()-pd.Timedelta(days=5),d.close_utc.max()+pd.Timedelta(days=8))
        ax.grid(alpha=.18)
        ax.legend(ncol=2,loc="lower left",fontsize=9)
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(OUT/f"B_6D_BC_GABUNGAN_{yr}.png",dpi=150,bbox_inches="tight")
        plt.close(fig)
    print(f"BC combined charts: {len(x)} 6D CLOSED records, {x.source_year.min()}–{x.source_year.max()}; "
          f"strong POIs={sum(x.poi_label!='')}")

if __name__=="__main__":
    main()
