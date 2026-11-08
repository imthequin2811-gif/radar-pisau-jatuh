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

## LOCK SEMENTARA REVISI B + C (8 Nov 2026) — DISETUJUI PENGGUNA (opsi 1, 2, 3)

- **Jangan tampilkan CCI dan WMA terpisah sebagai grafik utama.** Pakai **satu chart** dua garis: **B = GAP (CCI18 - WMA6)** dan **C = WMA6(CCI18)**; TF **6D CLOSED** tetap. Chart harus mudah diarahkan mouse ke masing-masing tanggal, bukan dashboard HTML eksternal.
- Periode eksplorasi minimal **1 Jan 2022 s.d. CLOSED terakhir** dengan pemilih **2022 | 2023 | 2024 | 2025 | 2026** agar titik tidak bertumpuk. Default = tahun sekarang; jendela 4 bulan boleh sebagai zoom tambahan, bukan mengganti tampilan tahun.
- **Label visual minimal dan tegas:** jika CCI cross WMA dari bawah ke atas saat **WMA6 ≤ -100**, tampilkan simbol / label **AKUMULASI?**; bila cross dari atas ke bawah saat **WMA6 ≥ +80**, **EXIT?**. Ini label *kandidat studi* untuk BTC/crypto, bukan order; crossover biasa tetap terekam di tabel tetapi tidak memenuhi grafik.
- Warna sinyal: kandidat akumulasi hijau, kandidat exit merah; crossing normal diberi penanda kecil netral atau cukup tabel. Kedua garis GAP dan WMA selalu terlihat bersamaan. Level referensi: GAP = 0; WMA = −100 / +80 (level tidak boleh disamakan sebagai harga).
- **Hover/titik** sebaiknya menampilkan tanggal CLOSED 6D UTC / WIB, GAP, WMA6, CCI18, cash kapitalisasi US$B dan Δcash 6D (kalau didukung); tanggal tidak boleh digeser ke awal candle. Klik untuk memilih tahun dan melihat daftar POI di bawah.
- Sertakan **tiga sampel CLOSED terakhir**, ΔWMA, Δ²WMA, sudut, panah. Sinyal harus dihitung dari raw history dengan warm-up lintas tahun, bukan dari 4 bulan saja.
- Metode B terverifikasi dari dataset GitHub. **Metode A (TOTAL−TOTALES) tetap MISSING** sampai TradingView CSV tersedia. Jangan salin B sebagai A.
- Satu peringatan metodologis: *akumulasi* / *exit* di sini hanya tag eksperimen berdasarkan kapitalisasi stablecoin, bukan otomatis BUY/SELL BTC. Konfirmasi BTC belum diuji dalam radar ini.
- Jangan ubah format B+C terkunci sementara atau parameter CCI18/WMA6/6D tanpa persetujuan.

## LOCK GRAFIK B+C DIKOREKSI — 8 NOVEMBER 2026
Pengguna mengonfirmasi LOCK untuk format gabungan GAP + WMA6 + ZERO yang telah dikoreksi. **Histori 2022 sampai candle 6D CLOSED terbaru WAJIB ada pada setiap scan** (2022, 2023, 2024, 2025, 2026, dan tahun berikutnya), tidak hanya 4 bulan.

1. SATU grafik interaktif dalam chat: B = GAP (CCI18 - WMA6 on CCI); C = WMA6 pada CCI18; referensi horizontal ZERO = 0. Gunakan pemilih SEMUA dan masing-masing tahun supaya mouse/hover tanggal mudah dipakai. Jangan menggantikan format dengan dashboard HTML eksternal.
2. Sinyal crossing yang benar hanya saat GAP melintasi ZERO (CCI18 cross WMA6). Crossing garis GAP dengan garis WMA BUKAN sinyal. Belokan WMA hanya slope/momentum.
3. Gunakan tanggal kolom close_utc asli dari data/crypto_cash/B_6D_HISTORY.csv. Jangan konstruksi tanggal dari indeks titik; candle akhir tahun bisa kurang dari 6 hari dan harus diberi label sesuai panjang sesungguhnya. Tutup 00:00 UTC = 07:00 WIB.
4. Label kandidat AKUMULASI? hanya jika CROSS_UP dan WMA6 <= -100, dan EXIT? jika CROSS_DOWN dan WMA6 >= +80. Itu hipotesis likuiditas, belum valid sebagai keputusan BUY/SELL BTC.
5. Selalu sertakan ringkasan tiga sampel CLOSED terakhir: cash, perubahan nominal, GAP, CCI18, WMA6, delta WMA, delta2 WMA, sudut, panah, tgl close terakhir/berikutnya. B = DefiLlama; A = TOTAL - TOTALES tetap MISSING bila TradingView CSV belum tersedia.
6. Grafik sejarah sejak 2022 tidak boleh dihilangkan saat menyajikan zoom empat bulan. Format, indikator CCI18/WMA6, TF 6D CLOSED tidak boleh diubah tanpa izin pengguna.

