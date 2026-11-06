"""GBPUSD weekly MIXED_CLOSE_HIGHER inversion experiment.

A: LONG, price stop 0.1%; B: SHORT, price stop 0.1%;
C: SHORT, price stop 0.5%. Same direction-independent weekly signals.
All enter at first D1 open of signal week; if not stopped, exit at
next week's final D1 close. No fixed take-profit. Historical backtest only.

Two comparisons:
  MATCHED_47: EXACT same 47 entry dates as earlier losing long signals;
      hypothetical independent parallel trades, may overlap after reversal.
  INDEPENDENT: each variant trades ALL eligible MIXED_CLOSE_HIGHER events
      with a no-overlap state machine and first-entry-at-next-week rules.
This pattern was selected retrospectively; results are exploratory.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import backtest_weekly_01pct_sl as weekly

REPO_RESULTS = Path("weekly_01pct_sl_results/gbpusd_trades.csv")
OUT = Path("weekly_mixed_inversion_results")
OUT.mkdir(exist_ok=True)
CONFIGS = (
    ("A_LONG_SL_0p1", 1, 0.001),
    ("B_SHORT_SL_0p1", -1, 0.001),
    ("C_SHORT_SL_0p5", -1, 0.005),
)
FIRST_YEAR = 2019
COST_PIPS = 1.5
PIP = 0.0001


def outcome(d, week, name, sign, sl_frac):
    next_week = week + pd.Timedelta(days=7)
    segment = d[(d.week == week) | (d.week == next_week)]
    if segment.empty or not (segment.week == next_week).any():
        raise ValueError(f"Missing full two-week observation: {week}")
    first = segment.iloc[0]
    entry = float(first.open)
    stop = entry * (1 - sl_frac) if sign > 0 else entry * (1 + sl_frac)
    risk_price = abs(entry - stop)
    exited = segment.iloc[-1]
    exit_px = float(exited.close)
    why = "NEXT_WEEK_CLOSE"
    for _, q in segment.iterrows():
        hit = float(q.low) <= stop if sign > 0 else float(q.high) >= stop
        if hit:
            slipped = float(q.open) < stop if sign > 0 else float(q.open) > stop
            exit_px = float(q.open) if slipped else stop
            exited = q
            why = "STOP"
            break
    gross = (exit_px - entry) * sign / risk_price
    net_R = gross - COST_PIPS * PIP / risk_price
    # GBPUSD P&L is USD quote. Notional at most $100k with 10x leverage.
    units = min(100. / risk_price, 100000. / entry)
    risk_usd = units * risk_price
    return {
        "strategy": name, "week_utc": str(week), "year": int(week.year),
        "entry_date": str(first.date), "side": "LONG" if sign > 0 else "SHORT",
        "entry": entry, "stop_frac_pct": sl_frac * 100.,
        "sl": stop, "stop_pips": risk_price/PIP,
        "exit_date": str(exited.date), "exit": exit_px,
        "exit_reason": why, "net_R": net_R,
        "initial_risk_usd": risk_usd,
        "margin_usd": units * entry / 10.,
        "pnl_usd": net_R * risk_usd,
    }


def metrics(df):
    if df.empty:
        return dict(n=0, win_pct=np.nan, stop_pct=np.nan, total_R=0.,
                    avg_R=np.nan, profit_factor=np.nan, dd_R=0., pnl_usd=0.)
    r = df.net_R.to_numpy(dtype=float)
    eq = np.r_[0, r.cumsum()]
    loss = -r[r < 0].sum()
    wins = r[r > 0].sum()
    return dict(n=len(df), win_pct=round(100.*np.mean(r > 0),1),
                stop_pct=round(100.*(df.exit_reason=="STOP").mean(),1),
                total_R=round(float(r.sum()),2),
                avg_R=round(float(r.mean()),3),
                profit_factor=round(float(wins/loss),3) if loss>0 else np.nan,
                dd_R=round(float((eq-np.maximum.accumulate(eq)).min()),2),
                pnl_usd=round(float(df.pnl_usd.sum()),2))


def evaluate(d, original, eligible):
    anchor_weeks = list(pd.to_datetime(original.week_open_utc, utc=True))
    summary = []
    for mode in ("MATCHED_47","INDEPENDENT"):
        for name, sign, frac in CONFIGS:
            if mode == "MATCHED_47":
                weeks = anchor_weeks
            else:
                weeks = eligible
            rows = []
            free_week = pd.Timestamp("2019-01-01",tz="UTC")
            for week in weeks:
                if mode == "INDEPENDENT" and week < free_week:
                    continue
                out = outcome(d, week, name, sign, frac)
                rows.append(out)
                if mode == "INDEPENDENT":
                    # Do not open the next position until the first new week
                    # AFTER the week in which the previous position exited.
                    last_exit_week = weekly.utc_week_start(pd.Timestamp(out["exit_date"]))
                    free_week = last_exit_week + pd.Timedelta(days=7)
            t=pd.DataFrame(rows)
            filename = f"{mode.lower()}_{name.lower()}"
            t.to_csv(OUT / f"{filename}_trades.csv",index=False)
            summary.append(dict(mode=mode,strategy=name,**metrics(t)))
            for yr in range(2019,2027):
                filtered = t[t.year==yr] if not t.empty else t
                annual.append(dict(mode=mode,strategy=name,year=yr,**metrics(filtered)))
    return summary


if __name__=="__main__":
    if not REPO_RESULTS.exists():
        raise FileNotFoundError(f"Missing earlier strategy transactions: {REPO_RESULTS}")
    original_all = pd.read_csv(REPO_RESULTS)
    original = original_all[
        (original_all.side=="LONG") &
        (original_all.structure=="MIXED_CLOSE_HIGHER")
    ].copy()
    original_r = original.net_R.sum()
    if len(original)!=47 or not (-52.5 < original_r < -52.3):
        raise ValueError(f"Original benchmark changed: n={len(original)}, R={original_r:.3f}")
    daily = weekly.prep_data(weekly.base.get_data("gbpusd"))
    candles = weekly.weekly_candles(daily)
    eligible = []
    for w in candles.index:
        if w.year < FIRST_YEAR: continue
        p1,p2,nextw = (w-pd.Timedelta(days=7),
                       w-pd.Timedelta(days=14),
                       w+pd.Timedelta(days=7))
        if not all(x in candles.index for x in (p1,p2,nextw)): continue
        if not all(bool(candles.loc[x,"valid"]) for x in (p1,p2,w,nextw)):
            continue
        side,structure = weekly.monthly_base.direction(candles.loc[p1],candles.loc[p2])
        if structure=="MIXED_CLOSE_HIGHER":
            eligible.append(w)
    annual = []
    result = evaluate(daily,original,eligible)
    summary = pd.DataFrame(result)
    summary.to_csv(OUT/"summary.csv",index=False)
    pd.DataFrame(annual).to_csv(OUT/"yearly_results.csv",index=False)
    anchor_net = pd.read_csv(OUT/"matched_47_a_long_sl_0p1_trades.csv").net_R.sum()
    with (OUT/"README.txt").open("w") as f:
        f.write(f"Originally selected 47 signals: total {original_r:.4f}R.\n"
                f"Replayed original long positions: total {anchor_net:.4f}R.\n"
                f"All unfiltered eligible MIXED_CLOSE_HIGHER signals: {len(eligible)}.\n"
                "Matched hypothetical strategies are NOT independently executable "
                "portfolios, since exits and reentry timing may differ.\n"
                "Independent strategies enforce no overlapping positions.\n"
                "Dukascopy BID D1, 1.5 pip friction, no swap/realistic slippage.\n"
                "Selected a losing subgroup after observing outcomes: "
                "in-sample selection bias, not prospective proof.\n")
    print(summary.to_string(index=False),flush=True)
    print("Original benchmark 47, total R:",round(original_r,2),
          "Replayed:",round(anchor_net,2),flush=True)
    print("Raw eligible weekly signals:",len(eligible),flush=True)
