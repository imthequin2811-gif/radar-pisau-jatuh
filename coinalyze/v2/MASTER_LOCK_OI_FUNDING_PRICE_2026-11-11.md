# MASTER BARU — RADAR OI × FUNDING × HARGA V2
**Tanggal dibuat:** 11 November 2026. **Status:** DRAFT MASTER V2 sesuai permintaan pengguna, tidak menimpa file MASTER LOCK lain. Simpan keputusan pengguna yang mengotorisasi perubahan setelah ini sebagai revisi berikutnya.

## Sumber dan cakupan
- **Data:** GitHub [data/coinalyze/history](https://github.com/imthequin2811-gif/radar-pisau-jatuh/tree/main/data/coinalyze/history). Dihimpun dari API Coinalyze.
- **Pasar:** satu kontrak perpetual **OKX** per aset: `BTCUSDT_PERP.3`, `ETHUSDT_PERP.3`, `SOLUSDT_PERP.3`, `BNBUSDT_PERP.3`. Data bukan total OI pasar global atau data Binance. Kontrak OKX untuk harga/OI/funding konsisten.
- Data harian disaring hingga **sebelum 11 November 2026 00:00 UTC**. Hanya candle custom **CLOSED** penuh sejak reset 1 Jan 00 UTC. Referensi terakhir semua aset: **6D CLOSED 9 November 2026 07.00 WIB**. 4D = sensor; 6D = keputusan; 12D = konteks. Evaluasi 6D berikutnya 15 Nov; lalu 21 Nov, 27 Nov, 3 Des, 9 Des pukul 07 WIB.

## Teknik baru: tidak menggunakan CCI/WMA pada OI
- OI USD = notional open interest Coinalyze API dengan `convert_to_usd=true`. Nilai dolar bisa berubah karena harga, bukan semata jumlah posisi baru.
- **OI coin-equivalent = OI USD / harga futures CLOSE**, metrik estimasi kuantitas, bukan observasi langsung kontrak long/short.
- OI coin 6D % & 12D %, perbandingan harga 6D/12D, funding percentile historis, dan reaksi harga 4D lebih utama daripada CCI/WMA OI.
- **Funding di visual = rata-rata 6 nilai daily CLOSE dari API Coinalyze, dalam satuan native API**. Tidak identik dengan biaya funding aktual tiap settlement 8 jam; jangan rescale persen sembarangan.
- Status: BUILD-UP ketika OI coin bertambah; FLUSH ketika turun tajam; CROWDING hanya bila funding/eksposur sudah ekstrem dan harga macet; RECLAIM harus terbukti di harga 4D CLOSED. OI tidak dapat sendiri menentukan arah net long atau net short, karena setiap kontrak memiliki kedua sisi.
- Harga spot/analisis radar harga lama menjadi validasi independen, bukan input perhitungan OI/Funding.

## Proyeksi 1 bulan — model analog eksploratif
- Horizon **5 candle 6D ke depan:** 15, 21, 27 November, 3, 9 Desember 2026, pukul 07 WIB. 9 Des = +30 hari dari candle acuan 9 Nov.
- Untuk setiap aset secara terpisah, cari **30 tetangga historis terdekat** sejak 2023 yang cocok pada enam fitur yang diketahui di penutupan candle: perubahan harga 6D /8, perubahan OI coin 6D /12, funding-rank 24 candle diubah menjadi skala `(rank−0.5)×3`, perubahan harga 12D /14, perubahan OI coin 12D /20, perubahan harga 6D sebelumnya /8. Jarak Euclidean, bobot `1/(1+distance²)`.
- Analog wajib punya 5 candle 6D lengkap di masa depan yang sudah tercatat. Untuk titik tiap 6D, data analog dinormalisasi ke level sekarang, lalu diambil kuantil berbobot **P15, P50, P85** secara terpisah untuk **harga**, **OI koin**, **OI USD** dan **Funding**.
- **P50 adalah skenario tengah berdasarkan analog**, bukan target pasti; P15–P85 adalah rentang analog, bukan jaminan probabilitas 70%. P50 beberapa metrik/tanggal tidak harus satu jalur analog terpadu; jangan klaim P50(OI USD) = P50(harga) × P50(OI koin).

## Hasil snapshot CLOSED 9 November → prediksi 9 Desember
| Aset | Harga CLOSE 9 Nov | ΔOI coin 6D | Funding 6D native | Harga P50 9 Des | Harga rentang P15–P85 9 Des | OI coin P50 9 Des | OI USD P50 9 Des | Funding P50 9 Des | Akurasi arah 30D audit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BTC | $74818.10 | -0.63% | 0.006319 | $77664.81 | $64803.82–$92336.83 | 34686 | $2569.76M | 0.002405 | 54.3% |
| ETH | $2126.61 | 3.49% | 0.002523 | $2156.73 | $1904.85–$2678.91 | 667563 | $1455.22M | 0.004520 | 53.6% |
| SOL | $86.49 | -4.77% | 0.003966 | $85.99 | $62.27–$118.38 | 3507679 | $315.61M | 0.000701 | 46.4% |
| BNB | $684.76 | -18.53% | 0.002067 | $663.88 | $602.84–$726.74 | 67287 | $47.16M | 0.001742 | 50.3% |

## Pemeriksaan keandalan, batas & disiplin keputusan
- Audit **rolling-origin** historis 2024 sampai Agustus 2026, 151 titik uji/aset, analog pada cutoff hanya memakai sampel lampau yang seluruh hasil 5×6D-nya telah diketahui sebelum waktu keputusan. Ini audit retrospektif, bukan pengujian luar-sampel independen; ada overlap dan korelasi antar-sampel.
- BTC: akurasi arah 30D **54.3%**; cakupan rentang P15–P85 **69.5%**; median kesalahan persentase return 30D **8.8 poin persentase**.
- ETH: akurasi arah 30D **53.6%**; cakupan rentang P15–P85 **55%**; median kesalahan persentase return 30D **14.4 poin persentase**.
- SOL: akurasi arah 30D **46.4%**; cakupan rentang P15–P85 **76.2%**; median kesalahan persentase return 30D **18.1 poin persentase**.
- BNB: akurasi arah 30D **50.3%**; cakupan rentang P15–P85 **61.6%**; median kesalahan persentase return 30D **7.6 poin persentase**.
- Kualitas arah dekat acak. Hasil **tidak cukup** untuk entry long/short berleverage. OI/Funding digunakan sebagai radar tekanan dan potensi squeeze/flush, bukan trigger satu-satunya. Konfirmasi 4D pivot/struktur harga, 6D konfirmasi, area invalidasi, biaya/funding aktual, dan risk/reward diperlukan. Jika tidak jelas, **WAIT**.
- Data sumber berlaku untuk **satu kontrak OKX**; tidak mewakili agregat seluruh exchange, apalagi spot. Harga future bisa berbeda dari Binance Spot.
- Prediksi ini **bukan data live**, data yang masih RUNNING tidak boleh dinamai CLOSED. Forecast di HTML harus dipisah garis putus-putus dan arsiran.

## File master V2
- [Dashboard master visual](https://github.com/imthequin2811-gif/radar-pisau-jatuh/blob/main/coinalyze/v2/MASTER_RADAR_OI_FUNDING_PRICE_2026-11-11.html).
- [Data snapshot numerik 2026 + lima tanggal prediksi](https://github.com/imthequin2811-gif/radar-pisau-jatuh/blob/main/coinalyze/v2/RADAR_V2_OI_FUNDING_PRICE_DATA_2026-11-11.json).
- Semua master dan dashboard indikator CCI/WMA lama **tidak dihapus dan tidak diubah**. Versi V2 adalah **master riset baru, terpisah**.
