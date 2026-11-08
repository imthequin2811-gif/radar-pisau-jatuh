#!/usr/bin/env python3
"""Produce verifiable historical 6D visual study from precomputed Crypto Cash B.
No interpolation and no new data assumptions. Chart chronology follows CLOSED UTC.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT / "data" / "crypto_cash"
SOURCE=DIR / "B_6D_HISTORY.csv"


def build_bc_locked(t):
    """Locked 6D B+C+ZERO combined annual charts with exact source CLOSED dates."""
    for year, d in t.groupby("year_start"):
        d = d.sort_values("close_utc").copy()
        d["gap"] = d.cci18 - d.wma6
        fig, ax = plt.subplots(figsize=(15, 6))
        ax.plot(d.close_utc, d.gap, lw=2, label="B: GAP (CCI18 - WMA6)", color="#2563eb", marker=".", markersize=4)
        ax.plot(d.close_utc, d.wma6, lw=2, label="C: WMA6 on CCI18", color="#d97706", marker=".", markersize=4)
        ax.axhline(0, color="#64748b", ls="--", lw=1.2, label="ZERO: CCI/WMA cross")
        ac = d[(d.cross == "CCI_CROSS_UP") & (d.wma6 <= -100)]
        ex = d[(d.cross == "CCI_CROSS_DOWN") & (d.wma6 >= 80)]
        ax.scatter(ac.close_utc, ac.gap, marker="^", s=95, color="#16a34a", zorder=5, label="AKUMULASI? (study)")
        ax.scatter(ex.close_utc, ex.gap, marker="v", s=95, color="#dc2626", zorder=5, label="EXIT? (study)")
        for _, p in pd.concat([ac, ex]).iterrows():
            ax.annotate(p.close_utc.strftime("%d %b"), (p.close_utc, p.gap),
                textcoords="offset points", xytext=(0, 12 if p.cross == "CCI_CROSS_UP" else -18),
                ha="center", fontsize=8)
        ax.set_title(f"CRYPTO CASH B+C LOCKED | {year} | 6D CLOSED | ZERO")
        ax.set_ylabel("CCI units (GAP & WMA)")
        ax.grid(alpha=.22)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.legend(loc="best", ncol=2, fontsize=8)
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(DIR / f"B_C_ZERO_LOCKED_6D_{year}.png", dpi=145)
        plt.close(fig)
    t[["close_utc", "start", "cap", "cci18", "wma6", "gap_cci_wma",
       "flow_bn", "dwma", "d2wma", "angle", "cross", "arrow"]].to_csv(
        DIR / "B_C_ZERO_LOCKED_6D_2022_NOW.csv", index=False)


def main():
    if not SOURCE.is_file():
        raise SystemExit("Run build_crypto_cash.py first; B_6D_HISTORY.csv unavailable")
    t=pd.read_csv(SOURCE, parse_dates=["close_utc","start"]).sort_values("close_utc")
    t=t[t.start >= pd.Timestamp("2022-01-01")].copy()
    if t.empty: raise ValueError("No CLOSED 6D rows since 2022")
    # Audit-friendly: only exact CLOSED bucket timestamps, no interpolation.
    t["close_date_utc"]=t.close_utc.dt.strftime("%Y-%m-%d")
    t["close_datetime_wib"]=(t.close_utc+pd.Timedelta(hours=7)).dt.strftime("%Y-%m-%d 07:00 WIB")
    t["bucket_days"]=(t.close_utc-t.start).dt.days
    t["year_start"]=t.start.dt.year
    t["flow_6d_usd_bn"]=t.flow_bn
    t["cross_type"]=t.cross
    t["wma_slope_turn"]=np.where(
        (t.dwma>0)&(t.dwma.shift(1)<=0),"WMA_SLOPE_UP",
        np.where((t.dwma<0)&(t.dwma.shift(1)>=0),"WMA_SLOPE_DOWN","NONE"))
    full_cols=["close_date_utc","close_datetime_wib","start","bucket_days","cap","flow_6d_usd_bn",
               "cci18","wma6","dwma","d2wma","angle","delta_angle","cross_type","wma_slope_turn"]
    t[full_cols].to_csv(DIR/"B_6D_AUDIT_2022_NOW.csv",index=False,float_format="%.6f")
    t.loc[(t.cross_type!="NONE")|(t.wma_slope_turn!="NONE"),full_cols].to_csv(
        DIR/"B_6D_CROSSINGS_2022_NOW.csv",index=False,float_format="%.6f")

    years=sorted(t.year_start.unique().tolist())
    # Historical oscillator — a separate yearly panel ensures dates are readable.
    fig,axs=plt.subplots(len(years),1,figsize=(16,3.6*len(years)),sharey=True)
    axs=np.atleast_1d(axs)
    for ax,year in zip(axs,years):
        a=t.loc[t.year_start==year]
        ax.plot(a.close_utc,a.cci18,color="#aab4c4",lw=1.2,ls="--",alpha=.85,label="CCI18 Close")
        ax.plot(a.close_utc,a.wma6,color="#146ea8",lw=2.35,label="WMA6 on CCI18")
        ax.scatter(a.close_utc,a.wma6,color="#146ea8",s=9,zorder=4)
        for level in (-100,0,100): ax.axhline(level,color="#bbc4cc",ls=":",lw=.75)
        for side,c,m in (("CCI_CROSS_UP","#258a57","^"),("CCI_CROSS_DOWN","#c44843","v")):
            cross=a.loc[a.cross_type==side]
            ax.scatter(cross.close_utc,cross.wma6,s=75,marker=m,color=c,
                edgecolors="white",linewidths=.5,zorder=8,
                label=("CCI↑WMA cross" if side.endswith("_UP") else "CCI↓WMA cross"))
        ax.set_title(f"{year}  •  {len(a)} CLOSED candles  •  6D year-reset UTC",loc="left",fontsize=11,fontweight="bold")
        ax.set_ylabel("CCI / WMA")
        ax.grid(alpha=.2)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.tick_params(axis="x",rotation=0,labelbottom=True)
        ax.legend(ncol=4,fontsize=8,loc="upper right")
        if year<years[-1]:
            ax.set_xlim(pd.Timestamp(f"{year}-01-01"),pd.Timestamp(f"{year+1}-01-10"))
        else:
            ax.set_xlim(pd.Timestamp(f"{year}-01-01"),a.close_utc.max()+pd.Timedelta(days=9))
    fig.suptitle("CRYPTO CASH METHOD B  |  CCI18 + WMA6  |  6D CLOSED  |  FROM 2022",fontsize=17,fontweight="bold")
    fig.text(.5,.004,"Cross triangles mark CCI18 vs WMA6 crossings, NOT direct fiat outflows. "
             "Exact 6D dates and slope crossings: B_6D_CROSSINGS_2022_NOW.csv",ha="center",fontsize=9)
    fig.tight_layout(rect=[0,.015,1,.965],h_pad=1.5)
    fig.savefig(DIR/"B_6D_CCI_WMA_2022_NOW.png",dpi=145,bbox_inches="tight")
    plt.close(fig)

    fig,(ax0,ax1)=plt.subplots(2,1,figsize=(17,9),sharex=True,
                             gridspec_kw={"height_ratios":[1.2,1]},layout="constrained")
    ax0.plot(t.close_utc,t.cap,color="#17649f",lw=2.15,marker=".",markersize=2)
    ax0.set_ylabel("Total USD stablecoins • US$ billions")
    ax0.set_title("METHOD B — Circulating USD stablecoin capitalization | 6D CLOSED (2022–present)",loc="left",fontweight="bold")
    ax0.grid(alpha=.2)
    pos=t.flow_bn>=0
    ax1.bar(t.loc[pos,"close_utc"],t.loc[pos,"flow_bn"],width=4.7,color="#238b55",label="Supply ↑")
    ax1.bar(t.loc[~pos,"close_utc"],t.loc[~pos,"flow_bn"],width=4.7,color="#c54744",label="Supply ↓")
    ax1.axhline(0,color="#8f959c",lw=1)
    ax1.set_title("Six-day change in supply — not verified net fiat withdrawals",loc="left",fontweight="bold")
    ax1.set_ylabel("USD billions / CLOSED candle")
    ax1.grid(alpha=.19)
    ax1.legend()
    for ax in (ax0,ax1):
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.tick_params(axis="x",rotation=35)
    fig.savefig(DIR/"B_6D_USD_FLOW_2022_NOW.png",dpi=150,bbox_inches="tight")
    plt.close(fig)
    build_bc_locked(t)
    print(f"Historical 6D output: {len(t)} CLOSED candles, {years[0]}–{years[-1]}; "
          f"{sum(t.cross_type!='NONE')} CCI/WMA crossings.")

if __name__=="__main__":
    main()
