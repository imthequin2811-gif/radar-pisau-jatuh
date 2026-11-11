# RADAR TVL × CRYPTO — GitHub otomatis (modul terpisah)

Modul penelitian khusus **4H / 6H / 8H / 12H** dengan **CCI(18, Close) → WMA6 pada CCI**. Radar crypto 4D/6D/12D/18D yang sudah ada tidak diubah.

## Otomasi

- Workflow: [radar_tvl_intraday.yml](../../.github/workflows/radar_tvl_intraday.yml)
- Sumber snapshot: [DeFiLlama /v2/chains](https://api.llama.fi/v2/chains) — jumlah TVL per chain saat workflow berjalan, **proxy total**, bukan seri historis resmi `TOTAL_TVL`.
- Sumber harian resmi terpisah: [DeFiLlama /v2/historicalChainTvl](https://api.llama.fi/v2/historicalChainTvl).
- Sumber crypto: Binance Spot 1H, BTCUSDT/ETHUSDT/SOLUSDT/BNBUSDT.
- Jadwal observasi GitHub Actions: **23 menit lewat setiap jam UTC**, subject to GitHub schedule delay/failure.
- Pencatatan: hanya snapshot yang *benar-benar* berhasil diperoleh. Jam yang kosong tidak diisi/interpolasi. Status **CLOSED** TVL adalah proksi sampling, bukan OHLC TVL resmi.

## File yang muncul setelah job pertama berhasil

- `hourly_observed.csv` — waktu pengamatan, total proxy USD, jumlah chain, gap terhadap data resmi 1D.
- `daily_official.csv` — histori Total TVL resmi harian dari API.
- `crypto_1h_cache.json` — OHLC close Binance 1H (data sumber untuk TF kecil).
- `state_status.json` — tanggal terakhir job dan status API.

## Rumus dan batas pembandingan

CCI18 menggunakan 18 **close** dan rata-rata deviasi absolut dengan faktor 0,015. WMA6 adalah WMA linier berbobot 1..6 atas **CCI18**, tidak atas USD. Untuk intraday, CCI/WMA baru dapat dihitung setelah 23 candle TF utuh dan berurutan, lalu crossing WMA TVL vs coin dievaluasi pada tanggal TF yang sama.

Divergensi dan crossing ini adalah **riset momentum relatif**; nilainya belum membuktikan sinyal trading. TVL USD dipengaruhi juga oleh naik-turunnya valuasi token, bukan semata-mata arus modal segar.

Dashboard HTML offline milik pengguna dapat mengambil CSV langsung dari GitHub raw, tanpa menjalankan kolektor Windows atau mengunggah CSV.
