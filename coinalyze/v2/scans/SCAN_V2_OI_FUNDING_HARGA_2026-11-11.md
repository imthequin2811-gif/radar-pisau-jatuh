# SCAN & SAVE — MASTER V2 OI × FUNDING × HARGA
**Tanggal pemeriksaan:** 11 November 2026 (WIB/WITA).  
**Data acuan terakhir:** candle custom 6D **CLOSED 9 November 2026 pukul 07.00 WIB** (00:00 UTC).  
**Sumber:** GitHub `imthequin2811-gif/radar-pisau-jatuh`, `data/coinalyze/history`; empat kontrak **OKX perpetual**, satu per aset.  
**Verifikasi sumber:** SHA dari 12 CSV OHLCV/OI/Funding untuk BTC, ETH, SOL, BNB semuanya sama dengan catatan snapshot V2. Tidak ada perubahan data sumber dibandingkan saat V2 dibuat.  
**Status:** scan ulang selesai; master V2 tidak diubah. **Bukan feed harga realtime**.

## Ringkasan CLOSED
| Aset | Harga Δ6D | OI koin-ekuivalen Δ6D | Funding mean daily-close native | Status | Keputusan |
|---|---:|---:|---:|---|---|
| BTC | -2,57% | -0,63% | 0,006320 | OI relatif datar | WAIT |
| ETH | -5,59% | 3,49% | 0,002523 | BUILD-UP turun | WAIT |
| SOL | -5,94% | -4,77% | 0,003966 | DELEVERAGING | WAIT |
| BNB | -2,03% | -18,53% | 0,002067 | FLUSH besar | WAIT |

**BTC:** Penurunan harga tanpa pelepasan OI besar. Tidak ada reclaim harga 4D yang terkonfirmasi.

**ETH:** Harga turun dan OI koin bertambah, tetapi OI tidak membuktikan posisi yang dominan long/short.

**SOL:** Harga dan OI sama-sama turun. Pantulan belum terkonfirmasi.

**BNB:** OI koin -18,53%, harga -2,03%. Amati harga 4D reclaim; jangan otomatis menyebut bottom.

## Proyeksi hingga 9 Desember 2026 (30 hari, 5×6D)
**Model:** 30 analog historis per aset, P15/P50/P85; skenario, bukan data masa depan. Semua tanggal pukul 07.00 WIB: **15 Nov, 21 Nov, 27 Nov, 3 Des, 9 Des**. 4D CLOSED berikutnya **13 Nov**, 12D CLOSED berikutnya **21 Nov**.

| Aset | Harga acuan 9 Nov | P15 9 Des | P50 9 Des | P85 9 Des | OI koin P50 9 Des | OI USD P50 9 Des | Funding P50 9 Des | Ketepatan arah model historis |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BTC | $74.818 | $64.804 | **$77.665** | $92.337 | 34.686 | $2.569,76 juta | 0,002405 | 54,3% |
| ETH | $2.126,61 | $1.904,85 | **$2.156,73** | $2.678,91 | 667.563 | $1.455,22 juta | 0,004520 | 53,6% |
| SOL | $86,49 | $62,27 | **$85,99** | $118,38 | 3.507.679 | $315,61 juta | 0,000702 | 46,4% |
| BNB | $684,76 | $602,84 | **$663,88** | $726,74 | 67.287 | $47,16 juta | 0,001742 | 50,3% |

## Level dan aturan pembacaan
- **4D:** sensor perubahan harga dan pencarian reclaim/pivot sebelum memutuskan entry.
- **6D CLOSED:** keputusan setelah sinyal harga mendukung; jangan menganggap OI naik sama dengan LONG atau OI turun sama dengan SHORT.
- **12D CLOSED:** membedakan perubahan struktural dan pantulan sesaat.
- **OI koin-ekuivalen = OI USD / harga kontrak yang sama**. Ini normalisasi, bukan identifikasi kepemilikan short/long.
- **Funding** adalah rata-rata daily CLOSE dalam *satuan native Coinalyze*; bukan funding 8-jam aktual.
- **Keputusan tegas:** BTC **WAIT**, ETH **WAIT**, SOL **WAIT**, BNB **WAIT**. Fokus observasi **BNB flush** dan **ETH build-up**. Tidak ada harga eksekusi atau invalidasi baru yang bisa diturunkan dengan andal dari data OI sendiri.

## Keandalan
Audit historis rolling-origin: masing-masing 151 periode uji. Akurasi arah harga 30D: BTC 54,3%; ETH 53,6%; SOL 46,4%; BNB 50,3%. Ini tidak cukup untuk memastikan arah 1 bulan. Rentang P15–P85 dari analog bukan interval probabilitas terkalibrasi. Tidak memasukkan biaya, slippage, dan funding yang benar-benar dibayar.

## File proyek disimpan
- [MASTER V2 visual lama tetap utuh](https://github.com/imthequin2811-gif/radar-pisau-jatuh/blob/main/coinalyze/v2/MASTER_RADAR_OI_FUNDING_PRICE_2026-11-11.html)
- [Data V2 snapshot](https://github.com/imthequin2811-gif/radar-pisau-jatuh/blob/main/coinalyze/v2/RADAR_V2_OI_FUNDING_PRICE_DATA_2026-11-11.json)
- [MASTER V2 aturan](https://github.com/imthequin2811-gif/radar-pisau-jatuh/blob/main/coinalyze/v2/MASTER_LOCK_OI_FUNDING_PRICE_2026-11-11.md)
- [Salinan HTML SCAN 11 Nov](https://github.com/imthequin2811-gif/radar-pisau-jatuh/blob/main/coinalyze/v2/scans/SCAN_V2_OI_FUNDING_HARGA_2026-11-11.html)

## Kesimpulan akhir
**NO NEW POSITION / WAIT.** Tidak ada perubahan sinyal CLOSED dari scan master V2 sebelumnya. Kembali evaluasi 4D 13 Nov dan 6D 15 Nov 2026, seluruhnya pukul 07.00 WIB. Semua prediksi ke depan tetap **PROYEKSI**, bukan nilai CLOSED.
