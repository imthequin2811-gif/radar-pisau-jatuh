"""12D FOREX CCI18(CLOSE) + WMA7(CCI), ONE NEW POSITION PER FULL 12D BAR.
Dukascopy BID D1 (NOT TradingView/OANDA). Pure historical backtest; NO ORDERS.
Calendar blocks reset Jan 1 00:00 UTC; year-end partial 5/6-day residual
omitted from execution, and excluded from indicator warmup to avoid artificial gaps.
All trade decisions use PREVIOUS CLOSED 12D bar CCI and WMA.
Fixed roundtrip cost 1.5 pip. No swap, funding, real slippage, actual ask/bid.
Simulates $10,000 starting equity, 20x MAX brokerage leverage.
Two position sizing policies:
  RISK_1PCT: units sized to 1% equity at stop, capped by 20x notional.
  FULL_20X: full 20x notional at every 12D open (very high risk).
4 signals (the inverse is a diagnostic, not a recommendation):
  WMA7_SLOPE: LONG when WMA7 latest>previous else SHORT.
  CCI_VS_WMA7: LONG when previous CLOSED CCI>previous CLOSED WMA7 else SHORT.
  CCI_ZERO: LONG when CCI>0 else SHORT.
  INVERSE_WMA7_SLOPE: SHORT when WMA7 rising else LONG.
Stops: 0.5% or 1.0% entry-price. Time exit at current 12D CLOSE
or optional take profit 2R. If SL/TP hit, stay FLAT until NEXT 12D opening.
Only fully CLOSED, valid 12D bars are executed; 1 position per eligible block.
Model uses D1 high/low for stop-first conservative fills, with adverse open gaps.
Illustrative broker liquidation when equity <=50% opening margin is modelled;
broker-specific thresholds differ. Strategy stopped after that event.
2019-2023 in-sample selection; 2024 onward an untouched chronological report.
"""
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import pandas as pd
import backtest_model_a_6d12d as base

base.base.START="2017-01-01"
OUT=Path("forex_12d_cci18_wma7_results")
OUT.mkdir(exist_ok=True,parents=True)
PAIRS=("eurusd","gbpusd","usdchf")
MODELS=("WMA7_SLOPE","CCI_VS_WMA7","CCI_ZERO","INVERSE_WMA7_SLOPE")
SIZINGS=("RISK_1PCT","FULL_20X")
STOPS=(0.005,0.01)
EXITS=("CLOSE_12D","TP_2R")
INIT_USD=10000.
LEV=20.
MAINT_MARGIN_FRAC=.50
COST_PIPS=1.5
PIP=.0001
TRAIN_END_YEAR=2023
MIN_EQUITY_USD=100.


def ind_cci_close(close,n=18):
    sma=close.rolling(n,min_periods=n).mean()
    mad=close.rolling(n,min_periods=n).apply(
        lambda x: float(np.mean(np.abs(x-np.mean(x)))),raw=True)
    return (close-sma)/(.015*mad.replace(0,np.nan))


def ind_wma(s,n=7):
    w=np.arange(1,n+1,dtype=float)
    return s.rolling(n,min_periods=n).apply(
        lambda x: float(np.dot(x,w)/w.sum()),raw=True)


def make_bars(d):
    b=base.calendar_bars(d,12).copy()
    b["full_12d"]=(b.end-b.start).dt.days==12
    # Exclude year-end 1/2-day residual BEFORE calculating indicators.
    # Otherwise a non-trading Dec 31 residual creates NaN and artificially
    # erases 24 subsequent CCI18/WMA7 signals in the following year.
    b=b[b.full_12d].copy().reset_index(drop=True)
    b["cci18"]=ind_cci_close(b.close,18)
    b["wma7"]=ind_wma(b.cci18,7)
    b["wma7_prev"]=b.wma7.shift(1)
    b["cci18_prev"]=b.cci18.shift(1)
    b["is_complete"]=(b.valid & b.full_12d &
                      (b.end<=d.date.iloc[-1]+pd.Timedelta(days=1)))
    return b


