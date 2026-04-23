# 🎙️ Live Interaction Plan — 2 Jam Cartesia, Produk, Scene, Retensi

> Terakhir diedit: 2026-04-23 | [Buka di Notion](https://www.notion.so/Live-Interaction-Plan-2-Jam-Cartesia-Produk-Scene-Retensi-1267e9d752fa48ad847d1b2e778644a7)

> ⚠️ **Kritik utama terhadap versi lama**: dokumen sebelumnya terlalu terasa seperti template AI. Ia langsung bicara “live interaktif”, padahal **bahan visual belum ada**, produk awal belum dikunci, dan script voice terlalu generik. Live tidak boleh dimulai dari “mau ngomong apa”, tapi dari **produk apa yang layak dibahas, bukti visual apa yang bisa ditampilkan, dan alasan penonton mau bertahan**.

## 0 · Keputusan Final: Ini Bukan Video, Ini Acara 2 Jam

**Format live yang akan dibuat:**

```
Live faceless semi-hosted
→ visual produk/ruangan sebagai latar
→ voice-over Cartesia modular
→ interaksi komentar real-time
→ maksimal 2 jam lalu stop
→ bisa diulang di jam lain dengan urutan audio/scene berbeda
```

**Batas keras:**

- **Durasi maksimal 2 jam per sesi.** Setelah itu stop, evaluasi, lalu boleh ulang di jam lain.

- Jangan live kalau bahan visual masih kosong.

- Jangan mulai dari 1 produk tunggal selama 2 jam. Itu akan membosankan.

- Jangan membuat voice-over seperti robot promosi.

- Jangan pakai kategori gaming.

- Jangan sebut harga pasti di voice. Harga cukup diarahkan ke keranjang kuning.

---

## 1 · Kenapa Versi Lama Terasa Aneh

### Masalah sebagai host pembawa acara

1. **Terlalu banyak kalimat komando chat**  

  “Ketik lampu”, “ketik storage”, “ketik aman” kalau diulang terus terdengar seperti bot giveaway, bukan host.

1. **Belum ada produk awal yang jelas**  

  Live affiliate harus punya “meja jualan”. Kalau produknya belum dipilih, host terdengar mengambang.

1. **Tidak ada bahan capture**  

  OBS/Window Capture tidak menyelesaikan masalah kalau belum ada video/visual yang layak ditampilkan.

1. **Voice terlalu steril**  

  Kalimat seperti “solusi rumah praktis” benar, tapi kurang manusiawi. Host harus terdengar seperti orang yang sedang menemani, bukan membaca brosur.

1. **Tidak cocok untuk 2 jam**  

  Runsheet 30 menit bisa untuk test, tapi live 2 jam butuh blok, rotasi produk, jeda, reset, dan variasi audio.

**Kesimpulan kritis:** sebelum membuat voice Cartesia, kita harus kunci **tema live + daftar produk + bahan visual + library audio modular**.

---

## 2 · Produk Awal yang Dikunci untuk Live Pertama

### Tema Live Pertama

```
Rumah Aman & Praktis Saat Malam
```

Kenapa tema ini dipilih:

- Nyambung ke kebutuhan rumah nyata: pintu, keamanan, gelap, barang hilang.

- Bisa memuat beberapa produk dalam 2 jam.

- Tidak terasa random.

- Bisa dibahas dengan gaya edukasi, bukan jualan agresif.

### Urutan produk live pertama

| Urutan | Produk | Peran dalam live | Alasan dipilih | Status bahan |
| --- | --- | --- | --- | --- |
| 1 | **PALOMA DLP 6000 Digital Lock Smart Home** | Anchor / produk utama | High-ticket, komisi tinggi, topik keamanan rumah kuat | Butuh riset visual + aset produk dulu |
| 2 | **CCTV V380 Pro Dual Lens 360 Auto Tracking** | Produk pendamping keamanan | Harga lebih rendah, gampang dijelaskan, pain point jelas | Butuh demo UI / ilustrasi pantau rumah |
| 3 | **LED Senter XHP160 USB-C IPX6** | Produk darurat malam | Murah, mudah dipahami, cocok untuk mati lampu / outdoor | Bisa dibuat visual ruangan gelap + beam light |
| 4 | **DINGS Smart GPS Tracker Bluetooth** | Produk ringan untuk variasi | Masalah barang hilang relatable: kunci, dompet, tas | Butuh visual kunci/dompet/tas |

**Catatan host:** PALOMA tidak boleh dibahas 2 jam penuh. Jadikan PALOMA sebagai “produk utama”, lalu CCTV, senter, dan tracker sebagai “produk keluarga” dalam tema rumah aman.

---

## 3 · Riset Shop Live Sebelum Produksi Bahan

Sebelum generate visual dan voice, lakukan riset 45–60 menit di TikTok Shop / showcase.

### Checklist riset produk

- [ ] Cek apakah produk masih aktif di keranjang / showcase.

- [ ] Cek foto dan video seller yang boleh dipakai atau tidak.

- [ ] Cek review pembeli: cari keluhan nyata.

- [ ] Cek 5 pertanyaan umum pembeli.

- [ ] Cek variasi produk: ukuran, warna, paket.

- [ ] Cek apakah produk butuh instalasi teknisi.

- [ ] Cek batas klaim: jangan sebut anti-maling mutlak, jangan sebut garansi kalau tidak pasti.

- [ ] Ambil 3 angle aman: manfaat, kekurangan, cocok untuk siapa.

### Output riset wajib

| Produk | Yang harus dicatat sebelum live |
| --- | --- |
| PALOMA Smart Lock | Metode buka, tipe pintu yang cocok, instalasi, baterai, emergency access, keluhan review |
| CCTV V380 | Resolusi, night vision, auto tracking, memory card/cloud, aplikasi, keluhan koneksi |
| Senter XHP160 | Mode cahaya, charging, durasi baterai, tahan air, ukuran real, keluhan panas/berat |
| GPS Tracker | Jangkauan bluetooth, baterai, cara bunyi, cocok untuk kunci/dompet/tas, batas bukan GPS mobil real |

---

## 4 · Bahan Visual yang Harus Dibuat Dulu

Karena belum ada bahan capture, jangan mulai dari OBS. Mulai dari **asset pack**.

### Asset pack minimum untuk 2 jam

```
/live-assets/rumah-aman-malam/
├── 00_opening_room_loop/          5 clip x 30–60 detik
├── 01_paloma_smart_lock/          10 clip x 30–60 detik
├── 02_cctv_v380/                  8 clip x 30–60 detik
├── 03_senter_xhp160/              8 clip x 30–60 detik
├── 04_gps_tracker/                6 clip x 30–60 detik
├── 05_idle_room/                  10 clip x 30–60 detik
└── 06_fallback/                   3 clip x 30–60 detik
```

### Prinsip visual

- Visual harus bergerak pelan, bukan gambar diam.

- Ruangan harus realistis seperti rumah Indonesia biasa.

- Produk jangan terlihat palsu atau terlalu mewah.

- Kalau produk belum ada di tangan, gunakan visual **situasi masalah**, bukan klaim demo palsu.

- Hindari screenshot marketplace sebagai konten utama.

### Visual yang boleh dibuat walau produk belum ada

- Pintu rumah malam hari.

- Orang mencari kunci di meja.

- Area teras gelap.

- Lorong rumah saat mati lampu.

- Meja dengan kunci, dompet, tas.

- Ilustrasi CCTV memantau pintu.

- Close-up tangan membuka pintu tanpa menampilkan merek palsu.

### Visual yang tidak boleh

- Demo sidik jari PALOMA palsu jika belum ada footage real.

- Klaim “anti bobol” dengan adegan pembobolan berlebihan.

- Menampilkan logo/brand palsu.

- Menampilkan harga besar permanen.

- Menggunakan footage creator lain tanpa izin.

---

## 5 · Prompt Visual Realistis untuk Bahan Live

### Prompt opening rumah aman

```
realistic modest Indonesian house entrance at night, warm porch light, simple ceramic floor, wooden or metal front door, small shoe rack, keys on a table, calm daily life atmosphere, vertical 9:16, slow camera movement, natural shadows, no text, no watermark, not luxury, not cinematic overkill
```

### Prompt PALOMA / smart lock context tanpa demo palsu

```
realistic Indonesian front door close-up, modern digital door lock style without visible brand logo, hand reaching toward the door, home safety context, warm indoor light, subtle camera movement, vertical 9:16, realistic proportions, no fake text, no watermark
```

### Prompt CCTV context

```
realistic small Indonesian terrace at night, CCTV camera mounted near front door, soft night vision feeling, quiet neighborhood, practical home security atmosphere, vertical 9:16, slow pan, no text, no watermark, not scary, not dramatic crime scene
```

### Prompt senter context

```
realistic power outage in Indonesian home, hand holding LED flashlight, soft beam lighting a hallway, practical emergency situation, warm skin tone, modest interior, vertical 9:16, slow handheld movement, no text, no watermark
```

### Prompt tracker context

```
realistic table near front door with keys, wallet, small bag, bluetooth tracker attached to keychain, everyday Indonesian home, morning rush atmosphere, vertical 9:16, subtle camera movement, no text, no watermark
```

### Negative prompt umum

```
luxury mansion, sci-fi, cyberpunk, floating product, distorted hands, fake brand logo, unreadable text, watermark, exaggerated crime scene, blood, weapon, cartoon, over saturated, impossible perspective
```

---

## 6 · Voice Host: Gaya Baru yang Lebih Manusiawi

### Karakter suara

Bukan “sales robot”. Bukan “AI lucu-lucuan”.

**Karakter:**

```
Tetangga yang suka ngoprek rumah, ngomong santai, kadang ragu, jujur, dan tidak memaksa.
```

### Kata yang dipakai secukupnya

- “Coba lihat kasusnya...”

- “Kalau di rumah saya...”

- “Ini bukan wajib beli ya...”

- “Yang penting cocok dulu.”

- “Kalau ragu, jangan checkout dulu.”

- “Saya jelasin plus-minusnya.”

- “Kalau ada yang punya pengalaman, tulis di komentar.”

### Kata yang harus dikurangi

- “Bos” terlalu sering.

- “Solusi praktis” terlalu sering.

- “Ketik lampu / ketik aman” terlalu sering.

- “Cek keranjang kuning” terlalu sering.

### Rasio CTA

```
1 CTA setiap 5–7 menit
bukan setiap kalimat
```

---

## 7 · Library Voice Cartesia untuk 2 Jam

**Target produksi awal:** 160–220 potongan audio pendek.

Kenapa banyak? Karena kalau hanya 30 audio, 2 jam akan terasa berulang dan robotik.

### Struktur folder audio

```
/live-audio/rumah-aman-malam/
├── A_opening/             10 clip
├── B_reset_viewer/         20 clip
├── C_paloma_context/       35 clip
├── D_cctv_context/         30 clip
├── E_senter_context/       25 clip
├── F_tracker_context/      20 clip
├── G_question_hooks/       25 clip
├── H_price_safe/           15 clip
├── I_trust_safety/         15 clip
├── J_idle_human/           20 clip
└── K_closing/              10 clip
```

### Durasi audio

- Clip pendek: 5–8 detik.

- Clip penjelasan: 10–18 detik.

- Jangan buat monolog 1 menit kecuali untuk opening khusus.

- Sisipkan jeda 3–8 detik antar audio supaya tidak terdengar seperti radio otomatis.

---

## 8 · Script Voice: Opening yang Lebih Natural

```
Halo, saya mulai pelan-pelan dulu ya. Live ini bahas keamanan rumah malam hari: pintu, CCTV, senter darurat, dan barang kecil yang sering bikin hidup lebih tenang.
```

```
Kalau baru masuk, santai aja. Ini bukan live yang maksa beli. Saya lagi bongkar plus-minus beberapa barang rumah yang sering muncul di keranjang.
```

```
Hari ini temanya rumah aman saat malam. Mulai dari pintu depan, area teras, sampai barang kecil kayak kunci dan dompet yang sering hilang.
```

```
Kalau kamu punya pengalaman kunci ketinggalan, rumah kosong, atau area depan gelap, tulis aja. Saya pakai itu buat arah pembahasan.
```

---

## 9 · Script Voice: Reset untuk Penonton Baru

```
Buat yang baru masuk, kita lagi bahas paket rumah aman malam hari. Produk utamanya smart lock, lalu nanti nyambung ke CCTV, senter darurat, dan tracker kecil.
```

```
Kalau kamu baru join, konteksnya simpel: bukan semua barang harus dibeli. Kita pilih mana yang paling masuk akal untuk masalah rumah masing-masing.
```

```
Saya ulang sedikit ya. Fokus live ini bukan rumah mewah, tapi rumah biasa yang pengin lebih aman dan nggak ribet.
```

```
Yang saya suka dari tema ini: masalahnya dekat. Kunci hilang, teras gelap, rumah kosong, atau lupa taruh dompet. Hampir semua orang pernah.
```

---

## 10 · Script Voice: PALOMA Smart Lock

```
Kita mulai dari pintu dulu. Buat saya, pintu depan itu titik pertama yang harus diberesin sebelum mikir gadget rumah yang lain.
```

```
Smart lock itu bukan cuma soal keren. Yang paling terasa justru saat kunci ketinggalan, anak pulang duluan, atau rumah sering ditinggal.
```

```
Tapi saya jujur, smart lock bukan barang murah. Jadi jangan beli cuma karena kelihatan modern. Pastikan dulu pintu dan kebutuhannya cocok.
```

```
Kalau di rumah ada anak, orang tua, atau anggota keluarga yang sering lupa bawa kunci, fitur sidik jari bisa sangat membantu.
```

```
Hal yang wajib dicek sebelum beli smart lock: jenis pintu, ketebalan pintu, metode buka, baterai, dan akses darurat kalau baterai habis.
```

```
Saya tidak akan bilang ini anti maling mutlak. Tidak ada alat yang seratus persen. Tapi smart lock yang benar bisa menambah lapisan keamanan.
```

---

## 11 · Script Voice: CCTV V380

```
Setelah pintu, area kedua yang sering dilupakan itu teras. Banyak orang baru kepikiran CCTV setelah paket hilang atau ada kejadian aneh.
```

```
CCTV murah sekarang sudah cukup untuk pantau area depan rumah. Yang penting jangan asal beli, cek dulu night vision dan aplikasi HP-nya.
```

```
Kalau rumah sering kosong, satu kamera di pintu depan biasanya lebih berguna daripada banyak kamera tapi posisinya asal.
```

```
CCTV bukan cuma buat maling. Kadang cuma buat cek paket, anak sudah pulang belum, atau siapa yang lewat depan rumah.
```

```
Kalau koneksi internet rumah sering putus, pastikan kamu paham batas CCTV WiFi. Jangan berharap semua fitur jalan kalau WiFi tidak stabil.
```

---

## 12 · Script Voice: Senter XHP160

```
Sekarang masuk barang kecil yang sering diremehkan: senter. Pas listrik mati, baru terasa kalau senter HP itu sebenarnya darurat banget.
```

```
Senter yang layak di rumah itu bukan cuma terang. Harus mudah dicas, gampang dicari, dan kuat dipakai saat hujan atau mati lampu.
```

```
Saya suka senter karena manfaatnya jelas. Tidak perlu dijelaskan panjang-panjang. Rumah gelap, ambil senter, selesai.
```

```
Tapi tetap realistis. Senter kecil jangan dianggap seperti lampu sorot proyek. Cocoknya untuk rumah, halaman, motor, camping ringan, dan darurat.
```

```
Kalau di rumah belum punya senter khusus, ini justru barang pertama yang paling masuk akal sebelum beli gadget mahal.
```

---

## 13 · Script Voice: Smart Tracker

```
Sekarang barang kecil yang sering menyelamatkan pagi hari: tracker untuk kunci, dompet, atau tas.
```

```
Ini cocok untuk orang yang sering bilang, kunci tadi saya taruh mana ya. Masalah kecil, tapi kalau kejadian tiap hari bikin capek.
```

```
Yang perlu dipahami: tracker bluetooth bukan GPS mobil jarak jauh. Biasanya lebih cocok untuk cari barang di sekitar rumah atau area dekat.
```

```
Kalau kamu sering buru-buru pagi, barang kecil seperti ini bisa lebih berguna daripada kelihatannya.
```

---

## 14 · Script Voice: Pancing Interaksi yang Tidak Kaku

```
Kalau boleh tahu, di rumah kamu yang paling sering bikin khawatir apa: pintu, teras, mati lampu, atau barang sering hilang?
```

```
Saya pengin tahu kasus paling sering di sini. Ada yang pernah kunci ketinggalan di dalam rumah?
```

```
Kalau kamu tinggal di kos, kontrakan, atau rumah sendiri, kebutuhan keamanannya beda. Tulis tipe tempat tinggalnya kalau mau saya bahas.
```

```
Ada yang sudah pakai smart lock atau CCTV murah? Tulis pengalaman jujurnya. Bagus atau malah ribet?
```

```
Kalau harus pilih satu dulu: pintu aman, teras kepantau, atau senter darurat? Saya penasaran mayoritas pilih yang mana.
```

---

## 15 · Script Voice: Harga dan Keranjang yang Tidak Hard-Sell

```
Untuk harga saya tidak sebut angka pasti di live, karena promo bisa berubah. Kalau mau cek, lihat yang muncul di keranjang kuning.
```

```
Kalau harganya terasa kemahalan, jangan dipaksa. Cocokkan dulu dengan masalah yang mau diselesaikan.
```

```
Keranjang kuning itu buat cek detail, bukan berarti harus checkout sekarang. Baca spek dan review dulu.
```

```
Saya lebih suka kamu batal beli daripada beli barang yang tidak cocok dengan rumahmu.
```

```
Kalau bingung pilih yang mana, tulis kebutuhan utamanya. Nanti saya bantu urutkan dari yang paling masuk akal.
```

---

## 16 · Script Voice: Idle Saat Sepi tapi Tetap Manusiawi

```
Live masih pelan, nggak apa-apa. Biasanya di awal saya pakai buat jelasin konteks dulu, biar yang masuk belakangan nggak bingung.
```

```
Saya sambil susun urutan ya. Mulai dari pintu, lanjut teras, lalu barang darurat seperti senter dan tracker.
```

```
Kadang rumah itu bukan butuh banyak barang. Cukup satu titik yang benar-benar mengurangi rasa khawatir.
```

```
Kalau malam rumah terasa kurang aman, jangan langsung beli semuanya. Lihat dulu titik paling lemah: pintu, jendela, teras, atau penerangan.
```

---

## 17 · Script Voice: Penutup dan Stop 2 Jam

```
Saya tutup dulu setelah sesi ini ya. Live maksimal dua jam supaya tidak asal muter. Nanti bisa lanjut di jam lain dengan topik yang lebih rapi.
```

```
Makasih yang sudah mampir. Kalau tadi ada produk yang relevan, cek lagi pelan-pelan di keranjang. Jangan buru-buru checkout.
```

```
Sesi berikutnya kita bisa bahas dapur praktis atau storage rumah kecil. Tulis di komentar kalau ada topik yang paling kamu butuhkan.
```

---

## 18 · Runsheet 2 Jam

| Waktu | Blok | Produk / topik | Tujuan |
| --- | --- | --- | --- |
| 00:00–10:00 | Opening hangat | Tema rumah aman malam | Bangun konteks, jangan jualan dulu |
| 10:00–35:00 | Anchor 1 | PALOMA Smart Lock | Bahas pintu, kunci hilang, akses keluarga |
| 35:00–55:00 | Anchor 2 | CCTV V380 | Bahas teras, paket, rumah kosong |
| 55:00–65:00 | Reset penonton | Ringkasan + Q&A | Penonton baru tidak bingung |
| 65:00–85:00 | Anchor 3 | Senter XHP160 | Bahas mati lampu, halaman, darurat |
| 85:00–100:00 | Anchor 4 | Smart Tracker | Bahas kunci/dompet/tas hilang |
| 100:00–112:00 | Q&A bebas | Semua produk | Jawab komentar, pilih kebutuhan |
| 112:00–120:00 | Closing | Recap + stop live | Tutup rapi, tidak infinite loop |

---

## 19 · Randomization Rule supaya Bisa Diulang

### Aturan sesi

```
Sesi A pagi/sore:
PALOMA → CCTV → Senter → Tracker

Sesi B malam:
Senter → CCTV → PALOMA → Tracker

Sesi C siang:
Tracker → CCTV → Senter → PALOMA
```

### Aturan audio

- Jangan putar audio yang sama dalam 20 menit.

- Opening boleh sama, tapi reset viewer harus bervariasi.

- CTA keranjang maksimal 1 kali tiap 5–7 menit.

- Setelah 2 jam, stop live. Jangan looping terus.

### Aturan scene

- Ganti visual tiap 1–3 menit.

- Masukkan idle room saat transisi.

- Kalau komentar masuk, pindah ke scene Q&A.

- Jika visual produk belum siap, jangan bahas produk itu terlalu panjang.

---

## 20 · Prompt Batch Cartesia Final

```
Buat library voice-over untuk live TikTok affiliate @interiorhack.id bertema “Rumah Aman & Praktis Saat Malam”. Karakter suara: laki-laki Indonesia santai, seperti tetangga yang suka ngoprek rumah, jujur, tidak memaksa, kadang memberi catatan hati-hati.

Buat audio pendek yang bisa diputar random selama maksimal 2 jam live. Jangan terdengar seperti iklan. Jangan terlalu sering memakai kata “bos”. Jangan gunakan gaya robot, jangan hard-sell, jangan klaim harga pasti, jangan sebut link luar, jangan sebut WA/IG/Shopee/Tokopedia. Jika perlu CTA, sebut “cek keranjang kuning” secara halus.

Produk live:
1. PALOMA DLP 6000 Digital Lock Smart Home — fokus pintu, kunci hilang, akses keluarga, keamanan berlapis.
2. CCTV V380 Pro Dual Lens — fokus teras, paket, rumah kosong, pantau dari HP.
3. LED Senter XHP160 — fokus mati lampu, halaman gelap, darurat rumah.
4. DINGS Smart Tracker — fokus kunci, dompet, tas sering hilang.

Buat 200 variasi audio:
- 10 opening hangat
- 20 reset untuk penonton baru
- 35 pembahasan smart lock
- 30 pembahasan CCTV
- 25 pembahasan senter
- 20 pembahasan tracker
- 25 pertanyaan pemancing komentar
- 15 jawaban harga aman
- 15 trust/safety disclaimer
- 5 closing stop live 2 jam

Durasi setiap audio 5–18 detik. Bahasa natural, tidak terlalu rapi, seperti orang ngomong live. Sisipkan variasi jeda dan frasa manusiawi seperti “sebentar”, “kalau menurut saya”, “ini bukan wajib beli”, “coba cek dulu”.
```

---

## 21 · Checklist Produksi Sebelum Live Pertama

### Produk

- [ ] Cek 4 produk masih aktif di TikTok Shop.

- [ ] Baca 20 review tiap produk.

- [ ] Catat 5 keluhan tiap produk.

- [ ] Catat 5 pertanyaan umum tiap produk.

- [ ] Tentukan urutan produk sesi A dan B.

### Visual

- [ ] Buat minimal 50 clip visual 30–60 detik.

- [ ] Tidak ada footage orang lain tanpa izin.

- [ ] Tidak ada klaim demo palsu.

- [ ] Ada idle room loop.

- [ ] Ada fallback scene.

### Audio Cartesia

- [ ] Generate minimal 160 clip audio.

- [ ] File diberi nama kategori + nomor.

- [ ] Dengarkan 30 sampel acak.

- [ ] Buang audio yang terlalu robotik / terlalu sales.

- [ ] Pastikan tidak ada harga pasti dan link luar.

### OBS / Live

- [ ] Scene per produk siap.

- [ ] Window/Display Capture hanya menangkap OBS projector.

- [ ] Camera Tecgear siap sebagai backup.

- [ ] VB-CABLE audio masuk.

- [ ] Timer stop 2 jam disiapkan.

---

## 22 · Ukuran Sukses

**Test pertama jangan mengejar sales.** Ukur ini dulu:

- [ ] Live 30 menit tanpa warning.

- [ ] Tidak terasa robot saat ditonton ulang.

- [ ] Visual tidak membosankan dalam 10 menit pertama.

- [ ] Ada minimal 5 komentar real atau reaksi.

- [ ] Tidak ada penonton yang menulis “ini rekaman ya?” secara negatif.

- [ ] Setelah 30 menit, tidak ada notice/pelanggaran.

**Baru naik ke 2 jam jika test 30 menit aman.**

> ✅ **Bottom line**: jangan live sebelum punya bahan. Untuk live pertama, kunci tema **Rumah Aman & Praktis Saat Malam**, pakai 4 produk dalam satu cerita, generate 160–220 voice Cartesia pendek, dan stop maksimal 2 jam. Yang membuat live terasa manusiawi bukan banyaknya script, tapi variasi, jeda, kejujuran, dan kemampuan mengakui “jangan beli dulu kalau belum cocok”.

- [🧠 Orchestrator Implementation Plan — Python Worker + Svelte Control Center]

---
*Sync otomatis dari Notion. Jangan edit manual.*