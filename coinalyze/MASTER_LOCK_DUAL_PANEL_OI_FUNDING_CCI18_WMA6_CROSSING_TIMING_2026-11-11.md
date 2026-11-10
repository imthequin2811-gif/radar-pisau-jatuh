# MASTER LOCK — DUAL PANEL OI + FUNDING, CCI18 × WMA6, CROSSING & TIMING
**Persetujuan pengguna:** "versi yang ini kamu pakai IO [OI], funding di kasih cci 18 wma 6, crosing timing tf" kemudian **"save, lock"**. Disimpan 11 November 2026.
**STATUS: USER-LOCKED ADDENDUM.** Pertahankan sampai pengguna memberi izin perubahan. Tambahan, bukan pengganti MASTER LOCK lain.

## 1. Desain dan sumber angka yang DIKUNCI
1. **Dua panel besar yang mudah dibaca:** **Panel 01 OPEN INTEREST → CCI18 → WMA6** di atas dan **Panel 02 FUNDING → CCI18 → WMA6** di bawah, untuk instrumen BTC, ETH, SOL, BNB (contoh awal BTC).
2. Untuk masing-masing panel, **CCI(18) dari CLOSE data metrik Coinalyze** (OI atau funding) di candle custom, lalu **WMA(6) dari CCI18**, **BUKAN CCI harga Binance**, bukan WMA6 harga, bukan membandingkan OI mentah terhadap funding mentah. Kedua panel dihitung **secara independen**.
3. Timeframe: tombol **4D sensor/ABA-ABA**, **6D keputusan utama**, **12D gelombang besar**, dengan reset tahunan pada **1 Januari 00:00 UTC**. **CLOSED only** untuk semua crossing dan kesimpulan. Konteks 18D dari radar lain dipertahankan tanpa menggantinya.
4. Format visual: navy `#101b2b` dan `#142239`, **CCI18 cyan #38d9ff**, **WMA6 kuning #fbbf24**, CROSS UP lingkar hijau #4ade80, CROSS DOWN lingkar merah #fb7185, grid zona **+200, +100, 0, -100, -200**, tanggal mudah terlihat, *hover/klick* tanggal menampilkan nilai OI CCI/WMA dan Funding CCI/WMA yang benar dan timestamp WIB. Garis jangan terlalu tipis/kecil; seminimal mungkin keterangan tidak penting.
5. **CROSSING =** CCI18 metrik yang *menyeberang* WMA6 metrik antara dua candle CLOSED. **PRA-CROSS =** CCI mendekati WMA sebelum cross final. Perubahan slope WMA, crossing garis nol, dan crossing CCI↔WMA **tiga kondisi berbeda**, jangan dicampur.
6. **Timing/keputusan proaktif:** asisten mengidentifikasi sinyal **EARLY 4D**, **CONFIRM 6D**, **KONTEKS 12D** serta apakah entry **EARLY/CONFIRM/LATE**. Kombinasi OI+Funding CROSS UP/DOWN yang *searah* adalah sinyal pendukung, bukan jaminan arah harga, bukan kewajiban entry.
7. **Divergensi pada panel OI:** bandingkan pivot OI mentah dengan CCI18 yang dihitung dari OI, bukan dengan CCI harga. Divergensi funding bisa dibandingkan terpisah jika bukti pivot valid. Pivot tidak terkonfirmasi sebelum candle kanan CLOSED; hindari garis/pivot/angka rekaan.
8. **Garis bayangan hijau/merah 30–60 hari** berada **setelah batas CLOSED vertikal**, memakai skenario sintetis CCI OI dan CCI funding yang terpisah, lalu menghitung lintasan WMA6 dari tiap asumsi CCI. **JANGAN** diartikan target harga, prediksi pasti, maupun data masa depan.
9. **Harga Binance spot hanya validasi kedua**, untuk membahas apakah pergerakan harga masih sesuai dengan area ekstrem entry pengguna, level retest, invalidasi dan timing. **Jangan mengambil nilai CCI/WMA dari harga untuk mengganti panel OI/Funding.**
10. **Kesimpulan harus menyebut satu pilihan arah LONG/SHORT** bila data mendukung, beserta tingkat keyakinan, tetapi bedakan dengan **STATUS ENTRY: bisa entry / NO ENTRY** jika area ekstrem/trading pribadi belum terpenuhi. Jangan mengarang harga, mengubah limit user, atau melakukan order.

## 2. Contoh bacaan CLOSED 9 Nov 2026 pada BTC — snapshot, bukan angka live permanen
| TF | OI CCI18 | OI WMA6 | OI fresh CROSS | Funding CCI18 | Funding WMA6 | Funding fresh CROSS |
|---|---:|---:|---|---:|---:|---|
| 4D | +58.45 | +99.79 | DOWN 9 Nov | -83.14 | +18.79 | Sudah DOWN 5 Nov; bukan baru 9 Nov |
| 6D | +74.69 | +95.61 | DOWN 9 Nov | -70.64 | -20.09 | DOWN 9 Nov |
| 12D | +72.88 | +70.35 | Belum CROSS DOWN | -21.02 | +36.05 | DOWN 9 Nov |

Catatan: 4D pada 12 Okt 2026 OI CCI +88.88 < WMA +121.88 dan Funding CCI -138.2 < WMA -39.4, keduanya CROSS DOWN; ini **contoh peringatan awal**, bukan bukti bahwa setiap crossing dua metrik menghasilkan SHORT berhasil. 12D OI masih positif pada 9 Nov berarti risiko sinyal bearish belum sepenuhnya selaras.

## 3. Urutan output SCAN tetap
- Panel navy empat aset WMA6 6D gabungan yang sudah USER-LOCKED **tidak dihapus**.
- **Tambahkan** sesudahnya panel besar **OI + Funding CCI18/WMA6 dua tingkat** dengan pilihan aset dan TF 4D/6D/12D, crossing/historical date dan skenario warna berbeda.
- Tabel one-view 4D/6D/12D/18D (untuk metrik yang memiliki data), delta WMA, delta², tiga sudut, zona, dan jadwal close WIB tetap mengikuti LOCK utama.
- Akhiri dengan **putusan arah + validitas timing + invalidasi** menurut area ekstrem dan CLOSED. Bukan trading otomatis.
- Snapshot grafik interaktif disimpan pada `coinalyze/visuals/MASTER_LOCK_DUAL_PANEL_OI_FUNDING_CCI18_WMA6_4D_6D_12D.html`. Saat dataset terbaru tersedia, harus diregenerasi tanpa mengubah desain atau mengganti data lama dengan data asumsi.

## 4. Referensi LOCK yang DILINDUNGI
- `coinalyze/MASTER_LOCK_VISUAL_6D_OI_FUNDING_2026-11-09.md`: grafik gabungan empat aset, tidak diganti.
- `coinalyze/MASTER_LOCK_AREA_EKSTREM_CCI_GELombang_CROSSING_TAMBAHAN_2026-11-10.md`: lokasi entry, intuisi 4D, 6D, tambahan crossing.
- `coinalyze/MASTER_LOCK_TIMING_EARLY_LATE_KESIMPULAN_FORMAT_2026-11-10.md`: urutan laporan dan keputusan proaktif.
- `coinalyze/visuals/MASTER_LOCK_OI_CCI18_WMA6_4D_6D_12D_CROSS_DIVERGENCE.html`: grafik OI-only terdahulu tetap tersedia.

**Larangan mengubah tanpa persetujuan:** indikator, parameter, TF, reset, warna, urutan panel, status CLOSED, jenis metrik, arti crossing, klaim bayangan sebagai fakta, dan strategi transaksi pengguna.
