"""Write the 07:00 WIB daily spot and derivatives report."""
import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WIB = timezone(timedelta(hours=7))
ASSETS = ("BTC", "ETH", "SOL", "BNB")
BIAS = {
    (1, 1): "Harga menguat, posisi bertambah",
    (1, -1): "Pantulan dengan pengurangan posisi",
    (-1, 1): "Harga melemah, posisi bertambah",
    (-1, -1): "Harga melemah, posisi berkurang",
}


def rows(path):
    if path.is_file():
        with path.open(newline="", encoding="utf-8") as file:
            yield from csv.DictReader(file)


def derivatives(symbol, metric):
    path = DATA / "coinalyze" / "history" / f"{symbol}_{metric}-history_daily.csv"
    return {datetime.fromtimestamp(int(row["t"]), timezone.utc).date(): float(row["c"])
            for row in rows(path) if row["symbol"] == symbol}


def change(series, previous, latest):
    old, new = series.get(previous), series.get(latest)
    if old is None or new is None or not all(math.isfinite(v) and v > 0 for v in (old, new)):
        return None
    return 100 * (new / old - 1)


def display(value, format_spec):
    if value is None or not math.isfinite(value):
        return "—"
    return format(value, format_spec)


def direction(value):
    return (value > 0) - (value < 0)


def report(now):
    latest = now.astimezone(timezone.utc).date() - timedelta(days=1)
    previous = latest - timedelta(days=1)
    cutoff = datetime.combine(latest + timedelta(days=1), datetime.min.time(), WIB)
    contracts = {row["base_asset"]: row["symbol"]
                 for row in rows(DATA / "coinalyze" / "catalog" / "selected-markets.csv")}
    lines = [
        f"# Analisis harian kripto · {cutoff:%d-%m-%Y} · 07.00 WIB",
        "",
        f"Candle 1D Binance dan Coinalyze bertanggal {latest} UTC. "
        "Perubahan dibandingkan dengan hari UTC sebelumnya.",
        "",
        "| Aset | Spot USDT | Spot 1D | Kontrak Coinalyze | OI 1D | Funding sebelumnya → terakhir | Pembacaan |",
        "|---|---:|---:|---|---:|---|---|",
    ]
    for asset in ASSETS:
        spot_path = DATA / "binance" / f"{asset}USDT_1D_source.csv"
        spot = {datetime.fromisoformat(row["open_time_utc"]).date(): float(row["close"])
                for row in rows(spot_path) if row["status"] == "CLOSED"}
        spot_change = change(spot, previous, latest)
        symbol = contracts.get(asset, "")
        oi = change(derivatives(symbol, "open-interest"), previous, latest) if symbol else None
        funding = derivatives(symbol, "funding-rate") if symbol else {}
        if spot_change is None:
            bias = "Data spot 1D belum lengkap"
        elif oi is None:
            bias = "Konfirmasi OI belum tersedia"
        else:
            bias = BIAS.get((direction(spot_change), direction(oi)), "Harga atau OI stabil")
        lines.append(
            f"| {asset} | {display(spot.get(latest), ',.2f')} | {display(spot_change, '+.2f')} | "
            f"{symbol or '—'} | {display(oi, '+.2f')} | {display(funding.get(previous), '+.6g')} → "
            f"{display(funding.get(latest), '+.6g')} | {bias} |"
        )
    lines.extend([
        "", "Perubahan spot dan OI dalam persen. Funding memakai satuan asli API.",
        "Tanda — menunjukkan data untuk tanggal yang diperlukan belum tersedia.",
        "OI merujuk pada kontrak yang tercantum. Arah posisi tidak dapat disimpulkan dari OI saja.",
        "",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    output = DATA / "coinalyze" / "DAILY_WIB.md"
    output.write_text(report(datetime.now(timezone.utc)), encoding="utf-8")
