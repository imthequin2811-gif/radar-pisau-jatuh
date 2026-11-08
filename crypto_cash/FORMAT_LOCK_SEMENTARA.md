# CRYPTO CASH — FORMAT LOCK SEMENTARA (8 November 2026)

Pertahankan struktur ini untuk setiap scan berikutnya sampai pengguna menyetujui perubahan:

1. Metode A = CRYPTOCAP:TOTAL − CRYPTOCAP:TOTALES (TradingView). Jika data harian belum tersedia, tulis **MISSING**, bukan angka buatan.
2. Metode B = USD-pegged stablecoin market cap/supply (DefiLlama via Aethereal), data harian dan histori sejak 2017.
3. Indikator = CCI(18, Close) + WMA(6) dari CCI. WMA bukan pada kapitalisasi USD langsung.
4. Prioritaskan TF custom **6D CLOSED**, anchor reset 1 Januari 00:00 UTC; tampilkan TF **12D CLOSED** sebagai pembanding, dan 1D hanya bila diberi label eksplisit.
5. Jendela inti empat bulan terbaru **jangan dihapus atau diubah**. Tambahkan jendela 2022–sekarang sebagai visual historis terpisah.
6. Wajib visual: CCI18 dan WMA6 dengan crossing dan tanggal CLOSED yang dapat diaudit; kapitalisasi USD dan perubahan nominal USD setiap CLOSED 6D; detail setiap crossing (CCI/WMA dan titik perubahan arah slope WMA).
7. Wajib angka: terakhir tiga sampel CLOSED, delta WMA6, delta2 WMA6, sudut atan(delta/20), delta sudut, panah; tanggal CLOSED UTC dan WIB berikut jadwal close berikutnya; cash dan flow nominal US$B.
8. Jangan menyebut perubahan pasokan stablecoin sebagai jumlah USD bank yang benar-benar keluar tanpa bukti redemption.
9. Tahun akhir dapat memiliki candle 6D parsial lebih pendek; tandai bucket_days < 6 dan jangan samakan dengan candle 6D penuh saat backtest.
10. Boleh MENAMBAH grafik atau data untuk mempelajari pola tanpa mengganti format inti. Format yang sudah terkunci sementara tidak boleh diganti tanpa izin pengguna.

GitHub outputs yang harus dipertahankan:
- `B_6D_VISUAL.png`, `B_12D_VISUAL.png` — grafik 4 bulan
- `B_6D_CCI_WMA_2022_NOW.png` — lima panel tahunan, tahun 2022 sampai sekarang
- `B_6D_USD_FLOW_2022_NOW.png` — USD supply & perubahan 6D sejak 2022
- `B_6D_AUDIT_2022_NOW.csv` — semua CLOSED candles dengan tanggal dan nilai
- `B_6D_CROSSINGS_2022_NOW.csv` — daftar crossing beserta tanggal
- `RADAR_SUMMARY.csv`, `STATUS.json`

Status 8 November 2026: B tersedia, A belum memiliki ekspor TradingView; tidak diperkenankan merekayasa seri A.
