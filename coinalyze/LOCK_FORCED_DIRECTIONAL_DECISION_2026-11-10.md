# USER LOCK — KEPUTUSAN PROAKTIF LONG/SHORT BERDASARKAN FAKTA (RADAR COINALYZE)
Tanggal: 10 November 2026
Status: USER-LOCKED, addendum. Jangan ubah tanpa persetujuan eksplisit pengguna.
Berlaku OTOMATIS untuk setiap scan, format, update, keputusan dan backtest tanggal tertentu yang memakai data OI/funding Coinalyze. User tidak perlu menulis "paksa masuk".

## Tujuan
**KOREKSI TERBARU PENGGUNA (10 November 2026):** "Jangan saya yang paksa, tapi kamu paksa dirimu dengan fakta data, timing, TF." Artinya asisten **sendiri yang wajib memulai penilaian dan memilih bias/arah terbaik** dari bukti yang tersedia setiap kali melakukan scan; tidak menunggu user meminta "dipaksa masuk". Prioritaskan timing dan struktur timeframe yang telah ditentukan. Pilihan adalah penilaian/skenario, bukan perintah broker atau jaminan hasil.

Setiap scan berakhir dengan **keputusan proaktif**, tidak berhenti pada tabel indikator. Jika data cukup untuk menentukan bias, tulis **PILIHAN ARAH: LONG [aset] / SHORT [aset]**, lengkap dengan status **ENTRY SEKARANG / MENUNGGU TIMING** berdasarkan syarat harga dan candle yang dapat diverifikasi. Jangan memaksa eksekusi ketika setup buruk atau data tidak cukup: arah tetap bisa dipilih sebagai *bias hipotetis* dengan keyakinan rendah, tetapi tindakan berlabel **JANGAN ENTRY** dan alasan jelas. Bila data aktual tidak tersedia/valid, jangan mengarang arah maupun angka.

## Hierarki timeframe bila pengguna memakai SOP ini
- 4D CLOSED: aba-aba dan timing lebih awal; bukan pengganti keputusan 6D.
- 6D CLOSED: timeframe keputusan utama LONG/SHORT.
- 12D dan 18D CLOSED: konteks besar, zona, arah tekanan dan konflik.
- Jika pengguna secara eksplisit menentukan timeframe berbeda untuk keputusan, gunakan timeframe yang diminta; jangan diam-diam pindahkan keputusan ke timeframe lain.
- Candle custom reset 1 Januari 00:00 UTC; sumber Close; CCI18 pada OI/funding -> WMA6 dari CCI18. Jangan ubah indikator atau rumus.
- Bedakan harga, OI, funding; crossing CCI/WMA, perubahan slope WMA dan crossing garis 0 adalah fenomena yang berbeda.

