
"""
MODEL A FOREX - AUTOMATIC BACKTEST
Data: Dukascopy BID 1D (not TradingView OANDA)
Pairs: EURUSD, GBPUSD, USDCHF
Strategy:
  Price Action + Liquidity Sweep
  Mean Reversion + Strong Breakout
"""

import subprocess
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# CONFIGURATION
START = "2019-01-01"
END = datetime.now(timezone.utc).strftime("%Y-%m-%d")

SYMBOLS = ("eurusd", "gbpusd", "usdchf")

FEE_PIPS = 1.5
PIP = 0.0001
HOLD = 12
SWEEP_LOOKBACK = 10
BREAKOUT_LOOKBACK = 20

REPORT_DIR = Path("model_a_results")
REPORT_DIR.mkdir(exist_ok=True)


# ====================================
# AUTO DOWNLOAD - DUKASCOPY
# ====================================

def get_data(symbol):
    if not shutil.which("npx"):
        raise RuntimeError("Node.js/npx is not available")

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    file = data_dir / f"{symbol}.csv"

    if file.exists():
        file.unlink()

    command = [
        "npx", "--yes", "dukascopy-node",
        "-i", symbol,
        "-from", START,
        "-to", END,
        "-t", "d1",
        "-f", "csv",
        "-p", "bid",
        "-dir", str(data_dir),
        "-fn", symbol,
        "--retries", "3",
        "--batch-size", "5",
        "--batch-pause", "1500",
    ]

    print(
        f"Downloading {symbol} from Dukascopy: "
        f"{START} to {END} exclusive",
        flush=True,
    )

    subprocess.run(
        command,
        check=True,
        timeout=900,
    )

    if not file.is_file() or file.stat().st_size == 0:
        raise RuntimeError(
            f"{symbol}: CSV download missing: {file}"
        )

    df = pd.read_csv(file)
    df.columns = [
        str(c).strip().lower() for c in df.columns
    ]

    required = [
        "timestamp", "open", "high", "low", "close"
    ]

    if any(c not in df.columns for c in required):
        raise ValueError(
            f"{symbol}: invalid columns {list(df.columns)}"
        )

    df["date"] = pd.to_datetime(
        pd.to_numeric(df["timestamp"], errors="raise"),
        unit="ms",
        utc=True,
    )

    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="raise")

    df = (
        df.sort_values("date")
        .drop_duplicates("date")
        .reset_index(drop=True)
    )

    if len(df) < 200:
        raise ValueError(
            f"{symbol}: insufficient history"
        )

    if df[["open", "high", "low", "close"]].isna().any().any():
        raise ValueError(f"{symbol}: missing OHLC")

    valid = (
        (df.high >= df[["open", "close", "low"]].max(axis=1))
        &
        (df.low <= df[["open", "close"]].min(axis=1))
    )

    if not valid.all():
        raise ValueError(f"{symbol}: invalid OHLC")

    last_date = df.date.iloc[-1]

    if (
        pd.Timestamp.now(tz="UTC") - last_date
    ).days > 7:
        raise ValueError(
            f"{symbol}: stale candle {last_date}"
        )

    print(
        f"{symbol}: {len(df)} candles "
        f"last={last_date}",
        flush=True,
    )

    return df


# ====================================
# MODEL A - SIGNAL GENERATION
# ====================================

def signals(df):
    d = df.copy()

    for n in (SWEEP_LOOKBACK, BREAKOUT_LOOKBACK):
        d[f"hi{n}"] = (
            d.high.shift(1).rolling(n).max()
        )
        d[f"lo{n}"] = (
            d.low.shift(1).rolling(n).min()
        )

    d["body"] = (
        (d.close - d.open).abs()
        / (d.high - d.low).replace(0, np.nan)
    )

    d["mid10"] = (d.hi10 + d.lo10) / 2

    output = []

    for i in range(21, len(d) - 1):
        bar = d.iloc[i]
        nxt = d.iloc[i + 1]

        if pd.isna(bar.hi20) or pd.isna(bar.lo20):
            continue

        kind = None
        side = 0
        stop = None

        # LIQUIDITY SWEEP LONG
        if (
            bar.low < bar.lo10
            and bar.close > bar.lo10
            and bar.close < bar.mid10
        ):
            kind = "SWEEP_MEAN_REVERSION"
            side = 1
            stop = bar.low - 2 * PIP

        # LIQUIDITY SWEEP SHORT
        elif (
            bar.high > bar.hi10
            and bar.close < bar.hi10
            and bar.close > bar.mid10
        ):
            kind = "SWEEP_MEAN_REVERSION"
            side = -1
            stop = bar.high + 2 * PIP

        # STRONG BREAKOUT LONG
        elif (
            bar.close > bar.hi20
            and bar.body >= 0.60
            and bar.close > bar.open
        ):
            kind = "STRONG_BREAKOUT"
            side = 1
            stop = bar.low - 2 * PIP

        # STRONG BREAKOUT SHORT
        elif (
            bar.close < bar.lo20
            and bar.body >= 0.60
            and bar.close < bar.open
        ):
            kind = "STRONG_BREAKOUT"
            side = -1
            stop = bar.high + 2 * PIP

        if kind is None:
            continue

        entry = float(nxt.open)
        risk = (entry - stop) * side

        if risk <= 0:
            continue

        if kind == "SWEEP_MEAN_REVERSION":
            target = float(bar.mid10)

            if (target - entry) * side < 2 * risk:
                continue
        else:
            target = entry + side * 2 * risk

        output.append({
            "idx": i + 1,
            "signal_date": str(bar.date.date()),
            "entry_date": str(nxt.date.date()),
            "setup": kind,
            "side": "LONG" if side > 0 else "SHORT",
            "sign": side,
            "entry": entry,
            "stop": float(stop),
            "target": float(target),
            "risk": risk,
        })

    return output