def signal(bar,model):
    w=float(bar["wma7"]); prev=float(bar["wma7_prev"])
    c=float(bar["cci18"])
    if model=="WMA7_SLOPE": return 1 if w>prev else -1
    if model=="INVERSE_WMA7_SLOPE": return -1 if w>prev else 1
    if model=="CCI_VS_WMA7": return 1 if c>w else -1
    if model=="CCI_ZERO": return 1 if c>0 else -1
    raise ValueError(model)


def marked_pnl(pair,units,side,entry,mark):
    if pair=="usdchf":
        return units*side*(mark-entry)/mark
    return units*side*(mark-entry)


def price_for_required_pnl(pair,units,side,entry,need):
    if pair=="usdchf":
        fraction=need/(units*side)
        return entry/(1-fraction) if fraction<1 else np.nan
    return entry+need/(units*side)


def size_position(pair,entry,stop_frac,equity,sizing):
    if pair=="usdchf":
        # Units in BASE USD; margin notional is already USD.
        base_units_cap=LEV*equity
        base_risk_unit=stop_frac
        units=(min(base_units_cap,.01*equity/base_risk_unit)
               if sizing=="RISK_1PCT" else base_units_cap)
        fee=units*(COST_PIPS*PIP/entry)
        notional=units
    else:
        base_units_cap=LEV*equity/entry
        base_risk_unit=entry*stop_frac
        units=(min(base_units_cap,.01*equity/base_risk_unit)
               if sizing=="RISK_1PCT" else base_units_cap)
        fee=units*COST_PIPS*PIP
        notional=units*entry
    return units,fee,notional/LEV


def simulate(pair,d,b,model,sizing,stop_frac,exit_rule):
    equity=INIT_USD
    peak=equity
    lowest=equity
    dd_min_pct=0.
    trades=[]
    closeout=False
    year_end=pd.Timestamp("2019-01-01",tz="UTC")
    for k in range(2,len(b)):
        candle=b.iloc[k]
        if candle.start<year_end: continue
        if not candle.is_complete: continue
        previous=b.iloc[k-1]
        if not previous.valid or not np.isfinite(
            np.array([previous.cci18,previous.wma7,previous.wma7_prev],dtype=float)
        ).all():
            continue
        if equity<=MIN_EQUITY_USD: break
        block=d[(d.date>=candle.start)&(d.date<candle.end)]
        if block.empty: continue
        side=signal(previous,model)
        entry=float(block.open.iloc[0])
        stop=entry*(1-side*stop_frac)
        units,fee,margin=size_position(pair,entry,stop_frac,equity,sizing)
        if units<=0: continue
        tp=entry+side*2*abs(entry-stop) if exit_rule=="TP_2R" else np.nan
        equity_before=equity
        cash=equity-fee
        stopout_equity=MAINT_MARGIN_FRAC*margin
        stopout_price=price_for_required_pnl(pair,units,side,entry,stopout_equity-cash)
        fill=float(block.close.iloc[-1])
        exit_day=block.date.iloc[-1]
        why="CLOSE_12D"
        for _,day in block.iterrows():
            openp=float(day.open)
            adverse=float(day.low) if side>0 else float(day.high)
            day_open_eq=cash+marked_pnl(pair,units,side,entry,openp)
            # At session open, broker may liquidate on large gap first;
            # otherwise SL gaps fill at actual OPEN.
            if day_open_eq<=stopout_equity:
                fill=openp;exit_day=day.date;why="MARGIN_CLOSEOUT";closeout=True
                break
            if (openp<=stop if side>0 else openp>=stop):
                fill=openp;exit_day=day.date;why="STOP_GAP"
                break
            marked_adverse=cash+marked_pnl(pair,units,side,entry,adverse)
            stop_touch=adverse<=stop if side>0 else adverse>=stop
            # Stop occurs before worse margin threshold in normal trade,
            # but treat margin threshold crossing first if it is closer.
            if stop_touch:
                stop_equity=cash+marked_pnl(pair,units,side,entry,stop)
                if (stopout_equity>stop_equity and
                    (adverse<=stopout_price if side>0 else adverse>=stopout_price)):
                    fill=stopout_price;why="MARGIN_CLOSEOUT";closeout=True
                else:
                    fill=stop;why="STOP"
                exit_day=day.date
                break
            if marked_adverse<=stopout_equity:
                fill=stopout_price;exit_day=day.date;why="MARGIN_CLOSEOUT";closeout=True
                break
            if np.isfinite(tp) and (float(day.high)>=tp if side>0 else float(day.low)<=tp):
                fill=tp;exit_day=day.date;why="TP"
                break
            closing_mark=cash+marked_pnl(pair,units,side,entry,float(day.close))
            open_peak=peak
            peak=max(peak,closing_mark)
            lowest=min(lowest,day_open_eq,marked_adverse,closing_mark)
            dd_min_pct=min(dd_min_pct,
                100*(min(day_open_eq,marked_adverse,closing_mark)/open_peak-1))
        equity=cash+marked_pnl(pair,units,side,entry,fill)
        # Insolvency may occur on extreme gap. Don't compound negative equity.
        equity=max(0.,equity)
        lowest=min(lowest,equity)
        dd_min_pct=min(dd_min_pct,100*(equity/peak-1))
        peak=max(peak,equity)
        trades.append({
            "pair":pair.upper(),"model":model,"sizing":sizing,
            "stop_pct_price":stop_frac*100,"exit_rule":exit_rule,
            "period_start":str(candle.start),"period_end":str(candle.end),
            "entry_date":str(block.date.iloc[0]),"exit_date":str(exit_day),
            "year":int(candle.start.year),"direction":"LONG" if side>0 else "SHORT",
            "signal_closed":str(previous.end),
            "cci18":float(previous.cci18),"wma7":float(previous.wma7),
            "wma7_prev":float(previous.wma7_prev),
            "entry":entry,"sl":stop,"tp":tp,"exit":fill,
            "exit_reason":why,"units":units,
            "fee_usd":fee,"margin_initial_usd":margin,
            "equity_before":equity_before,"equity_after":equity,
            "pnl_usd":equity-equity_before,
            "pnl_pct_of_entry_equity":(equity/equity_before-1)*100,
            "risk_usd_if_stop":abs(marked_pnl(pair,units,side,entry,stop)),
            "intratrade_dd_pct_running":dd_min_pct
        })
        if closeout or equity<=0: break
    return trades


