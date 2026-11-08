#!/usr/bin/env python3
"""Crypto Cash A vs B: 6D/12D CCI(18, Close) + WMA(6) on CCI.
B: USD-pegged stablecoin supply (DefiLlama via Aethereal daily CSV).
A: TradingView CRYPTOCAP:TOTAL - CRYPTOCAP:TOTALES, if CSV exports exist.
All buckets reset on Jan 1 00:00 UTC. Only complete CLOSED bars are scored.
"""
from __future__ import annotations
import argparse
import json
import math
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

B_URL = "https://dataset.aethereal.top/files/stablecoin-market-cap-history.csv"
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crypto_cash"
DATA.mkdir(parents=True, exist_ok=True)

def dates(v):
    if pd.api.types.is_numeric_dtype(v):
        n = pd.to_numeric(v, errors="coerce")
        unit = "ms" if n.dropna().median() > 1e11 else "s"
        return pd.to_datetime(n, unit=unit, utc=True).dt.tz_convert(None).dt.normalize()
    return pd.to_datetime(v, errors="coerce", utc=True).dt.tz_convert(None).dt.normalize()

def read_b():
    req = urllib.request.Request(B_URL, headers={"User-Agent": "Mozilla/5.0 CryptoCashRadar/1.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = resp.read()
    import io
    f = pd.read_csv(io.BytesIO(data))
    if not {"date", "circulating_usd"}.issubset(f.columns):
        raise ValueError("Bad B dataset schema")
    s = pd.Series(pd.to_numeric(f.circulating_usd, errors="coerce").to_numpy(), index=dates(f.date), name="B")
    s = s.dropna().groupby(level=0).last().sort_index() / 1e9
    if len(s) < 500 or s.index[-1] < pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() - pd.Timedelta(days=7):
        raise ValueError("B source stale or insufficient history")
    s.rename("usd_billions").to_csv(DATA / "B_DAILY_HISTORY.csv", index_label="date")
    return s

def read_tv(path):
    f = pd.read_csv(path)
    cols = {str(c).strip().lower(): c for c in f.columns}
    tc = next((cols[k] for k in ("time", "date", "datetime", "timestamp") if k in cols), None)
    cc = next((cols[k] for k in ("close", "closing price", "value") if k in cols), None)
    if not tc or not cc:
        raise ValueError(f"{path}: required columns time/date and close")
    s = pd.Series(pd.to_numeric(f[cc], errors="coerce").to_numpy(), index=dates(f[tc]))
    return s.dropna().groupby(level=0).last().sort_index()

def read_a():
    total, ex = DATA / "TV_TOTAL_1D.csv", DATA / "TV_TOTALES_1D.csv"
    if not total.exists() and not ex.exists():
        return None
    if not (total.exists() and ex.exists()):
        raise ValueError("Both TV_TOTAL_1D.csv and TV_TOTALES_1D.csv are required")
    z = pd.concat({"total": read_tv(total), "ex": read_tv(ex)}, axis=1).dropna()
    a = (z["total"] - z["ex"]) / 1e9
    if (a < 0).any():
        raise ValueError("A negative: check TOTAL/TOTALES exports and USD units")
    return a.rename("A")

def candles(s, tf, cutoff):
    f = s.to_frame("cap").sort_index()
    years = f.index.year
    year_start = pd.to_datetime(years.astype(str) + "-01-01")
    idx = (f.index - year_start).days // tf
    f["start"] = year_start + pd.to_timedelta(idx * tf, unit="D")
    year_end = pd.to_datetime(years.astype(str) + "-12-31") + pd.Timedelta(days=1)
    f["end"] = pd.to_datetime(np.minimum((f.start + pd.Timedelta(days=tf)).values, year_end.values))
    g = f.groupby(["start", "end"]).agg(cap=("cap", "last"), rows=("cap", "count")).reset_index()
    g = g[(g.end <= cutoff) & (g.rows == (g.end - g.start).dt.days)].copy().sort_values("end")
    g = g.set_index("end")
    mean = g.cap.rolling(18, min_periods=18).mean()
    mad = g.cap.rolling(18, min_periods=18).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    g["cci18"] = (g.cap - mean) / (0.015 * mad.replace(0, np.nan))
    g["wma6"] = g.cci18.rolling(6, min_periods=6).apply(
        lambda x: float(np.dot(x, np.arange(1, 7)) / 21), raw=True)
    g["flow_bn"] = g.cap.diff()
    g["dwma"] = g.wma6.diff()
    g["d2wma"] = g.dwma.diff()
    g["angle"] = np.degrees(np.arctan(g.dwma / 20))
    g["delta_angle"] = g.angle.diff()
    g["gap_cci_wma"] = g.cci18 - g.wma6
    g["cross"] = np.where((g.gap_cci_wma > 0) & (g.gap_cci_wma.shift(1) <= 0), "CCI_CROSS_UP",
                 np.where((g.gap_cci_wma < 0) & (g.gap_cci_wma.shift(1) >= 0), "CCI_CROSS_DOWN", "NONE"))
    def arrow(r):
        if pd.isna(r.dwma) or pd.isna(r.d2wma): return "N/A"
        if r.dwma < 0: return "DOWN_RECOVERING" if r.d2wma > 0 else "DOWN_ACCELERATING"
        return "UP_SLOWING" if r.d2wma < 0 else "UP_ACCELERATING"
    g["arrow"] = g.apply(arrow, axis=1)
    g["closed_wib"] = (g.index + pd.Timedelta(hours=7)).strftime("%Y-%m-%d %H:%M WIB")
    return g

def plot(which, tf, g, start, cutoff):
    sub = g.loc[g.index >= start]
    fig, axes = plt.subplots(3, 1, figsize=(15, 10), sharex=True, gridspec_kw={"height_ratios":[1,1.35,1]})
    if not sub.empty:
        axes[0].plot(sub.index, sub.cap, marker=".", label=f"{which} USD stablecoins")
        axes[1].plot(sub.index, sub.cci18, ls="--", marker=".", alpha=.65, label="CCI18 close")
        axes[1].plot(sub.index, sub.wma6, lw=2.6, marker="o", label="WMA6(CCI18)")
        axes[2].bar(sub.index, sub.flow_bn, width=tf * .6, label="Change per CLOSED candle (US$B)")
        for level in (-100,0,100): axes[1].axhline(level, ls=":", alpha=.55)
        axes[2].axhline(0, color="gray", lw=1)
        for ax in axes: ax.grid(alpha=.2); ax.legend(fontsize=9, loc="best")
    axes[0].set_ylabel("Capitalization US$B")
    axes[1].set_ylabel("CCI / WMA units")
    axes[2].set_ylabel("Net change US$B")
    axes[2].xaxis.set_major_locator(mdates.DayLocator(interval=12))
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    axes[2].set_xlim(start, cutoff + pd.Timedelta(days=3))
    fig.suptitle(f"CRYPTO CASH {which} — {tf}D CLOSED | CCI18 + WMA6 | 4 months")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(DATA / f"{which}_{tf}D_VISUAL.png", dpi=150)
    plt.close(fig)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--asof", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    args = p.parse_args()
    cutoff = pd.Timestamp(args.asof)
    start = cutoff - pd.DateOffset(months=4)
    stocks = {"B": read_b()}
    a = read_a()
    if a is not None: stocks["A"] = a
    status = {"snapshot_utc":args.asof, "source_B":B_URL,
              "source_A":"TradingView CSV exports" if a is not None else "MISSING - requires TV exports",
              "rules":"Close only; UTC year anchor; CCI18 of capitalization; WMA6 of CCI; angles atan(delta/20)"}
    latest = []
    for name, s in stocks.items():
        for tf in (6, 12):
            g = candles(s, tf, cutoff)
            g.to_csv(DATA / f"{name}_{tf}D_HISTORY.csv", index_label="close_utc")
            plot(name, tf, g, start, cutoff)
            ready = g.dropna(subset=["wma6","dwma","d2wma"])
            if ready.empty:
                status[f"{name}_{tf}D"] = "HISTORY_INSUFFICIENT"; continue
            last = ready.iloc[-1]
            latest.append({"method":name, "tf":f"{tf}D", "closed_utc":ready.index[-1].strftime("%Y-%m-%d 00:00 UTC"),
              "closed_wib":last.closed_wib, "cash_usd_bn":round(float(last.cap),4),
              "net_flow_usd_bn":round(float(last.flow_bn),4), "cci18":round(float(last.cci18),3),
              "wma6":round(float(last.wma6),3), "dwma":round(float(last.dwma),3),
              "d2wma":round(float(last.d2wma),3), "angle":round(float(last.angle),3),
              "arrow":last.arrow, "cross":last.cross})
    pd.DataFrame(latest).to_csv(DATA / "RADAR_SUMMARY.csv", index=False)
    status["available_methods"] = list(stocks)
    status["valid_rows"] = len(latest)
    (DATA / "STATUS.json").write_text(json.dumps(status, indent=2), encoding="utf8")
    print(json.dumps(status, indent=2))
    print(pd.DataFrame(latest).to_string(index=False))

if __name__=="__main__":
    main()
