# 🎙️ 20 · Live Voice Script v2 — Fragment, Reaction Kit, SSML, Pronunciation (Cartesia TTS Optimized)

> **Status**: FINAL spec untuk generate audio library Cartesia 2 jam live.
> 

> **Posisi**: Ini *tactical execution layer* di atas [🎙️ Live Interaction Plan — 2 Jam Cartesia, Produk, Scene, Retensi](https://www.notion.so/Live-Interaction-Plan-2-Jam-Cartesia-Produk-Scene-Retensi-1267e9d752fa48ad847d1b2e778644a7?pvs=21) (strategic frame). Doc #86 tetap sebagai sumber persona + runsheet + guardrail. Doc ini fokus ke apa yang benar-benar di-TTS.
> 

> **Output target**: 220+ clip audio Cartesia, siap random-play via worker, human-ready untuk live 2 jam.
> 

<aside>
🎯

**Kenapa dokumen ini dibuat**: audit kritis terhadap doc #86 menemukan 10 gap untuk konteks live (fragment terlalu panjang, 0 reaction kit, 0 pronunciation guide, 0 SSML markup, energy datar, tidak ada bridge transition). Dokumen ini menutup semuanya dengan script yang siap paste ke Cartesia batch.

</aside>

---

## 1 · Prinsip Revisi (Kenapa v2 Berbeda)

| Aspek | v1 (doc #86) | **v2 (doc ini)** |
| --- | --- | --- |
| Disfluency natural | Tidak ada | **"eh", "hmm", "oke oke", "sebentar"** |
| Name mention slot | Tidak ada | **Ada, via placeholder {{name}}** |
| SSML markup | Tidak ada | **Template break/emphasis/speed** |
| Bridge antar produk | Tidak ada | **15 clip transition** |
| Total target clip | 160-220 | **220 final, terdistribusi lebih merata** |

---

## 2 · Pronunciation Guide (Wajib Tempel ke Prompt Cartesia)

Cartesia Sonic-3 bahasa Indonesia kadang salah baca nama produk dan singkatan teknis. Tulis ke prompt sebagai "pronunciation hint":

| Tulisan di script | Cara Cartesia harus baca | Workaround di script |
| --- | --- | --- |
| DLP 6000 | de-el-pe enam ribu | Tulis **"DLP enam ribu"** langsung |
| XHP160 | eks-ha-pe seratus enam puluh | Tulis **"XHP seratus enam puluh"** atau skip angka |
| USB-C | yu-es-be-se | Tulis **"port USB C"** |
| CCTV | se-se-te-ve | Tulis **"CCTV"** — Cartesia sudah handle oke |
| checkout | cek-aut | Aman — tapi preferred: pakai **"check out"** atau **"beli"** |

**Rule umum**: hindari angka + huruf campuran. Spell out manual. Kalau butuh spesifik model, sebut "model terbaru" atau "seri terbaru" saja.

---

## 3 · SSML / Markup Pacing Reference

Cartesia Sonic-3 support prosody control via special tokens. Template yang dipakai:

| Efek | Markup | Kapan dipakai | Jeda pendek (breath) | `...` (titik tiga) | Antar fragment, before hook word |
| --- | --- | --- | --- | --- | --- |
| Jeda sedang (thinking) | `, eh,`  atau `, hmm,`  | Saat pretend-mikir, natural filler | Jeda panjang (beat) | newline atau `.  .  .` | Setelah punchline, before CTA |
| Emphasis / stress | UPPERCASE kata kunci | Product name, action word | Speed slow (dramatis) | Tambah `.`  antar kata | Warning / safety line |
| Speed fast (excited) | Kalimat pendek 3-5 kata berentet | Celebrate, high moment | Question lift | Akhiri dengan `?` jelas | Pancing komentar |

**Contoh before/after**:

> **Before (v1)**: "Smart lock itu bukan cuma soal keren. Yang paling terasa justru saat kunci ketinggalan, anak pulang duluan, atau rumah sering ditinggal."
> 

> **After (v2)**: "Smart lock ya... ini bukan cuma keren-kerenan. Yang paling kerasa... pas kunci ketinggalan. Anak pulang duluan. Rumah kosong. Situasi kayak gitu."
> 

Jeda `...` jadi breath, fragment pendek = Cartesia tidak force-fill intonasi robotik.

---

## 4 · Struktur Folder Audio v2 (220 clip)

```
/apps/worker/static/audio_library/
├── A_opening/              12 clip (3 variasi × 4 tone: hook-problem, hook-question, hook-promise, hook-story)
├── B_reset_viewer/         20 clip (4 energy tier × 5 variasi)
├── C_paloma/               30 clip (context:20 + safety:5 + CTA:5)
├── D_cctv/                 25 clip (context:18 + safety:4 + CTA:3)
├── E_senter/               20 clip (context:15 + safety:3 + CTA:2)
├── F_tracker/              18 clip (context:14 + safety:2 + CTA:2)
├── G_question_hooks/       20 clip (20 pertanyaan distinct)
├── H_price_safe/           12 clip (single:6 + merged:6)
├── I_trust_safety/         10 clip
├── J_idle_filler/          15 clip (fragment pendek pretend-think)
├── **R_reaction_kit**/     **35 clip** (gift:8 + share:6 + follow:6 + join:6 + milestone:5 + merged_comment:4)
├── **T_bridge/**           **15 clip** (transisi antar produk)
├── **Z_closing_staged**/   8 clip (T-10:2 + T-5:2 + T-2:2 + T-30s:1 + T-0:1)
└── index.json              (auto-generate dari gen_audio_library.py)

TOTAL: 220 clip
```

---

## 5 · Script Library v2 per Kategori

### 5.1 · A_opening (12 clip — 4 hook types × 3 variasi)

**Hook tipe 1 — Problem statement (tonal: curious-concerned)**

```
Rumah kamu malam ini aman nggak? Pintu... teras... lampu darurat. Kita bahas satu-satu.
```

```
Kunci ketinggalan. Teras gelap. Paket hilang. Tiga masalah malam hari. Saya bedah pelan-pelan.
```

```
Malam ini saya nggak jual produk mewah. Saya bahas hal kecil yang bikin rumah lebih tenang.
```

**Hook tipe 2 — Pertanyaan langsung (tonal: engaging)**

```
Coba jawab di komentar... di rumah kamu, yang paling sering bikin was-was apa?
```

```
Titik paling lemah di rumah kamu... pintu, teras, atau penerangan? Saya penasaran.
```

```
Kalau harus beresin satu dulu... kamu pilih yang mana? Saya tunggu jawabannya.
```

**Hook tipe 3 — Promise / benefit (tonal: warm)**

```
Dua jam ini saya temanin ya. Kita ngobrol soal rumah aman... santai, nggak maksa beli.
```

```
Saya bongkar plus-minus empat barang rumah. Yang cocok ya cocok. Yang nggak, jangan dipaksa.
```

```
Goal saya simpel... kamu selesai nonton lebih paham rumah sendiri. Itu udah cukup.
```

**Hook tipe 4 — Story-driven (tonal: personal)**

```
Tadi malem teras rumah saya gelap banget. Keingetan senter. Dari situ saya mikir banyak hal.
```

```
Kemarin tetangga cerita paket raib di depan pintu. Nah... dari situ topik CCTV muncul.
```

```
Istri saya sering lupa kunci taruh mana. Kejadian sehari-hari. Ternyata ada solusinya.
```

---

### 5.2 · B_reset_viewer (20 clip — 4 energy tier)

**Tier HIGH (viewer masuk rame)** — pitch naik, cepat

```
Buat yang baru masuk... cepat saya ulang. Tema malam ini rumah aman... pintu, CCTV, senter, tracker. Ikut aja.
```

```
Halo yang baru join. Kita lagi bahas... pintu depan. Sabar ya, saya ulang konteksnya bentar.
```

**Tier MID (steady pace)** — natural

```
Kalau baru mampir, gampang. Kita lagi ngobrolin empat barang rumah... dari pintu sampai barang kecil.
```

```
Yang baru gabung... konteksnya simpel. Rumah aman malam hari. Pilih mana yang relevan buat kamu.
```

**Tier LOW (sepi, reflektif)** — pelan, humble

```
Oke pelan-pelan aja. Buat yang baru... saya jelasin ulang dari awal nggak apa-apa.
```

```
Mumpung santai... saya rewind konteks. Kita lagi di topik keamanan rumah. Tema sehari-hari.
```

*(14 variasi lagi dengan pola yang sama, mixed tier)*

---

### 5.3 · C_paloma (30 clip — context 20 + safety 5 + CTA 5)

**Context 20 — Fragment style**

```
Pintu depan. Titik pertama. Kalau ini lemah... sisanya percuma.
```

```
Smart lock ya... ini bukan cuma keren-kerenan. Yang paling kerasa pas kunci ketinggalan.
```

```
Anak pulang duluan. Orang tua tua lupa bawa kunci. Situasi kayak gitu yang bikin mikir.
```

```
Tapi jujur... smart lock bukan barang murah. Jangan beli cuma karena kelihatan modern.
```

```
Cek dulu... jenis pintu, ketebalan, metode buka. Tiga ini wajib.
```

```
Fitur sidik jari... sangat membantu. Terutama kalau di rumah ada banyak anggota keluarga.
```

```
Baterai habis... gimana? Ini pertanyaan penting. Harus ada akses darurat fisik.
```

```
Paloma DLP enam ribu... fokusnya keamanan berlapis. Bukan sekedar buka-tutup.
```

```
Kalau pintu kamu kayu tipis... smart lock pintar pun nggak maksimal. Pondasinya dulu.
```

```
Instalasi... ada yang DIY, ada yang harus teknisi. Tanya dulu sebelum checkout.
```

*(10 context lagi dengan variasi sudut: akses keluarga, rumah sering kosong, anak kecil, tamu menginap, emergency scenario, compare dengan kunci biasa, integrasi smart home, maintenance, kondisi lembab, kompatibilitas pintu existing)*

**Safety 5**

```
Saya nggak bilang ini anti maling mutlak. Nggak ada alat seratus persen. Itu jujur aja.
```

```
Kalau ragu... jangan dipaksa. Cek pintu kamu dulu, cocok apa nggak sama model ini.
```

```
Jaminan kunci darurat wajib ada. Kalau nggak ada... batalin aja. Serius.
```

```
Baca review jujur dulu. Bukan yang bintang lima aja. Baca yang bintang dua, tiga.
```

```
Bukan rekomendasi wajib. Kalau pintu kamu udah oke... nggak perlu paksa upgrade.
```

**CTA 5 — Soft**

```
Kalau tertarik... cek aja yang di keranjang kuning. Detail lengkapnya di situ.
```

```
Pengin tahu lebih... keranjang kuning ada. Baca spek sama review dulu ya, jangan langsung klik.
```

```
Saya taruh di keranjang... cek pelan-pelan. Nggak harus hari ini checkout-nya.
```

```
Buat yang cocok... keranjang kuning paling atas. Buat yang ragu... skip aja dulu.
```

```
Detailnya ada di keranjang. Harga bisa berubah, jadi saya nggak sebut di sini ya.
```

---

### 5.4 · D_cctv (25 clip — context 18 + safety 4 + CTA 3)

**Context 18**

```
Setelah pintu... teras. Area kedua yang sering dilupakan.
```

```
CCTV murah sekarang... udah cukup buat pantau depan rumah. Udah zaman lain dari dulu.
```

```
V tiga delapan puluh... dual lens, auto tracking. Intinya bisa ngejar objek yang gerak.
```

```
Night vision... wajib. Kalau CCTV siang oke malam buta, percuma.
```

```
Satu kamera di posisi bener... lebih berguna dari lima kamera pasang asal.
```

```
Koneksi WiFi rumah kamu stabil? Kalau sering putus... CCTV WiFi ya kejepit.
```

```
CCTV bukan cuma buat maling. Kadang cuma cek... paket udah sampai belum.
```

```
Anak pulang sekolah... lewat depan rumah. Notifikasi HP muncul. Tenang.
```

*(10 context lagi)*

**Safety 4**

```
Jangan rekam tetangga... itu pelanggaran privasi. Arahkan ke area rumah sendiri aja.
```

```
Simpanan cloud... cek dulu gratisnya berapa lama. Jangan kaget pas disuruh bayar.
```

```
Memory card... backup. Jangan mengandalkan satu metode aja.
```

```
Password aplikasi CCTV... ganti default. Serius. Jangan pakai admin123 terus.
```

**CTA 3**

```
Keranjang kuning ada. Cek spesifikasi dulu... resolusi, penyimpanan, aplikasi.
```

```
Kalau pas buat teras kamu... keranjang kuning. Kalau masih ragu... skip.
```

```
Baca detail di keranjang. Pastikan area rumah kamu WiFi-nya sampai.
```

---

### 5.5 · E_senter (20 clip — context 15 + safety 3 + CTA 2)

**Context 15**

```
Barang kecil yang diremehkan... senter.
```

```
Listrik mati... baru kerasa. Senter HP itu darurat banget.
```

```
Senter rumah yang layak... bukan cuma terang. Harus gampang dicas, gampang dicari.
```

```
Tahan hujan, tahan jatuh... itu dua kriteria utama. Selain terang.
```

```
XHP seratus enam puluh... type C charging. Udah nggak pakai baterai boros.
```

```
Rumah gelap... ambil senter... selesai. Manfaatnya nggak perlu dijelasin panjang.
```

*(9 context lagi: mode cahaya, durasi baterai, ukuran tangan, outdoor camping, cari barang di bawah sofa, cek meteran air, halaman motor mogok)*

**Safety 3**

```
Jangan dianggap lampu sorot proyek. Ini buat rumah, halaman, motor, camping ringan.
```

```
Senter murah banget tapi super terang... curiga dulu. Biasanya baterai bocor cepet.
```

```
Cas-nya pakai kabel type C yang bener... jangan asal colok. Senter mahal rusak gara-gara charger jelek.
```

**CTA 2**

```
Buat yang belum punya senter khusus... ini barang pertama yang masuk akal.
```

```
Keranjang kuning ada. Modelnya USB C charging, standar IPX enam.
```

---

### 5.6 · F_tracker (18 clip — context 14 + safety 2 + CTA 2)

**Context 14**

```
Barang kecil yang sering nyelametin pagi hari... tracker.
```

```
"Kunci tadi saya taruh mana ya"... masalah kecil. Tapi kalau tiap hari... capek.
```

```
Dings Smart Tracker... pakai bluetooth. Bunyi dari HP, ketemu.
```

```
Tapi perlu paham... ini bukan GPS mobil jarak jauh. Jangkauannya terbatas.
```

```
Buat cari barang di sekitar rumah... pas banget. Buat lacak mobil hilang... nggak bisa.
```

*(9 variasi lagi: cocok untuk dompet, tas, remote TV, mainan anak, HP mode silent)*

**Safety 2**

```
Baterai... cek tipe-nya. Ada yang ganti, ada yang built-in. Beda awet.
```

```
Jangan pasang ke barang yang bisa kena air... tracker bluetooth biasa nggak tahan air.
```

**CTA 2**

```
Pengin coba... keranjang kuning. Harga biasanya ramah.
```

```
Buat yang sering bilang "kunci dimana"... ini worth it banget.
```

---

### 5.7 · G_question_hooks (20 clip — pertanyaan distinct)

```
Di rumah kamu... yang paling sering bikin khawatir apa?
```

```
Pernah nggak... kunci ketinggalan di dalam rumah? Cerita dong.
```

```
Kos, kontrakan, apa rumah sendiri? Kebutuhan keamanannya beda lho.
```

```
Udah ada yang pakai smart lock? Pengalamannya jujur aja... bagus apa ribet?
```

```
CCTV murah... worth it nggak? Yang udah pasang, review dong.
```

```
Senter di rumah kamu... ada apa nggak? Jujur aja ya.
```

```
Pernah barang hilang di rumah sendiri? Seberapa sering?
```

```
Kalau harus pilih satu dulu... pintu, teras, senter, atau tracker? Kenapa?
```

```
Rumah kamu WiFi nya kenceng? Kalau mau pakai CCTV... itu pengaruh.
```

```
Anggota rumah berapa orang? Pengaruh ke pilihan smart lock lho.
```

*(10 lagi: pintu kayu atau besi, teras terang atau gelap, tinggal di gang atau jalan besar, punya anak kecil atau nggak, sering ditinggal kerja, hewan peliharaan, tinggal di lantai berapa, ada pagar atau nggak, tetangga dekat, pernah kemalingan)*

---

### 5.8 · H_price_safe (12 clip — single 6 + merged 6)

**Single response (biasa)**

```
Harga... saya nggak sebut angka pasti. Bisa berubah kapan aja. Cek keranjang kuning.
```

```
Kalau harga terasa mahal... jangan dipaksa. Cocokin dulu sama masalah yang mau dibenerin.
```

```
Keranjang kuning buat cek detail. Bukan berarti harus checkout sekarang.
```

```
Saya lebih suka kamu batal beli... daripada beli barang nggak cocok.
```

```
Bingung pilih mana? Tulis kebutuhan utama kamu. Saya bantu urutkan.
```

```
Promo bisa berubah. Makanya saya nggak janji harga fixed di sini.
```

**Merged response (banyak orang nanya harga bareng)**

```
Banyak yang nanya harga ya... oke saya jawab sekali buat semuanya. Cek keranjang kuning. Itu selalu update.
```

```
Komentar harga numpuk... saya gabung aja ya. Harga ada di keranjang kuning, bukan di saya.
```

```
Lima enam yang nanya harga... jawabannya sama. Keranjang kuning. Maaf ya nggak bisa sebut satu-satu.
```

```
Biar adil ya... harga nggak saya sebut. Semua lihat langsung di keranjang kuning sistem TikTok Shop.
```

```
Oke oke... harga ya. Satu jawaban buat semua: keranjang kuning. Saya nggak kontrol harga dari sini.
```

```
Promo beda-beda per user kadang. Makanya lebih adil kalau kalian cek sendiri di keranjang kuning.
```

---

### 5.9 · I_trust_safety (10 clip)

```
Saya affiliate, bukan penjual langsung. Produk dari seller, saya cuma rekomendasi.
```

```
Komisi ada... wajar. Tapi saya nggak akan jual barang yang saya sendiri ragu.
```

```
Baca review dulu sebelum checkout. Bintang lima aja... curiga. Baca yang bintang dua tiga.
```

```
Garansi... tanya seller langsung di chat. Saya nggak bisa jamin garansi spesifik.
```

```
Kalau barang sampai rusak... klaim ke TikTok Shop. Ada sistem proteksinya.
```

```
Bukan semua produk saya pakai sendiri. Kalau cuma rekomen dari review, saya bilang jujur.
```

```
Penting... baca spesifikasi sampai detail. Jangan cuma lihat foto.
```

```
Variasi produk... pilih yang sesuai. Jangan ambil yang asal karena kelihatan paling mahal.
```

```
Kalau ragu... chat seller dulu. Tanya detail yang belum jelas. Hak kamu.
```

```
Saya di sini bukan buat maksa. Kamu yang keputusannya, bukan saya.
```

---

### 5.10 · J_idle_filler (15 clip — fragment pretend-think)

```
Sebentar ya... lagi scroll komentar dulu.
```

```
Hmm... oke oke.
```

```
Eh ada yang ketik apa tadi... saya scroll ulang.
```

```
Bentar... saya liat urutannya.
```

```
Kedip kedip... maaf ya.
```

```
Oke... lanjut.
```

```
Mumpung lagi sepi... saya minum dulu.
```

```
Nah... itu dia.
```

```
Sabar ya... saya atur dulu.
```

```
Eh iya... tadi mau ngomong apa ya.
```

```
Hmm... oke jadi gini.
```

```
Bentaran... saya liat produk lain dulu.
```

```
Oke oke... jalan terus.
```

```
Eh... tadi sampai mana ya.
```

```
Ya udah... santai aja.
```

---

### 5.11 · ⭐ R_reaction_kit (35 clip — KATEGORI BARU)

**R.1 Gift received (8 clip)** — gunakan `name` placeholder, worker substitute saat play

```
Makasih gift-nya kak... wah mantep banget.
```

```
Gift masuk... terima kasih banyak. Jarang-jarang nih.
```

```
Wah ada yang kirim gift... saya terima ya, makasih.
```

```
Seneng banget ada gift... appreciate banget.
```

```
Terima kasih supportnya. Gift itu bikin semangat.
```

```
Wah makasih kak yang kirim gift... saya keinget terus.
```

```
Gift nya masuk... terima kasih ya, lanjut bahas produknya.
```

```
Appreciate banget. Makasih support nya di live ini.
```

**R.2 Share received (6 clip)**

```
Makasih yang udah share live ini... rame-ramein.
```

```
Ada yang share... wah terima kasih banyak.
```

```
Live nya di-share... bantu banget buat jangkauan. Makasih ya.
```

```
Share button itu gratis tapi bantu banget. Terima kasih yang nge-share.
```

```
Buat yang share... saya doain urusan rumahnya lancar.
```

```
Share count naik... terima kasih buat yang udah bantu.
```

**R.3 Follow request (6 clip)**

```
Buat yang belum follow... klik aja kalau suka topiknya. Gratis.
```

```
Yang mau update konten kayak gini... tombol follow ada di atas.
```

```
Makasih yang baru follow... selamat datang di sini.
```

```
Follow dulu biar nggak ketinggalan live berikutnya.
```

```
Yang sering nonton tapi belum follow... pencet aja, gampang.
```

```
Buat yang baru follow... seneng banget, makasih ya.
```

**R.4 Join notification (6 clip)**

```
Selamat datang yang baru masuk... santai ya, konteksnya saya ulang bentar.
```

```
Ada yang baru join... halo, welcome.
```

```
Yang baru masuk... makasih udah mampir.
```

```
Wah ada yang baru join... kita lagi di topik pintu rumah.
```

```
Buat yang baru klik... santai aja, topiknya rumah aman malam hari.
```

```
Halo yang baru mampir... saya lagi bahas empat produk. Ikut aja.
```

**R.5 Viewer milestone (5 clip)**

```
Wah sekarang udah 50 viewer... rame. Makasih ya.
```

```
Viewer naik terus... seneng liatnya. Terima kasih yang bertahan.
```

```
Seratus viewer tembus... wah saya nggak nyangka. Makasih semuanya.
```

```
Rame banget... saya jadi semangat. Lanjut terus ya.
```

```
Dua ratus viewer... saya stuck kata-kata, terima kasih banyak.
```

**R.6 Merged repeated comments (4 clip)**

```
Banyak yang nanya pertanyaan sama... saya jawab sekali aja ya biar adil.
```

```
Komentar numpuk pertanyaan sama... oke oke, saya gabung jawabannya.
```

```
Lima yang nanya hal serupa... jawabannya satu, saya satukan.
```

```
Sabar ya yang nanya hal sama berkali-kali... saya jawab bareng.
```

---

### 5.12 · ⭐ T_bridge (15 clip — KATEGORI BARU)

Transisi antar produk dan antar phase.

**T.1 Opening → Paloma (3)**

```
Oke... cukup basa-basinya. Kita mulai dari pintu dulu.
```

```
Langsung aja... produk pertama. Pintu depan.
```

```
Mulai dari yang paling krusial... pintu. Paloma smart lock.
```

**T.2 Paloma → CCTV (3)**

```
Pintunya cukup ya... sekarang kita geser ke luar. Teras.
```

```
Dari dalam ke luar rumah. CCTV buat area depan.
```

```
Oke pindah topik... dari pintu ke pantauan teras.
```

**T.3 CCTV → Senter (3)**

```
Pantauan udah... sekarang barang darurat. Senter.
```

```
Next... barang kecil tapi wajib ada. Senter buat mati lampu.
```

```
Oke geser... dari CCTV ke senter. Dua-duanya penting buat malam.
```

**T.4 Senter → Tracker (3)**

```
Senter beres... sekarang barang kecil terakhir. Tracker.
```

```
Lanjut ke tracker ya... barang yang sering kelupaan di mana.
```

```
Oke senter cukup... pindah ke tracker. Cocok buat yang suka lupa taruh kunci.
```

**T.5 Product → Q&A (3)**

```
Sebentar... saya mau lihat komentar dulu. Banyak yang belum saya jawab.
```

```
Oke cukup bahas produk ya... saya break bentar buat jawab pertanyaan.
```

```
Pause dulu... kita Q&A. Yang nanya tadi saya scroll ulang.
```

---

### 5.13 · Z_closing_staged (8 clip)

**T-10 menit (2)**

```
Live ini tinggal sepuluh menit ya. Yang mau nanya... kejar aja.
```

```
Sepuluh menit terakhir... yang pengin detail, silakan komentar sekarang.
```

**T-5 menit (2)**

```
Lima menit terakhir... saya akan tutup pelan-pelan.
```

```
Waktu hampir habis ya. Lima menit lagi saya stop.
```

**T-2 menit (2)**

```
Dua menit terakhir... recap cepat. Kita bahas pintu, teras, senter, tracker.
```

```
Hampir tutup. Terima kasih yang bertahan dari awal sampai sekarang.
```

**T-30s (1)**

```
Tiga puluh detik terakhir... makasih semua yang udah mampir.
```

**T-0 (1)**

```
Oke saya tutup ya. Sampai ketemu di live berikutnya. Jaga rumah baik-baik.
```

---

## 6 · Cartesia Batch Prompt v2 (SIAP PASTE)

<aside>
📋

Gunakan prompt ini sebagai system prompt saat generate audio library via `scripts\gen_audio_library.py`. Edit per kategori sebelum run.

</aside>

```
Kamu adalah Cartesia Sonic-3 voice engine. Generate audio Bahasa Indonesia dengan karakter suara:

PERSONA: Laki-laki Indonesia usia 30-an, seperti tetangga yang suka ngoprek rumah. Santai, jujur, kadang ragu, tidak memaksa. Bukan sales. Bukan penyiar radio.

STYLE:
- Fragment pendek 3-12 kata per unit
- Banyak jeda natural (titik tiga ... = breath, koma = pause pendek)
- Disfluency natural: "eh", "hmm", "oke oke", "sebentar", "mumpung", "bentar"
- UPPERCASE kata kunci = emphasis / stress
- Intonasi pertanyaan naik di akhir kalau ada tanda ?
- Tempo: normal untuk context, lebih cepat untuk reaction kit, lebih pelan untuk safety

PRONUNCIATION:
- "Paloma" = pa-LO-ma (stress tengah)
- "DLP enam ribu" = de-el-pe enam ribu
- "V tiga delapan puluh" = ve tiga delapan puluh
- "XHP seratus enam puluh" = eks-ha-pe seratus enam puluh
- "IPX enam" = i-pe-iks enam
- "USB C" = yu-es-be se
- "Dings" = dings (rhyme with things)
- "CCTV" = se-se-te-ve

AVOID:
- Tone iklan radio
- Kalimat panjang 20+ kata
- Kata "bos" terlalu sering
- Hard-sell / desperate closer
- Harga pasti (angka rupiah)
- Link luar (WA, IG, Shopee, Tokopedia)
- Klaim mutlak ("anti maling", "100% aman")

OUTPUT per clip:
- Durasi 5-18 detik
- Format WAV 44.1kHz mono 16-bit
- Volume normalized -3dB
- Tidak ada background noise
- Save dengan nama file: <KATEGORI>_<NOMOR>.wav

Voice ID: a167e0f3-df7e-4d52-a9c3-f949145efdab
Model: sonic-3
Language: id
```

---

## 7 · File Naming Convention

```
<KATEGORI>_<NOMOR_3_DIGIT>.wav

Contoh:
A_opening_001.wav  (hook tipe 1 variasi 1)
A_opening_005.wav  (hook tipe 2 variasi 2)
R_reaction_kit_gift_001.wav
R_reaction_kit_share_003.wav
T_bridge_paloma_cctv_002.wav
Z_closing_staged_t10_001.wav
```

Director Python akan baca `index.json` yang generated otomatis dari script `gen_audio_library.py`:

```json
{
  "version": "2.0",
  "clips": [
    {"id": "A_opening_001", "file": "A_opening_001.wav", "category": "A_opening", "tone": "hook_problem", "duration": 6.2, "tier": "high"},
    {"id": "R_reaction_kit_gift_001", "file": "R_reaction_kit_gift_001.wav", "category": "R_reaction_kit", "subcategory": "gift", "duration": 4.1, "tier": "high", "requires_substitution": true, "placeholders": ["name"]}
  ]
}
```

---

## 8 · QA Checklist Before Commit Audio Library

Per batch (setelah generate, before push):

- [ ]  Dengarkan **30 sample acak** dari total 220
- [ ]  Reject kalau: robotic, terlalu cepat, pronunciation salah, ada clip lain kebawa, noise artifact
- [ ]  **Target pass rate**: 80% minimum. Kalau di bawah 75%, regenerate dengan prompt tuning.
- [ ]  Check durasi: no clip >20s (target 5-18s)
- [ ]  Check volume: normalized -3dB semua clip
- [ ]  Check file naming: match `clips_script.yaml` ID
- [ ]  Check `index.json`: semua clip ter-list, tidak ada orphan file
- [ ]  **Spot test kategori R**: reaction kit harus bunyi "hangat", bukan "dibaca"
- [ ]  **Spot test kategori J**: idle filler harus bunyi "mikir", bukan "baca script"
- [ ]  **Spot test kategori T**: bridge harus bunyi "geser topik natural", bukan "jump cut"

---

## 9 · Worker Integration Notes

### 9.1 — Director harus tahu kategori baru

Update `apps/worker/config/clips_script.yaml`:

```yaml
categories:
  A_opening: { count: 12, weight: 1.0, tier_distribution: {high: 4, mid: 4, low: 4} }
  B_reset_viewer: { count: 20, weight: 0.8, tier_distribution: {high: 6, mid: 8, low: 6} }
  C_paloma: { count: 30, weight: 1.0, subtypes: {context: 20, safety: 5, cta: 5} }
  D_cctv: { count: 25, weight: 1.0, subtypes: {context: 18, safety: 4, cta: 3} }
  E_senter: { count: 20, weight: 1.0, subtypes: {context: 15, safety: 3, cta: 2} }
  F_tracker: { count: 18, weight: 1.0, subtypes: {context: 14, safety: 2, cta: 2} }
  G_question_hooks: { count: 20, weight: 0.6 }
  H_price_safe: { count: 12, weight: 0.4, subtypes: {single: 6, merged: 6} }
  I_trust_safety: { count: 10, weight: 0.3 }
  J_idle_filler: { count: 15, weight: 0.5 }
  R_reaction_kit: { count: 35, weight: 2.0, subtypes: {gift: 8, share: 6, follow: 6, join: 6, milestone: 5, merged: 4}, trigger: event }
  T_bridge: { count: 15, weight: 1.5, trigger: phase_change }
  Z_closing_staged: { count: 8, weight: 3.0, trigger: time_remaining, tiers: {t10: 2, t5: 2, t2: 2, t30s: 1, t0: 1} }
```

### 9.2 — Event-triggered categories

R dan Z tidak play random — di-trigger event spesifik:

| Kategori | Trigger | Logic |
| --- | --- | --- |
| R_reaction_kit.share | TikTokLive `ShareEvent` | Pick random clip |
| R_reaction_kit.join | TikTokLive `JoinEvent` | Throttle: max 1/60s |
| R_reaction_kit.merged | Duplicate comment count ≥3 dalam 30s | Pick random, skip individual reply |
| Z_closing_staged | `live_elapsed_s` vs `LIVE_MAX_DURATION_S` | Hard schedule T-10/T-5/T-2/T-30s/T-0 |

### 9.3 — Update `director.py` (ringkas)

```python
# Pseudocode
async def on_event(event):
    if isinstance(event, GiftEvent):
        clip = pick_random("R_reaction_kit.gift")
        audio = substitute_placeholders(clip, {"name": event.user.unique_id})
        await play_audio(audio, priority=HIGH)
    elif isinstance(event, ShareEvent):
        clip = pick_random("R_reaction_kit.share")
        await play_audio(clip, priority=HIGH)
    # ...dst

async def on_phase_change(old_phase, new_phase):
    bridge = pick_bridge_clip(old_phase, new_phase)
    await play_audio(bridge, priority=HIGH)
    # lalu lanjut schedule category utama phase baru

async def on_tick():
    elapsed = time.time() - session_start
    remaining = LIVE_MAX_DURATION_S - elapsed
    if remaining <= 600 and not played_t10:
        await play_audio(pick("Z_closing_staged.t10"), priority=HIGH)
        played_t10 = True
    # ...dst untuk t5, t2, t30s, t0
```

### 9.4 — Placeholder substitution

File `R_reaction_kit_gift_001.wav` tidak bisa pre-record nama `name`. Solusinya:

**Option A (preferred)**: Generate clip tanpa nama, lalu TTS inline untuk nama saja saat event (Cartesia low-latency API call).

**Option B (simpler)**: Pre-record 8 variasi tanpa nama sama sekali, pure "Makasih gift-nya kak, wah mantep banget!". Nama di-display overlay only.

**Rekomendasi**: Start dengan Option B (MVP). Upgrade ke Option A di v0.5.

---

## 10 · Migrasi dari Doc #86

<aside>
📦

Doc #86 tetap aktif sebagai **strategic frame**. Doc ini (#20) jadi **source of truth untuk batch TTS**.

</aside>

**Urutan migrasi**:

1. Generate dulu 220 clip audio sesuai doc ini (bukan 160 clip versi doc #86)
2. Update `apps/worker/config/clips_script.yaml` dengan kategori R dan T
3. Update `director.py` dengan event-triggered category logic
4. Update `index.json` schema: tambah field `subcategory`, `tier`, `requires_substitution`, `placeholders`
5. Doc #86 masih berguna untuk: persona base, runsheet 2 jam structure, product selection rationale, checklist produksi umum

**Yang DEPRECATED dari doc #86**:

- Section 7 "Library Voice Cartesia" struktur folder (v1 — ganti dengan section 4 doc ini)
- Section 20 "Prompt Batch Cartesia Final" (v1 — ganti dengan section 6 doc ini)
- Semua script section 8-17 di doc #86 (v1 — ganti dengan section 5 doc ini yang sudah fragment-style)

---

## 11 · Sprint 1-Hari: Generate 220 Clip

- <strong>Pagi (3 jam) — Generate batch 1-3</strong>
    1. Set API key Cartesia di `.env` local
    2. Copy prompt dari section 6 ke system prompt field
    3. Run `scripts\gen_audio_library.bat` dengan kategori A, B, C (total 62 clip)
    4. Spot test 10 clip random, verify quality
    5. Regenerate yang fail (target pass 80%)
- <strong>Siang (3 jam) — Generate batch 4-6</strong>
    1. Run kategori D, E, F, G (total 83 clip)
    2. Run kategori H, I, J (total 37 clip)
    3. Spot test per kategori
    4. Fix pronunciation issues via prompt tuning
- <strong>Sore (2 jam) — Generate kategori baru R, T, Z</strong>
    1. Run kategori R_reaction_kit (35 clip) — pay attention ke tier high
    2. Run kategori T_bridge (15 clip)
    3. Run kategori Z_closing_staged (8 clip)
    4. **Critical**: dengar ulang kategori R, harus hangat bukan datar
- <strong>Malam (1 jam) — Finalize index + commit</strong>
    1. Run `scripts\build_audio_index.py` → generate `index.json`
    2. Verify total 220 clip matched
    3. Git add `apps/worker/static/audio_library/*.wav` (override .gitignore sementara)
    4. Commit dengan message `feat(audio): generate v2 library 220 clips (Cartesia Sonic-3)`
    5. Push ke origin/master
    6. Trigger dress rehearsal 30 menit

---

## 12 · Success Metrics

Ukur setelah 3 kali live 30-menit test:

| Metric | Target | Cara ukur |
| --- | --- | --- |
| Retention 15 menit | ≥20% | Same |
| "Ini rekaman ya?" comment | 0 negative | Manual review comments |
| Share reaction latency | ≤3 detik | Same |
| TTS pronunciation accuracy | ≥95% benar | Manual review 20 clip random |

---

## 13 · Referensi

- [🎙️ Live Interaction Plan — 2 Jam Cartesia, Produk, Scene, Retensi](https://www.notion.so/Live-Interaction-Plan-2-Jam-Cartesia-Produk-Scene-Retensi-1267e9d752fa48ad847d1b2e778644a7?pvs=21)
- [🧠 Orchestrator Implementation Plan — Python Worker + Svelte Control Center](https://www.notion.so/Orchestrator-Implementation-Plan-Python-Worker-Svelte-Control-Center-ebeaa1b997794405bad652a133f2afbe?pvs=21)
- [🔬 17 · v0.4 Implementation Review — Bugs, Gaps & Completion Plan](https://www.notion.so/17-v0-4-Implementation-Review-Bugs-Gaps-Completion-Plan-3b7aa241f5284b99bd6819d091b7f067?pvs=21)
- [🎨 18 · UX Navigation + Go-Live Gap Closure (Backend + Frontend)](https://www.notion.so/18-UX-Navigation-Go-Live-Gap-Closure-Backend-Frontend-fff3bef08a734370a76ca77ba4c8feeb?pvs=21)
- [🎬 19 · Video Faceless Workflow — Supplier + AI Gen + Reference Recon (B-roll Ambient)](https://www.notion.so/19-Video-Faceless-Workflow-Supplier-AI-Gen-Reference-Recon-B-roll-Ambient-15cac1e82fe34e3d869de731c71856b2?pvs=21)

---

<aside>
✅

**Bottom line**: Dokumen ini adalah **source of truth final** untuk generate audio library. Doc #86 tetap valuable sebagai strategic frame, tapi yang di-paste ke Cartesia batch adalah section 5 + section 6 dokumen ini. Targetnya: 220 clip human-ready, live-reactive, TTS-optimized, siap untuk live 2 jam pertama.

</aside>