def performance(rows):
    if not rows:
        return dict(trades=0,initial_usd=np.nan,final_usd=np.nan,
                    pnl_usd=0.,return_pct=np.nan,
                    max_closed_dd_pct=np.nan,win_pct=np.nan,sl_pct=np.nan,
                    profit_factor=np.nan,closeout=False)
    start=rows[0]["equity_before"]
    finish=rows[-1]["equity_after"]
    eq=np.array([start]+[x["equity_after"] for x in rows])
    pnl=np.array([x["pnl_usd"] for x in rows])
    gains=pnl[pnl>0].sum();losses=-pnl[pnl<0].sum()
    return dict(
      trades=len(rows),initial_usd=round(start,2),
      final_usd=round(finish,2),pnl_usd=round(finish-start,2),
      return_pct=round(100*(finish/start-1),2),
      max_closed_dd_pct=round(float(np.min(100*(eq/np.maximum.accumulate(eq)-1))),2),
      win_pct=round(float(np.mean(pnl>0)*100),1),
      sl_pct=round(float(np.mean([r["exit_reason"].startswith("STOP") for r in rows])*100),1),
      profit_factor=round(float(gains/losses),3) if losses>0 else np.nan,
      closeout=bool(any(r["exit_reason"]=="MARGIN_CLOSEOUT" for r in rows))
    )