## LOCK TAMBAHAN — FILTER ZONA EKSTREM & TABEL TANGGAL 6D (8 Nov 2026)

Pengguna menyukai tabel ZERO Crossing dengan checkbox Hanya zona ekstrem, tanggal CLOSED 6D dan WMA4; minta aturan visual dibedakan dan dikunci. Ini adalah lapisan EXPERIMEN CCI12/WMA4 6D, tanpa mengganti LOCK CCI18/WMA6 Metode B utama.

- Wajib tampilkan dan pertahankan toggle **Hanya zona ekstrem**, aktif secara default saat mengulas crossing. Semua tanggal merujuk pada **close_utc** candle custom 6D dengan reset 1 Januari 00:00 UTC / 07:00 WIB; tidak boleh merekonstruksi tanggal dari indeks jika close_utc tersedia.
- Semua crossing dicari dari GAP = CCI12 - WMA4(CCI12) yang berganti tanda melintasi ZERO pada CLOSED, bukan persilangan dengan kurva WMA4.
- **FILTER ekstrem yang disetujui (jangan diam-diam ganti)**: hanya CROSS_DOWN saat WMA4 >= +80 (TOP) dan CROSS_UP saat WMA4 <= -100 (BOTTOM). Crossing lain disembunyikan bila filter aktif. User bisa mematikan checkbox untuk lihat semua.
- Tambahkan kolom ZONA dan ΔWMA4 / arah WMA4, tanpa menghilangkan kolom asli tanggal CLOSED 6D, arah crossing, GAP, WMA4. Band zona TOP awal: +80 sampai kurang dari +100, TOP ekstrem: +100 sampai kurang dari +150, TOP sangat ekstrem: +150 atau lebih. BOTTOM ekstrem: -100 sampai lebih dari -150, BOTTOM sangat ekstrem: -150 atau kurang. Di antaranya netral.
- Tanggal studi yang diberi tanda oleh pengguna: 2025-04-07 (CROSS_DOWN, WMA4 ~121.33, ΔWMA4 +3.91); 2025-06-24 (~107.61, ΔWMA4 -5.80); 2025-12-21 (~105.88, ΔWMA4 +8.69). **Ketiganya TOP ekstrem**, namun perhatikan beda SLOPE: 24 Juni negatif, dua lainnya positif. Zona dan slope tidak menjamin profit, hanya petunjuk momentum stablecoin.
- Dua warna keluarga: zona TOP merah/oranye; zona BOTTOM hijau. Tingkat ekstrem wajib dapat dibaca dalam teks/angka, tidak bergantung pada warna saja. Penanda ↑/↓ membedakan slope (WMA naik/turun) dari crossing GAP.
- **CATATAN DATA**: uji CCI12/WMA4 yang tampil sekarang bersumber dari kapitalisasi stablecoin Metode B, BUKAN Metode A. Jangan labeli sebagai hasil A, sebab pasangan seri TradingView TOTAL dan TOTALES belum tersedia. Setelah data A diperoleh, terapkan format sama pada A yang asli.
- Format dengan filter zona ekstrem, tanggal, dan tingkatan ini LOCK; mengubah ambang batas filter, rumus atau tampilan tanggal memerlukan persetujuan pengguna.

## Penyempurnaan LOCK: tanggal titik ZERO Crossing bisa dibaca langsung (8 November 2026)
- Tooltip/chart bawaan yang hanya menunjukkan GAP/WMA/ZERO tanpa tanggal dianggap TIDAK memadai. Grafik harus memungkinkan pointer mouse memunculkan tanggal CLOSED 6D yang besar dan jelas di atas/di dekat titik, bukan perlu ditanyakan ke asisten.
- Di atas grafik tampilkan tanggal yang sedang disorot, zona (TOP ekstrem, BOTTOM ekstrem, atau tengah), status CROSS UP/DOWN atau bukan crossing, nilai GAP, WMA4, delta WMA4; sentuh/geser pointer untuk eksplorasi, klik untuk menahan pilihan jika memungkinkan.
- Tetap sediakan daftar tanggal crossover dengan filter Hanya zona ekstrem. 07 April, 24 Juni dan 21 Desember 2025 harus dapat dipelajari secara independen.
- Catatan data wajib terlihat: seri CCI12/WMA4 yang telah ditampilkan adalah turunan Metode B (stablecoin), hanya proksi pembanding selama data asli A (TOTAL−TOTALES) tidak ada. Jangan salah sebut data proksi sebagai A.
