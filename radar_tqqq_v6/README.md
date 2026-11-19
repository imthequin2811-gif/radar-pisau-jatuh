# Radar TQQQ v6 — SCAN offline

Versi kerja baru, 19 November 2026. MASTER LOCK v5 tidak diubah.

Buka `radar-tqqq-v6-scan.html` langsung di browser. Tidak perlu login, instalasi, server, atau API key. Snapshot, CSS dan JavaScript ada di satu file. SCAN memerlukan internet; saat offline snapshot terakhir tetap tersedia dan umur data dihitung ulang. Setelah SCAN, tekan **Simpan HTML offline** untuk membawa snapshot terbaru ke file unduhan. Penyimpanan cache browser bersifat tambahan; dukungannya pada file:// berbeda antar-browser.

## Membaca radar

- Aba-aba teratas: kondisi terkini dari CLOSED aktual. **TAHAN KEPUTUSAN** saat data TQQQ belum layak; **DEFENSIF — JANGAN TAMBAH** saat CCI 6D di bawah WMA yang turun; **SIAGA** saat 4D membaik tetapi 6D belum memenuhi syarat; **SIAPKAN ENTRY — BERSYARAT** jika aturan indikator terpenuhi, lalu validasi rencana, R:R dan harga pemicu. Tidak ada order otomatis atau probabilitas kemenangan.
- 4 kolom TQQQ / VIX / NDTH / DXY, 3 baris: 4D CCI18/WMA6, 6D CCI18/WMA6, 12D CCI9/WMA3. Harga historis berupa strip kecil di atas.
- Cursor tanggal bersama: geser atau pakai keyboard/pemilih tanggal. Patok **A**, geser ke **B**, baca perubahan CCI/WMA. Ringkasan replay terpisah dari keputusan terkini.
- Histori 4/8 bulan, 1/2 tahun, tahun lalu, semua histori. Tombol ±4 bulan dan batas tanggal replay. Semua histori mencakup Treasury sejak 1990; panel market menampilkan data hanya sejak sumber masing-masing tersedia.
- Mode **02A**: G = abs(CCI−WMA), selalu nonnegatif. LV0 <10, LV1 <25, LV2 <50, LV3 <100, LV4 <200, LV5 ≥200. Level mengukur jarak, bukan arah atau probabilitas reversal.
- Inersia 24 hari memproyeksikan signed gap dari tiga CLOSED terakhir, meluruhkan kecepatan/percepatan, lalu menampilkan nilai absolut. Proyeksi 100 hari dari master tetap tersedia sebagai riset tambahan, dengan galat historis dan model patokan. Keduanya skenario, bukan pemicu entry.
- Tambahan filter v6 yang belum dibacktest: jangan kejar ketika 4D CCI >100, di atas WMA, dan gap ≥100; mode awal juga ditahan ketika 6D jelas melemah. Mesin inti v5 tetap byte-identik. 12D, VIX, NDTH, dolar dan yield merupakan konteks, bukan voting otomatis.
- Posisi saya hanya pilihan eksplisit pengguna. Peringatan stop membutuhkan pilihan sudah memegang, stop valid, dan quote bertimestamp ≤15 menit. Tetap periksa eksekusi di broker.

## Data dan SCAN

Market: `https://raw.githubusercontent.com/imthequin2811-gif/radar-pisau-jatuh/main/data/tqqq_radar/market-data.json`

Treasury: `https://raw.githubusercontent.com/imthequin2811-gif/radar-pisau-jatuh/main/data/tqqq_radar/bonds.json`

TQQQ memakai Yahoo Finance TQQQ, VIX memakai histori resmi Cboe dan quote terpisah, DXY memakai Yahoo DX-Y.NYB. NDTH adalah **INDEX:NDTH aktual**, arsip TradingView sejak 29 Desember 2006 dan pembaruan EODData; bukan NDX atau rekonstruksi breadth. Data NDTH tetap EOD.

Treasury memakai feed XML resmi U.S. Treasury: <https://home.treasury.gov/treasury-daily-interest-rate-xml-feed>. Snapshot awal v6 memuat 9.226 observasi, 2 Januari 1990–18 November 2026, tujuh tenor 2Y/3Y/5Y/7Y/10Y/20Y/30Y. Seluruh 37 tahun dicocokkan ke feed resmi; tidak ada perbedaan pada baris arsip Bond yang saling beririsan. Nilai null dipertahankan. Jeda penerbitan >31 hari memulai warm-up baru; chart tidak menyambung jeda panjang. CCI dihitung dari yield, bukan harga obligasi.

Workflow market lama tetap dipakai, jadwal ±15 menit. Workflow v6 Treasury terpisah berjalan pada menit 35 pukul 00/06/12/18 UTC hari kerja; GitHub dapat menunda jadwal. Browser memeriksa feed tiap 60 detik atau lewat SCAN. SCAN mengambil publikasi pipeline terakhir, bukan menjamin tick real-time atau memaksa penyedia menerbitkan data baru. Kegagalan salah satu sumber mempertahankan snapshot sebelumnya dengan pesan gagal. Timestamp/data yang mundur atau dari masa depan ditolak.

Batas kesegaran TQQQ mengikuti master: umur EOD maksimum 96 jam; bukan validasi lengkap kalender bursa. Replay memakai revisi data terbaru, bukan arsip vintage yang diketahui pada tanggal lampau. Tidak ada bukti profitabilitas dari aturan keputusan ini.

## Validasi

- 11 uji numerik: ambang level, hierarki keputusan, missing plan, data basi/masa depan, no-chasing, cross/WMA berlawanan, stop, replay, batas tahun inersia, validasi feed dan warm-up Treasury.
- 5 uji parser Treasury: null/zero, rentang/nonfinite, hari belum selesai/masa depan, duplikat, kegagalan sumber menjaga arsip.
- Uji DOM offline: 12 panel, 4 strip harga, 7 tenor, cursor sinkron, A/B, cutoff historis, 02A, inersia, 100 hari, tidak ada NaN path, tanpa aset eksternal.
- Uji SCAN: data baru menghitung ulang keputusan, data mundur ditolak, kegagalan tidak menghapus snapshot, HTML simpanan terbuka offline dengan snapshot/keputusan baru.
- MASTER HTML SHA-256 tetap `0e4765a14e57ba322abdd6b68c60d7f3cb161487cbd0b590b1ab0af41ee326a6`.
- Verifikasi interaksi dilakukan melalui jsdom; pemeriksaan visual di browser nyata belum tersedia dalam sesi ini.

Kode dashboard, data tertanam, aturan dan CSS dapat dilihat langsung pada source HTML. Folder lokal versi ini juga berisi modul `dist/`, `build.py`, collector dan tests. `python build.py` membangun HTML tanpa menyentuh MASTER_LOCK.
