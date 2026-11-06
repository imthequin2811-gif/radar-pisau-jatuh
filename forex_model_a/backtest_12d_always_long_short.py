"""LONG ALWAYS vs SHORT ALWAYS in 12-day Forex calendar blocks.

Objective: compare fixed directional exposure rather than screen signals.
Positions: open at each NEW closed-eligible 12D block's first D1 OPEN,
close at its last D1 CLOSE, re-open at next block's first D1 OPEN.
12D resets Jan 1 UTC annually; the 5/6-day year-end residual is
included explicitly to avoid pretending exposure is fully continuous.
Last RUNNING 12D block is omitted; closed 2019--present blocks only.
Historical quote source: Dukascopy BID D1, not TradingView OANDA.

Portfolio starts $10,000 and REINVESTS profits/losses, with leverage
1x, 2x, or 10x of CURRENT equity at entry. Flat roundtrip 1.5 pip
transaction cost at entry, no other costs. Trade may end in a simulated
FULL broker margin closeout when equity <= 50% of initial margin.
Margin requirement = notional / 10, i.e. broker maximum available 10x.
This broker maintenance rule is illustrative, NOT a real broker
liquidation policy. In this test, margin closeout terminates strategy,
and the remaining cash is retained. Intraday crossing of margin
threshold is checked against historical daily HIGH/LOW and opening gaps.
No TP/SL except simulated margin closeout. No order execution.
"""
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import backtest_model_a_6d12d as base

PAIRS=("eurusd","gbpusd","usdchf")
SIDES=(("ALWAYS_LONG",1),("ALWAYS_SHORT",-1))
LEVERAGES=(1,2,10)
START_USD=10000.
ASSUMED_COST_PIPS=1.5
PIP=.0001
BROKER_MAX_LEVERAGE=10.
MAINTENANCE_MARGIN_PCT=0.50
RESULTS=Path("forex_12d_long_vs_short_results")
RESULTS.mkdir(exist_ok=True,parents=True)


def pnl_usd(pair,units,side,entry,price):
    if pair=="usdchf":
        return units*side*(price-entry)/price
    return units*side*(price-entry)


def trigger_for_margin(pair,units,side,entry,required_pnl):
    """Solve units*side*quoted_change == required USD PnL."""
    if pair=="usdchf":
        z=required_pnl/(units*side)
        denominator=1.-z
        return entry/denominator if denominator>0 else np.nan
    return entry+required_pnl/(units*side)


def price_and_margin(pair,d):
    dates = d.copy()
    blocks=base.calendar_bars(dates,12)
    first=pd.Timestamp("2019-01-01",tz="UTC")
    # Include fully closed 12D and year-end residual buckets. No RUNNING blocks.
    closed=blocks[blocks.valid &
             (blocks.start>=first) &
             (blocks.end<=dates.date.iloc[-1]+pd.Timedelta(days=1))].copy()
    if closed.empty: raise ValueError("No closed buckets for 2019 onward")
    return closed


