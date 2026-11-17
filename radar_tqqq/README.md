# Radar TQQQ · VIX · NDTH · DXY — data otomatis

Collector tanpa API key, Python standard library. File data: [`../data/tqqq_radar/market-data.json`](../data/tqqq_radar/market-data.json).

GitHub Actions memeriksa setiap **15 menit** (menit 07, 22, 37, 52 UTC). Ini polling best-effort, bukan streaming; antrean GitHub dan cache sumber dapat menambah jeda. Dashboard memeriksa salinan GitHub setiap 60 detik selama halaman terbuka.

| Data | Sumber | Status yang benar |
|---|---|---|
| Quote VIX | Yahoo Finance `^VIX` | Quote bertimestamp; latensi tidak dijamin |
| VIX OHLC harian | Cboe VIX History CSV | EOD resmi, dapat terlambat terbit |
| Quote + OHLC DXY | Yahoo Finance `DX-Y.NYB` | Quote bertimestamp + EOD; bukan broad USD/futures |
| NDTH | EODData `INDEX:NDTH` | **EOD**, bukan live intraday |
| TQQQ | Yahoo Finance TQQQ | Quote + split-adjusted OHLC, tanpa penyesuaian dividen |

## Pemisahan wajib

- `latestQuote.asOf` adalah waktu harga dari penyedia, bukan waktu collector berjalan. NDTH hanya mempunyai `sessionDate`; jam harga tidak dibuat-buat.
- `retrievedAt` / `historyFetchedAt` adalah waktu pengambilan. `dataThroughAt` membatasi sampai kapan kalender boleh dianggap tercakup oleh OHLC; fetch sukses saja tidak membuat candle terbaru CLOSED.
- Quote tidak dimasukkan ke deret EOD. Indikator CCI/WMA memakai `rows` yang sudah final saja. Tidak ada order broker.
- Perubahan last price tidak otomatis mengonfirmasi cross CCI/WMA. Crossing kalender yang membutuhkan sesi EOD yang belum tersedia tetap belum final.
- Jika sumber gagal, simpan data lama beserta timestamp aslinya, set `historyFetchStatus` atau `quoteFetchStatus` ke ERROR, dan catat alasan. Jangan mengubah waktu data menjadi seolah baru.
- NDTH adalah seri aktual Nasdaq-100 di atas SMA200. Setiap pengambilan menggabungkan sesi baru ke arsip. Histori pendek tidak diisi dengan NDX, rekonstruksi konstituen, atau nilai sintetis. Tidak ada feed NDTH intraday terverifikasi yang dipasang.
- Sumber publik dapat membatasi permintaan atau berubah format. Jika perlu NDTH intraday berlisensi, sambungkan penyedia yang memberi akses; jangan labeli EOD sebagai live.

## Menjalankan dan memeriksa

```sh
python -m unittest discover -s radar_tqqq -p 'test_*.py'
python radar_tqqq/collect.py --force-history
```

Workflow `Radar TQQQ VIX NDTH DXY — automatic data` bisa dijalankan manual dengan **Run workflow**. Riwayat harian ditarik ulang tiap enam jam, quote tiap run. Workflow hanya melakukan commit ke `data/tqqq_radar/`; file crypto dan radar lain tidak diubah.

Dashboard HTML unduhan tetap membawa snapshot offline dan mengambil pembaruan publik GitHub saat tersambung. Pembaruan otomatis tidak memerlukan login GitHub di HTML. Versi HTML lama yang hanya snapshot perlu diganti dengan versi otomatis.


## NDTH history backfill — 17 November 2026

The original EODData page exposed only recent daily rows. The archive now includes **5,024 actual daily INDEX:NDTH OHLC observations, 2006-12-29 through 2026-11-16**, obtained from [TradingView's public chart](https://www.tradingview.com/symbols/INDEX-NDTH/). This is the actual Nasdaq 100 Stocks Above 200-Day Average series, not a reconstruction using today's constituents.

Validation: all 11 overlapping EODData rows matched OHLC exactly. An independent [50-row TradingView export on GitHub](https://github.com/Gabriele-Gurrera/z_Codici_finiti_e_ganzi/blob/95187f23f9b202188c911c9681ed3e43736d7909/modello_tv_NDTH_INDEX_1D.csv) also matched all OHLC values. Dates were unique and ordered, values stayed within 0–100%, and there were no gaps longer than seven calendar days. This cross-check does not independently audit every historical observation.

The existing scheduled collector retains the full archive and appends completed daily EODData rows. NDTH remains EOD, not real-time. Backfill provenance and validation dates are stored in `assets.NDTH.historyArchive`.

For a deliberate future history refresh:

```bash
python -m pip install 'websockets>=15,<16'
python radar_tqqq/backfill_ndth.py
```

The optional backfill uses the anonymous public chart feed without credentials. It validates the resolved symbol, at least five overlapping recent EOD observations, OHLC bounds, duplicates, and gaps before writing. A rejected/unavailable feed leaves the existing archive untouched. The chart interface is unofficial and may change; the scheduled EOD collector does not depend on it.