# ====================================
# BACKTEST SIMULATION
# ====================================

def simulate(df, candidates):
    trades = []
    free_idx = -1

    for s in candidates:
        i = s["idx"]

        if i <= free_idx:
            continue

        outcome = "TIME_EXIT"
        exit_idx = min(i + HOLD - 1, len(df) - 1)
        exit_px = float(df.iloc[exit_idx].close)

        for k in range(i, min(i + HOLD, len(df))):
            bar = df.iloc[k]

            if s["sign"] == 1:
                stop_hit = bar.low <= s["stop"]
                tp_hit = bar.high >= s["target"]
            else:
                stop_hit = bar.high >= s["stop"]
                tp_hit = bar.low <= s["target"]

            if stop_hit or tp_hit:
                outcome = (
                    "STOP" if stop_hit else "TARGET"
                )

                exit_px = (
                    s["stop"] if stop_hit
                    else s["target"]
                )

                # Conservative if stop and target
                # both touched within same candle.
                if stop_hit:
                    if (
                        float(bar.open) - s["stop"]
                    ) * s["sign"] < 0:
                        exit_px = float(bar.open)

                exit_idx = k
                break

        gross_r = (
            (exit_px - s["entry"])
            * s["sign"]
            / s["risk"]
        )

        net_r = (
            gross_r
            - FEE_PIPS * PIP / s["risk"]
        )

        trade = {
            k: v for k, v in s.items()
            if k not in ("idx", "sign")
        }

        trade.update({
            "exit_date": str(
                df.iloc[exit_idx].date.date()
            ),
            "exit": exit_px,
            "exit_reason": outcome,
            "gross_R": gross_r,
            "net_R": net_r,
        })

        trades.append(trade)
        free_idx = exit_idx

    return pd.DataFrame(trades)


# ====================================
# PERFORMANCE METRICS
# ====================================

def stats(trades):
    if trades.empty:
        return {
            "trades": 0,
            "winrate_pct": np.nan,
            "avg_R": np.nan,
            "total_R": np.nan,
            "max_drawdown_R": np.nan,
            "profit_factor": np.nan,
        }

    r = trades.net_R

    equity = r.cumsum()
    dd = equity - equity.cummax().clip(lower=0)

    wins = r[r > 0].sum()
    losses = -r[r < 0].sum()

    return {
        "trades": len(trades),
        "winrate_pct": round(
            (r > 0).mean() * 100, 1
        ),
        "avg_R": round(r.mean(), 3),
        "total_R": round(r.sum(), 2),
        "max_drawdown_R": round(dd.min(), 2),
        "profit_factor": (
            round(wins / losses, 3)
            if losses > 0 else np.nan
        ),
    }


# ====================================
# MAIN
# ====================================

def main():
    summary = []

    for symbol in SYMBOLS:
        df = get_data(symbol)

        print(
            f"{symbol}: {len(df)} bars "
            f"{df.date.iloc[0].date()} "
            f"through {df.date.iloc[-1].date()}"
        )

        trades = simulate(df, signals(df))

        if not trades.empty:
            trades.insert(0, "symbol", symbol.upper())

        trades.to_csv(
            REPORT_DIR / f"{symbol}_trades.csv",
            index=False,
        )

        segments = [
            (
                "ALL",
                pd.Series(True, index=trades.index),
            ),
            (
                "TRAIN_TO_2023",
                trades.entry_date < "2024-01-01"
                if not trades.empty
                else pd.Series(dtype=bool),
            ),
            (
                "HOLDOUT_2024_ON",
                trades.entry_date >= "2024-01-01"
                if not trades.empty
                else pd.Series(dtype=bool),
            ),
        ]

        for segment, mask in segments:
            subset = trades[mask]

            summary.append({
                "pair": symbol.upper(),
                "sample": segment,
                "setup": "ALL",
                **stats(subset),
            })

            if not subset.empty:
                for setup, group in subset.groupby("setup"):
                    summary.append({
                        "pair": symbol.upper(),
                        "sample": segment,
                        "setup": setup,
                        **stats(group),
                    })

    result = pd.DataFrame(summary)

    result.to_csv(
        REPORT_DIR / "summary.csv",
        index=False,
    )

    print(result.to_string(index=False))
    print("Backtest completed")
    print("Source: Dukascopy BID D1, not OANDA")
    print("Assumed roundtrip cost: 1.5 pips")
    print("No swap or position sizing included")


if __name__ == "__main__":
    main()