def run_strategy(pair,d,blocks,label,side,leverage):
    balance=START_USD
    peak=START_USD
    worst_dd=0.
    min_equity=START_USD
    rows=[]
    closeout=None
    for _,bar in blocks.iterrows():
        if closeout: break
        days=d[(d.date>=bar.start)&(d.date<bar.end)]
        if days.empty: continue
        entry=float(days.open.iloc[0])
        if balance<=.01:
            closeout={"date":str(days.date.iloc[0]),"reason":"BALANCE_EXHAUSTED"}
            break
        equity_start=balance
        if pair=="usdchf":
            units=equity_start*leverage
            fee_usd=units*ASSUMED_COST_PIPS*PIP/entry
        else:
            units=equity_start*leverage/entry
            fee_usd=units*ASSUMED_COST_PIPS*PIP
        fee_paid=fee_usd
        cash=equity_start-fee_paid
        opening_margin=equity_start*leverage/BROKER_MAX_LEVERAGE
        min_allowed=opening_margin*MAINTENANCE_MARGIN_PCT
        threshold=trigger_for_margin(pair,units,side,entry,
                                     min_allowed-cash)
        exit_date=days.date.iloc[-1]
        exit_price=float(days.close.iloc[-1])
        reason="PERIOD_CLOSE"
        for _,day in days.iterrows():
            openp=float(day.open)
            bad=float(day.low) if side>0 else float(day.high)
            marked_open=cash+pnl_usd(pair,units,side,entry,openp)
            marked_bad=cash+pnl_usd(pair,units,side,entry,bad)
            hit_at_open=marked_open<=min_allowed
            hit_intraday=marked_bad<=min_allowed
            if hit_at_open or hit_intraday:
                # Use the MODELLED actual exit mark, not the day's later
                # adverse high/low after the position is already closed.
                exit_price=openp if hit_at_open else threshold
                marked_exit=cash+pnl_usd(pair,units,side,entry,exit_price)
                min_equity=min(min_equity,marked_exit)
                worst_dd=min(worst_dd,(marked_exit-peak)/peak*100)
                exit_date=day.date
                reason="ILLUSTRATIVE_MARGIN_CLOSEOUT"
                break
            min_equity=min(min_equity,marked_open,marked_bad)
            worst_dd=min(worst_dd, (min(marked_open,marked_bad)-peak)/peak*100)
            marked_close=cash+pnl_usd(pair,units,side,entry,float(day.close))
            peak=max(peak,marked_close)
            worst_dd=min(worst_dd,(marked_close-peak)/peak*100)
        balance=cash+pnl_usd(pair,units,side,entry,exit_price)
        min_equity=min(min_equity,balance)
        worst_dd=min(worst_dd,(balance-peak)/peak*100)
        peak=max(peak,balance)
        record=dict(pair=pair.upper(),strategy=label,leverage=leverage,
              start=str(bar.start),period_end=str(bar.end),
              is_full_12d=bool((bar.end-bar.start).days==12),
              entry_date=str(days.date.iloc[0]),exit_date=str(exit_date),
              side="LONG" if side>0 else "SHORT",
              entry=entry,exit=exit_price,exit_reason=reason,
              fee_usd=fee_paid,equity_before=equity_start,
              equity_after=balance,
              pnl_usd=balance-equity_start,
              return_pct=(balance/equity_start-1)*100,
              margin_usd=opening_margin)
        rows.append(record)
        if reason=="ILLUSTRATIVE_MARGIN_CLOSEOUT":
            closeout={"date":str(exit_date),"price":exit_price,
                      "balance_remaining":balance}
            break
    return rows,dict(
        pair=pair.upper(),strategy=label,leverage=leverage,
        trades=len(rows),
        full_12d_trades=sum(r["is_full_12d"] for r in rows),
        initial_usd=round(START_USD,2),
        final_equity_usd=round(balance,2),
        net_pnl_usd=round(balance-START_USD,2),
        return_pct=round((balance/START_USD-1)*100,2),
        worst_intraday_equity_dd_pct=round(worst_dd,2),
        min_intraday_equity_usd=round(min_equity,2),
        margin_closeout=bool(closeout),
        closeout_date=(closeout or {}).get("date",""),
        data_end=str(d.date.iloc[-1])
    )


def main():
    base.base.START="2017-01-01"
    summary=[]; annual=[]; audit=[]
    for pair in PAIRS:
        daily=base.daily_data(base.base.get_data(pair))
        blocks=price_and_margin(pair,daily)
        audit.append(dict(pair=pair.upper(),n_complete_periods=len(blocks),
                          n_full_12d=int(((blocks.end-blocks.start).dt.days==12).sum()),
                          first_D1=str(daily.date.iloc[0]),
                          last_D1=str(daily.date.iloc[-1]),
                          last_completed_period_end=str(blocks.end.iloc[-1])))
        for label,sign in SIDES:
            for lev in LEVERAGES:
                trades,result=run_strategy(pair,daily,blocks,label,sign,lev)
                summary.append(result)
                pd.DataFrame(trades).to_csv(
                    RESULTS/f"{pair}_{label.lower()}_{lev}x_trades.csv",index=False)
                for year in range(2019,datetime.now(timezone.utc).year+1):
                    y=[t for t in trades if pd.Timestamp(t["entry_date"]).year==year]
                    if not y: continue
                    y_equity_start=y[0]["equity_before"]
                    y_equity_end=y[-1]["equity_after"]
                    annual.append(dict(pair=pair.upper(),strategy=label,leverage=lev,
                      year=year,n=len(y),start_usd=round(y_equity_start,2),
                      end_usd=round(y_equity_end,2),
                      pnl_usd=round(y_equity_end-y_equity_start,2),
                      return_pct=round((y_equity_end/y_equity_start-1)*100,2),
                      margin_closeout=any(x["exit_reason"]==
                          "ILLUSTRATIVE_MARGIN_CLOSEOUT" for x in y)))
                print(f'{pair.upper()} {label} {lev}x: final '
                      f'{result["final_equity_usd"]} USD, '
                      f'return {result["return_pct"]}%, '
                      f'MC={result["margin_closeout"]}',flush=True)
    pd.DataFrame(summary).to_csv(RESULTS/"summary.csv",index=False)
    pd.DataFrame(annual).to_csv(RESULTS/"yearly_results.csv",index=False)
    pd.DataFrame(audit).to_csv(RESULTS/"data_audit.csv",index=False)
    print(pd.DataFrame(summary).to_string(index=False),flush=True)
    print("No order execution; 12D calendar buckets reset Jan 1 UTC. "
          "Last RUNNING candle omitted. Year-end residual included as such. "
          "Constant exposure only within daily OHLC periods, reset at each 12D "
          "entry; 1x/2x/10x compounding, no price SL/TP except mock MC at "
          "equity <=50% initial margin; all available balance used as margin "
          "at 10x. Cost 1.5pip roundtrip per entry; swap/slippage excluded. "
          "Dukascopy BID D1 only, not OANDA.",flush=True)


if __name__=="__main__":
    main()
