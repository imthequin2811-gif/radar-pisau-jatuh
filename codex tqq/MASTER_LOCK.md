# MASTER LOCK — CODEX TQQ

Status: **DIKUNCI atas instruksi pengguna, 18 November 2026 (WIB)**.
Versi: **v5 — TQQQ / VIX / NDTH / DXY, histori NDTH lengkap**.

[Buka dashboard master](MASTER_LOCK/radar-tqqq.html)

## Aturan penyimpanan

Master adalah salinan identik HTML v5 yang telah diberikan kepada pengguna. Jangan ubah atau timpa master. Pekerjaan berikutnya harus memakai salinan dan nomor versi baru di luar `MASTER_LOCK/`. Perubahan master hanya jika pengguna meminta pembukaan kunci secara eksplisit.

Desain, kode, rumus, dan snapshot data di arsip dibekukan. HTML tetap memiliki pembaruan data GitHub yang sudah ada; angka yang tampil saat tersambung internet dapat berubah tanpa mengubah file master. NDTH tetap data akhir sesi, bukan real-time.

## Konfigurasi yang dipertahankan

- Empat instrumen sejajar: TQQQ, VIX, NDTH, DXY.
- Baris 6D: CCI18(CLOSE) / WMA6(CCI).
- Baris 12D: CCI9 / WMA3 sebagai sensor; pilihan pembanding CCI18 / WMA6.
- Detail 4D, daftar crossing, harga historis kecil, skala CCI bersama, serta kursor tanggal tersinkron.
- Candle kalender 4D/6D/12D berjangkar 1 Januari UTC, dengan warm-up berlanjut lintas tahun. Keputusan memakai CLOSED; RUNNING tidak menjadi konfirmasi final.
- Proyeksi CCI 100 hari kalender dari CLOSED terakhir memakai patokan tetap, tren teredam, pengembalian ke nol, dan gelombang teredam. Bobot diuji secara berjalan tanpa data masa depan; WMA diturunkan dari rangkaian CCI. Rentang galat bukan probabilitas terkalibrasi atau jaminan keuntungan.
- Histori NDTH yang disimpan: 5.024 sesi, 29 Desember 2006–16 November 2026. Sebanyak 11 sesi cocok dengan EODData dan 50 sesi cocok dengan ekspor TradingView di GitHub. Pemeriksaan ini tidak mengaudit setiap observasi historis secara independen.
- Data aktual INDEX:NDTH; tanpa substitusi NDX, proksi konstituen saat ini, atau harga buatan.

## Integritas dan asal versi

SHA-256 HTML: `0e4765a14e57ba322abdd6b68c60d7f3cb161487cbd0b590b1ab0af41ee326a6`.

[Versi sumber yang dipatok pada commit](https://github.com/imthequin2811-gif/radar-pisau-jatuh/blob/4ffc9450524584d0807e48ffb8bdcefc7370986c/radar_tqqq/radar-auto.html).

`SHA256SUMS` pada folder ini memeriksa file HTML utama. Salinan lokal dan ZIP juga menyimpan kode sumber, data JSON/CSV, collector, audit NDTH, serta skrip validasi dalam `MASTER_LOCK/`. Skrip build dan uji tersebut disimpan apa adanya; sebagian masih memakai path workspace aslinya dan harus dijalankan atau disesuaikan pada salinan kerja, bukan dengan mengubah master.

Validasi sebelum penguncian: hitungan indikator dan kalender, delapan panel, kursor tersinkron, proyeksi tanpa look-ahead, WMA proyeksi, pemuatan dari file lokal, fallback offline, serta sembilan pemeriksaan collector/backfill telah lulus. Penguncian ini diverifikasi dengan kecocokan byte dan checksum, tanpa mengubah implementasi.
