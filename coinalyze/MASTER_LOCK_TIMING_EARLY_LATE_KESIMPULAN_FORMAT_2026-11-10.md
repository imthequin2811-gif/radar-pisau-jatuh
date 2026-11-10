# MASTER LOCK — KESIMPULAN, TIMING EARLY vs LATE & FORMAT SCAN COINALYZE
**Tanggal persetujuan user:** 10 November 2026
**Status:** USER LOCKED / SAVE. Jangan ubah kecuali user memberi persetujuan eksplisit.
**Prioritas:** Addendum analitis dan pelaporan di atas SOP visual yang sudah disetujui; tidak mengganti/memodifikasi master lock lain, indikator, aset, layout atau kode workflow GitHub.

## Dokumen LOCK induk (wajib dipakai bersama)
- Visual persis: `coinalyze/MASTER_LOCK_VISUAL_6D_OI_FUNDING_2026-11-09.md`.
- Keputusan mandiri setiap scan: `coinalyze/LOCK_FORCED_DIRECTIONAL_DECISION_2026-11-10.md`.
- Sumber studi angka historis dan kesalahan sinyal: `coinalyze/research/TIMING_STUDY_EARLY_VS_LATE_2026-11-10.md`.
- Dataset: `data/coinalyze/` + `data/binance/{BTC,ETH,SOL,BNB}USDT_1D_source.csv`.

## LOCK 1 — Prinsip kesimpulan wajib
1. Asisten **mandiri memutuskan bias LONG atau SHORT terbaik**, aset utama, dan kapan timing entry **layak atau belum** berdasarkan **fakta**, **tanggal CLOSED**, dan **timeframe**. User tidak perlu mengetik "paksa".
2. Pilih **arah** tegas dari data. **Beda** antara "arah utama = LONG/SHORT" dan "eksekusi = ENTRY SEKARANG / MENUNGGU TIMING / NO ENTRY karena bukti tidak mencukupi". Jangan mengarang sinyal/level, mengklaim fill, atau mengambil risiko buta.
3. Sebelum menyimpulkan, cek **kondisi harga relatif ke awal gerakan** dan **perubahan laju**, agar tidak baru LONG sesudah kenaikan besar atau baru SHORT di dekat local low.
4. **18D dan 12D** = arah/zona/top–bottom/konteks besar; **6D CLOSED** = bias keputusan utama; **4D CLOSED** = sensor dini, SHOT 1 antisipatif, crossing dan perbaikan Δ²WMA. Gunakan timeframe lain hanya jika user minta.
5. Boleh mengambil **SHOT 1 antisipatif** dari 4D saat 6D mulai melandai/berbalik dan ada dukungan struktur harga, tanpa menunggu 6D CROSS untuk setiap ide; tetapi tidak boleh otomatis membalik posisi karena satu CROSS 4D melawan slope 6D/12D.
6. CCI(18, CLOSE dari metric OI/funding) lalu WMA6 pada CCI, **bukan pada harga**, custom 4D/6D/12D/18D reset tahunan 1 Januari 00:00 UTC. Wajib candle CLOSED terverifikasi; RUNNING dan proyeksi di panel terpisah.
7. **CROSS UP/DOWN** berarti CCI18 melintas WMA6 antara dua candle CLOSED, **bukan** WMA menembus nol, **bukan** WMA sekadar berubah slope.
8. Arah OI, funding, dan harga tidak identik. OI naik tidak otomatis bullish; funding melemah tidak otomatis SHORT. Data OI/funding bisa berasal dari **satu kontrak exchange**, bukan agregat seluruh exchange.
9. Semua rekomendasi hipotetis memuat harga referensi + tanggal data sumber, invalidasi berdasarkan harga, risiko squeeze/rebound, dan keyakinan tinggi/sedang/rendah. Hindari entry buruk walau bias arah jelas. Tidak melakukan order.
10. Backtest tanggal lampau harus memisahkan **KEPUTUSAN yang tersedia saat itu** dari **HASIL SESUDAHNYA**. Histori unduhan sekarang bukan snapshot yang direkam ketika pasar lampau; jangan mengklaim telah memvalidasi keuntungan hanya dari beberapa kasus.

## LOCK 2 — Kesimpulan hasil kajian tanggal (untuk dipelajari, bukan sinyal otomatis)
| Tanggal dan TF saat itu | Keputusan yang direkonstruksi | Fakta/timing utama | Hasil sesudahnya (evaluasi saja) |
|---|---|---|---|
| 24 Jun 2026 6D CLOSED | **LONG SOL antisipatif kecil** | OI 4D bawah -100 mulai naik; OI 6D WMA -113.8 -> -101.7, Δ+12.1, Δ²+42.2, CCI CROSS UP; 12D belum konfirmasi; funding 6D berlawanan | SOL Spot 24 Jun $69.71 -> 6 Jul $81.59 (+17.04%) |
| 16 Sep 2026 6D CLOSED | **LONG ETH** | OI 4D CROSS UP pada 14 Sep; OI 6D WMA 80.5 -> 92.5, Δ+11.9; 12D Δ+16.2, 18D Δ+18.6 | ETH Spot 16 Sep $2,398.26 -> 22 Sep $2,776.19 (+15.76%) |
| 18 Sep 2026 4D CLOSED | **LONG BTC SHOT 1** | BTC 4D OI dan funding CROSS UP; 6D CLOSED 16 Sep WMA 52.1 Δ+0.5 (laju hampir datar); 12D/18D WMA negatif tetapi naik | BTC Spot 18 Sep $76,417.01 -> 22 Sep $86,620 (+13.35%) |
| 22 Sep 2026 6D CLOSED | **Jangan kejar LONG ETH; bias SHORT bersyarat** | ETH sudah naik +15.76% sejak 16 Sep, OI 6D kuat +131.4; funding 6D Δ-20 dan 4D funding CROSS DOWN; **belum** ada konfirmasi harga/4D OI SHORT pada saat itu | ETH Spot 22 Sep $2,776.19 -> 28 Sep $2,688.65 (-3.15%) |
| 26 Sep 2026 4D CLOSED | **SHORT ETH antisipatif** | ETH 4D OI CCI CROSS DOWN (CCI91.8 < WMA115.3); crossing 6D menyusul 28 Sep, meskipun slope WMA6 masih positif saat itu | ETH Spot 26 Sep $2,691.61 -> 16 Oct $2,442.08 (-9.27%, arah short diuntungkan) |
| 9 Nov 2026 6D CLOSED | **SHORT SOL = bias; bukan market short di dekat low** | 4D OI CROSS DOWN; OI 6D 55.2 ->36.0, 12D 134.6 ->100.7; funding 6D CROSS DOWN; 18D OI masih naik; harga dekat 6D low $85.02 | Belum ada hasil untuk dijadikan bukti |

