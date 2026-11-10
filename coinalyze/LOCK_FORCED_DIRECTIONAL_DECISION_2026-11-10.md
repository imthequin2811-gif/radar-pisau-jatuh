# USER LOCK — KEPUTUSAN PAKSA LONG/SHORT (RADAR COINALYZE)
Tanggal: 10 November 2026
Status: USER-LOCKED, addendum. Jangan ubah tanpa persetujuan eksplisit pengguna.
Berlaku untuk permintaan "scan", "keputusan", "jika dipaksa masuk", "long atau short", dan backtest tanggal tertentu yang memakai data OI/funding Coinalyze.

## Tujuan
Pengguna meminta kesimpulan operasional yang tegas. Jika pengguna menginstruksikan *harus memilih posisi*, asisten wajib memutuskan **satu sisi: LONG atau SHORT** dari data dan timeframe yang diberikan, bahkan ketika indikator bercampur, bukan menolak membuat pilihan hanya karena sinyal belum sempurna. Pilihan adalah penilaian/skenario, bukan perintah broker atau jaminan hasil.

## Hierarki timeframe bila pengguna memakai SOP ini
- 4D CLOSED: aba-aba dan timing lebih awal; bukan pengganti keputusan 6D.
- 6D CLOSED: timeframe keputusan utama LONG/SHORT.
- 12D dan 18D CLOSED: konteks besar, zona, arah tekanan dan konflik.
- Jika pengguna secara eksplisit menentukan timeframe berbeda untuk keputusan, gunakan timeframe yang diminta; jangan diam-diam pindahkan keputusan ke timeframe lain.
- Candle custom reset 1 Januari 00:00 UTC; sumber Close; CCI18 pada OI/funding -> WMA6 dari CCI18. Jangan ubah indikator atau rumus.
- Bedakan harga, OI, funding; crossing CCI/WMA, perubahan slope WMA dan crossing garis 0 adalah fenomena yang berbeda.

## Output ringkas WAJIB untuk forced decision
1. **KEPUTUSAN PAKSA: LONG [aset] atau SHORT [aset]**, bukan jawaban abu-abu. Jika beberapa aset dibandingkan pilih **satu kandidat utama** dan jelaskan peringkat singkat.
2. **Tanggal keputusan, jam WIB, tanggal CLOSED terakhir tiap TF**, dan daftar data yang secara historis sudah tersedia *pada saat itu*. Jangan melihat masa depan (no look-ahead).
3. Bukti angka: CCI18, WMA6 prev→latest, ΔWMA, Δ²WMA, tiga sudut, crossing CCI/WMA OI/funding, harga/struktur dan konteks 12D/18D. Angka hanya jika data benar-benar tersedia/terverifikasi.
4. Tiga alasan terkuat pro-posisi dan dua hal yang dapat membantahnya; sebutkan jika OI dan funding menunjukkan positioning yang ambigu.
5. **Harga referensi entry dari sumber + tanggal yang tepat, level invalidasi berbasis struktur harga, dan kondisi batal**, tanpa membuat-buat harga live. Bila harga yang dapat dieksekusi belum ada, sebutkan bahwa entry adalah hipotetis, bukan fill aktual.
6. **Tingkat keyakinan (tinggi / sedang / rendah)** dan sumber keterbatasan (misalnya hanya satu kontrak exchange). Kalau sinyal lemah tetapi dipaksa memilih, label **"pilihan bersyarat, keyakinan rendah"** alih-alih menyebutnya konfirmasi.
7. Untuk backtest, pisahkan secara ketat **KEPUTUSAN SAAT ITU** versus **HASIL SETELAHNYA**. Evaluasi setelah kejadian tidak boleh dipakai menentukan entry historis.
8. **Tidak mengeksekusi order.** Jika data pokok tidak tersedia atau file rusak, jangan menciptakan crossing atau angka; pilih arah hipotetis hanya bila ada dasar yang dapat diverifikasi, dan katakan dengan jelas jika belum dapat diputuskan berbasis data.
9. Jangan memakai kalimat penutup yang menghapus pilihan ("mungkin long mungkin short", "WAIT saja") ketika pengguna meminta keputusan paksa. Boleh membedakan pilihan paksa dari sinyal eksekusi terkonfirmasi.

## Preferensi visual dan format tetap terkunci
Master visual sebelumnya tetap menjadi acuan:
`coinalyze/MASTER_LOCK_VISUAL_6D_OI_FUNDING_2026-11-09.md`
Jangan ubah: navy #101b2b, 4 aset BTC kuning, ETH biru, SOL hijau, BNB ungu, hover, crossing ring, kartu prev/Δ/Δ²/angle, status warna, zona TOP/TENGAH/BOTTOM, hanya CLOSED. Output keputusan adalah **tambahan laporan setelah panel visual**, bukan alasan mengganti atau menghapus visual.

## Contoh yang sudah diberikan (bukan aturan entry otomatis)
Pada pembacaan blind sebelum 3 November 2026, asisten memilih **SHORT SOL**: kelemahan OI 4D/6D/12D, harga turun, funding WMA6 masih naik, dengan peringatan bahwa OI 18D belum bearish. Contoh ini tidak boleh digeneralisasi tanpa backtest lebih luas.

## Catatan integritas
Pengguna meminta keputusan lebih tegas, bukan penghilangan kejujuran atau batas keselamatan. Jangan menyatakan mampu menonaktifkan pengamanan, jangan mengarang dataset, jangan mengklaim keuntungan pasti. Keputusan tegas harus tetap bertumpu pada bukti historis yang tersedia.