def main():
    summary=[];yearly=[];last=[];audit=[]
    for pair in PAIRS:
        d=base.daily_data(base.base.get_data(pair))
        b=make_bars(d)
        b.to_csv(OUT/f"{pair}_12d_cci18_wma7_candles.csv",index=False)
        audit.append(dict(pair=pair.upper(),data_first=str(d.date.iloc[0]),
           data_last=str(d.date.iloc[-1]),
           full_valid_12d=int(b.is_complete.sum()),
           total_bars=int(len(b)),running_or_invalid=int((~b.is_complete).sum())))
        for model in MODELS:
            for sizing in SIZINGS:
                for sl in STOPS:
                    for exit_rule in EXITS:
                        rows=simulate(pair,d,b,model,sizing,sl,exit_rule)
                        train=[r for r in rows if r["year"]<=TRAIN_END_YEAR]
                        test=[r for r in rows if r["year"]>TRAIN_END_YEAR]
                        perf=performance(rows)
                        perf_train=performance(train)
                        perf_test=performance(test)
                        summary.append(dict(pair=pair.upper(),model=model,
                             sizing=sizing,sl_price_pct=sl*100,
                             exit_rule=exit_rule,**perf,
                             train_trades=perf_train["trades"],
                             train_return_pct=perf_train["return_pct"],
                             train_final_usd=perf_train["final_usd"],
                             train_closed_dd_pct=perf_train["max_closed_dd_pct"],
                             max_intratrade_dd_pct=(round(float(rows[-1]["intratrade_dd_pct_running"]),2)
                               if rows else np.nan),
                             test_trades=perf_test["trades"],
                             test_return_pct=perf_test["return_pct"],
                             test_final_usd=perf_test["final_usd"]))
                        for year in range(2019,datetime.now(timezone.utc).year+1):
                            y=[r for r in rows if r["year"]==year]
                            p=performance(y)
                            yearly.append(dict(pair=pair.upper(),model=model,
                              sizing=sizing,sl_price_pct=sl*100,
                              exit_rule=exit_rule,year=year,**p))
                        # Only save trade-by-trade for risk-capped configurations
                        # plus two full20x diagnostics to keep repo lean.
                        if sizing=="RISK_1PCT" or (model=="WMA7_SLOPE" and exit_rule=="CLOSE_12D"):
                            pd.DataFrame(rows).to_csv(OUT/
                               f"{pair}_{model.lower()}_{sizing.lower()}_sl{int(sl*1000)}_{exit_rule.lower()}_trades.csv",
                               index=False)
                        if rows: last.append(rows[-1])
                        print(f"{pair.upper()} {model} {sizing} SL={sl*100:.1f}% "
                              f"{exit_rule}: return={perf['return_pct']}% "
                              f"closed DD={perf['max_closed_dd_pct']}% "
                              f"trades={perf['trades']} MC={perf['closeout']}",
                              flush=True)
    df=pd.DataFrame(summary)
    df.to_csv(OUT/"summary.csv",index=False)
    pd.DataFrame(yearly).to_csv(OUT/"yearly_results.csv",index=False)
    pd.DataFrame(audit).to_csv(OUT/"data_audit.csv",index=False)
    # Rank solely by PRE-2024 training years; report 2024+ without fitting.
    selected=[]
    for pair in PAIRS:
        g=df[(df.pair==pair.upper())&(df.sizing=="RISK_1PCT")].copy()
        g=g[(g.train_trades>80)&g.train_return_pct.notna()]
        if g.empty: continue
        g=g.sort_values(["train_return_pct","train_closed_dd_pct"],ascending=[False,False])
        selected.append(g.iloc[0].to_dict())
    pd.DataFrame(selected).to_csv(OUT/"train_selected_models.csv",index=False)
    print("TRAIN-ONLY winners (2019-2023). Test 2024+ not used for selection:",flush=True)
    print(pd.DataFrame(selected)[["pair","model","sl_price_pct","exit_rule",
         "train_return_pct","test_return_pct","return_pct",
         "max_closed_dd_pct","closeout"]].to_string(index=False),flush=True)
    print("All results are gross of swap and true broker spread/slippage. "
      "No guarantee of profitability, no live orders. "
      "Candle data Dukascopy BID 1D, actual broker margin rules may differ.",
      flush=True)

if __name__=="__main__":
    main()