**Pelajaran false cross penting:** ETH 4D OI CROSS DOWN **18 Sep** tetapi Spot naik dari $2,447.28 menjadi $2,776.19 pada 22 Sep (+13.44%). Maka **4D saja tidak boleh otomatis memicu reversal besar** ketika 6D dan 12D mengarah berlawanan.

**Pelajaran late entry:** BTC 4D OI+funding CROSS UP 18 Sep lebih dini daripada 6D CROSS UP 22 Sep sesudah spot naik +13.35%. Menunggu semua TF sempurna kadang terlambat. Namun sebuah CROSS baru di area TOP sesudah harga melesat juga bisa menjadi jebakan mengejar pergerakan.

## LOCK 3 — Format visual dan susunan laporan pada setiap "scan"
**Jangan mengganti format lama; tambahkan kesimpulan proaktif di bawahnya sesuai urutan ini.**
1. **HEADLINE:** tanggal scan, waktu snapshot GitHub UTC/WIB, data CLOSED terakhir/next CLOSED 4D 6D 12D 18D. Jika data Coinalyze stale, tandai tegas. Jangan klaim live.
2. **01 — GRAFIK NAVY INTERAKTIF 6D OI 4 ASET:** sama PERSIS dengan MASTER LOCK visual: latar #101b2b, panel #142239; BTC #fbbf24, ETH #38bdf8, SOL #34d399, BNB #d8b4fe. Empat garis dalam satu chart, hover/klick titik tanggal & empat kartu sinkron; lingkar crossing; batas +200,+100,0,-100,-200 dan zona TOP/TENGAH/BOTTOM; chips tanggal 24 Jun,16 Sep,22 Sep,latest (ubah chip latest bila tanggal CLOSED baru). Tetap responsif pada ponsel. Jangan ubah heading/urutan.
3. **02 — ONE-VIEW 6D OI + FUNDING:** per aset CCI18, WMA6 prev→latest, Δ, Δ², tiga sampel sudut, crossing CCI/WMA dengan tanggal CLOSED, status tekanan 🔴/⚫/🟢/🟠 sesuai lock visual. Jangan menyebut semua Δ negatif sebagai crossover baru.
4. **03 — KONTEKS 4D/12D/18D:** WMA prev→latest, Δ, Δ² dan zona; jadwal close WIB. Jika user meminta studi tanggal, pisahkan CLOSED 4D 22 Jun/18 Sep dari CLOSED 6D 24 Jun/22 Sep.
5. **04 — TIMING DECISION secara PROAKTIF:** pilih **SATU aset**, **LONG/SHORT**, alasan angka tertulis, tiga pro dan dua kontra, status EARLY/CONFIRM/LATE, entry sekarang atau menunggu level, invalidasi, risiko serta keyakinan. Jangan menunggu user "memaksa".
6. **05 — SKENARIO TANGGAL 1 BULAN:** berdasarkan jadwal CLOSED 6D, skenario naik/turun + apa yang membatalkan tesis, bukan angka prediksi/garis RUNNING hasil karangan.
7. **Sumber dan arsip:** tautan file `metadata.json`, `RADAR_OI_FUNDING_CCI18_WMA6.csv`, `data/coinalyze/history`, dan ringkasan scan jika disimpan. Pisahkan harga spot Binance dan indikator futures Coinalyze.

## LOCK 4 — Rambu integritas
- Jangan mengubah, menghapus, menyusun ulang aset/warna/grafik/kartu/indikator/candle reset yang sudah user lock tanpa persetujuan.
- Jika data valid tidak ada untuk keputusan tertentu, jangan membuat nilai atau crossing. Pilih bias hipotetis hanya ketika ada bukti, dan beri tingkat keyakinan.
- Grafik yang menggambar WMA6 boleh ditampilkan langsung dalam chat, namun arsip Markdown GitHub hanyalah **spesifikasi/hasil analisis**, bukan file aplikasi interaktif yang bisa diklik kecuali implementasi tersendiri dibuat.
- Hasil pada contoh historis bersifat selektif, **bukan backtest semua sinyal**. Jangan mengklaim winrate, profit factor, keuntungan bersih, atau bukti kinerja tanpa uji keseluruhan tanggal/sinyal.