## Output ringkas WAJIB untuk SETIAP SCAN (proaktif, tanpa disuruh)
1. **KEPUTUSAN MANDIRI: LONG [aset] atau SHORT [aset]** (pilih satu kandidat utama berdasarkan bukti), serta **STATUS TIMING: ENTRY / BELUM ENTRY** dan alasan konkret; tetap boleh menyatakan NO TRADE ketika tidak ada setup layak, tanpa menghilangkan bias yang terdukung.
2. **Tanggal keputusan, jam WIB, tanggal CLOSED terakhir tiap TF**, dan daftar data yang secara historis sudah tersedia *pada saat itu*. Jangan melihat masa depan (no look-ahead).
3. Bukti angka: CCI18, WMA6 prev→latest, ΔWMA, Δ²WMA, tiga sudut, crossing CCI/WMA OI/funding, harga/struktur dan konteks 12D/18D. Angka hanya jika data benar-benar tersedia/terverifikasi.
4. Tiga alasan terkuat pro-posisi dan dua hal yang dapat membantahnya; sebutkan jika OI dan funding menunjukkan positioning yang ambigu.
5. **Harga referensi entry dari sumber + tanggal yang tepat, level invalidasi berbasis struktur harga, dan kondisi batal**, tanpa membuat-buat harga live. Bila harga yang dapat dieksekusi belum ada, sebutkan bahwa entry adalah hipotetis, bukan fill aktual.
6. **Tingkat keyakinan (tinggi / sedang / rendah)** dan sumber keterbatasan (misalnya hanya satu kontrak exchange). Kalau sinyal lemah, label **"bias arah sementara, belum entry, keyakinan rendah"** alih-alih menyebutnya konfirmasi.
7. Untuk backtest, pisahkan secara ketat **KEPUTUSAN SAAT ITU** versus **HASIL SETELAHNYA**. Evaluasi setelah kejadian tidak boleh dipakai menentukan entry historis.
8. **Tidak mengeksekusi order.** Jika data pokok tidak tersedia atau file rusak, jangan menciptakan crossing atau angka; pilih arah hipotetis hanya bila ada dasar yang dapat diverifikasi, dan katakan dengan jelas jika belum dapat diputuskan berbasis data.
9. Jangan memakai kalimat penutup yang menghapus kesimpulan arah ("mungkin long mungkin short") ketika bukti sudah mendukung salah satu sisi. Pisahkan secara tegas **pilihan arah** dari **keputusan timing entry**. Tidak perlu user mengulang permintaan keputusan.

## Pemeriksaan timing wajib sebelum keputusan
- Mulai dari 18D dan 12D CLOSED untuk konteks TOP/TENGAH/BOTTOM, 6D CLOSED sebagai keputusan, 4D CLOSED sebagai aba-aba dan timing; periksa konflik antartimeframe, jangan mencampurkan candle RUNNING.
- Bandingkan arah **harga, OI dan funding**; identifikasi tekanan leverage, risiko squeeze dan kondisi ketika indikator naik tetapi harga gagal konfirmasi. Hindari asumsi semua OI naik = bullish atau funding negatif = otomatis long.
- Berikan tanggal candle CLOSED dan jadwal CLOSE berikutnya dalam WIB; simpulkan *timing sekarang* atau *menunggu candle/level harga*.
- Kelola kesalahan: data stale, gap, salah satuan funding, per kontrak vs agregat, atau crossing yang belum final harus menurunkan keyakinan dan dapat membuat NO ENTRY.
- Hindari hindsight: pada backtest buta per tanggal, hanya gunakan data yang sudah tersedia pada waktu keputusan, lalu sajikan hasil sesudahnya sebagai evaluasi terpisah.

## Preferensi visual dan format tetap terkunci
Master visual sebelumnya tetap menjadi acuan:
`coinalyze/MASTER_LOCK_VISUAL_6D_OI_FUNDING_2026-11-09.md`
Jangan ubah: navy #101b2b, 4 aset BTC kuning, ETH biru, SOL hijau, BNB ungu, hover, crossing ring, kartu prev/Δ/Δ²/angle, status warna, zona TOP/TENGAH/BOTTOM, hanya CLOSED. Output keputusan adalah **tambahan laporan setelah panel visual**, bukan alasan mengganti atau menghapus visual.

## Contoh yang sudah diberikan (bukan aturan entry otomatis)
Pada pembacaan blind sebelum 3 November 2026, asisten memilih **SHORT SOL**: kelemahan OI 4D/6D/12D, harga turun, funding WMA6 masih naik, dengan peringatan bahwa OI 18D belum bearish. Contoh ini tidak boleh digeneralisasi tanpa backtest lebih luas.

## Catatan integritas
Pengguna meminta inisiatif analitis dan keputusan lebih tegas, bukan penghilangan kejujuran atau batas keselamatan. Jangan menyatakan mampu menonaktifkan pengamanan, jangan mengarang dataset, jangan mengklaim keuntungan pasti. Keputusan tegas harus tetap bertumpu pada bukti historis yang tersedia. Tidak menempatkan order atau bertindak atas akun broker.
