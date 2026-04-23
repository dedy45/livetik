import yaml
clips=[]
opening=[
("Halo semuanya, selamat datang di live interiorhack! Senang banget kalian hadir di sini malam ini.","happy"),
("Hai hai hai, welcome back di live kita! Hari ini ada banyak produk keren yang mau kita bahas bareng.","happy"),
("Selamat datang di live interiorhack! Buat yang baru pertama kali mampir, kalian datang di waktu yang tepat.","happy"),
("Halo teman-teman semua! Makasih udah mampir ke live kita, ada banyak promo spesial hari ini lho.","happy"),
("Assalamualaikum dan selamat malam semuanya! Live kita mulai ya, siap-siap ada kejutan menarik.","happy"),
("Halo gaes! Selamat datang di live interiorhack, tempat solusi rumah impian kalian semua.","happy"),
("Hai semua yang udah join! Kita mulai live-nya ya, banyak produk bagus yang bakal kita showcase hari ini.","happy"),
("Selamat sore dan selamat datang! Makasih udah luangin waktu buat nonton live kita hari ini.","happy"),
("Halo halo! Wah udah banyak yang join nih, makasih ya teman-teman setia interiorhack.","happy"),
("Welcome to live interiorhack! Hari ini kita punya banyak produk premium dengan harga yang super terjangkau.","happy"),
("Hai semuanya, good evening! Kita mulai live malam ini dengan semangat dan produk-produk pilihan terbaik.","happy"),
("Halo teman-teman! Kalian udah siap belanja produk rumah berkualitas? Kita mulai yuk!","happy"),
("Selamat datang di live interiorhack, toko solusi hunian terpercaya kalian! Banyak yang mau kita share hari ini.","happy"),
("Hai hai! Makasih udah nemenin kita live hari ini, ada banyak info produk menarik yang sayang dilewatin.","happy"),
("Halo semua! Live kita resmi dimulai, yuk kita explore bareng produk-produk unggulan interiorhack.","happy"),
("Selamat bergabung di live interiorhack! Hari ini spesial banget, ada diskon dan promo eksklusif buat kalian.","happy"),
("Hai teman-teman! Seneng banget bisa ketemu lagi di live, kita bahas produk keren bareng-bareng yuk.","happy"),
("Halo semuanya! Live interiorhack dimulai, siap-siap dapet info produk terbaik dan penawaran spesial hari ini.","happy"),
]
for i,(text,emotion) in enumerate(opening,1):
    clips.append({"id":f"A_opening_{i:03d}","category":"A_opening","text":text,"tags":["opening","greeting"],"emotion":emotion})
paloma_demo=[
("Oke sekarang kita bahas PALOMA Smart Lock, kunci pintu pintar yang bakal bikin rumah kalian makin aman dan modern.","neutral"),
("PALOMA Smart Lock ini bisa dibuka pakai sidik jari, kartu, PIN, atau remote dari HP lho, canggih banget kan?","happy"),
("Coba lihat nih, PALOMA Smart Lock dipasang di pintu dan langsung bisa dioperasikan tanpa kunci konvensional sama sekali.","neutral"),
("Keunggulan PALOMA Smart Lock adalah materialnya yang premium, anti-karat, dan tahan cuaca ekstrem sekalipun.","neutral"),
("Dengan PALOMA Smart Lock, kalian bisa kasih akses ke anggota keluarga tanpa perlu duplikat kunci fisik lagi.","happy"),
("PALOMA Smart Lock punya fitur alarm otomatis kalau ada yang coba paksa buka pintu, keamanan ekstra buat rumah kalian.","neutral"),
("Instalasinya gampang banget, PALOMA Smart Lock bisa dipasang sendiri di rumah tanpa perlu tukang khusus.","happy"),
("Baterai PALOMA Smart Lock tahan sampai satu tahun pemakaian normal, jadi nggak perlu sering-sering ganti.","neutral"),
("PALOMA Smart Lock kompatibel dengan hampir semua jenis pintu, baik kayu, besi, maupun aluminium.","neutral"),
("Fitur auto-lock PALOMA Smart Lock otomatis mengunci pintu setelah beberapa detik, nggak perlu khawatir lupa kunci.","happy"),
("PALOMA Smart Lock hadir dalam beberapa pilihan warna elegan yang cocok dengan berbagai desain interior rumah.","happy"),
("Dengan teknologi enkripsi terkini, PALOMA Smart Lock memastikan data sidik jari kalian aman dan tidak bisa dicuri.","neutral"),
("PALOMA Smart Lock bisa menyimpan hingga 100 sidik jari berbeda, cocok buat rumah dengan banyak penghuni.","neutral"),
("Layar LCD PALOMA Smart Lock yang terang memudahkan pengoperasian bahkan di kondisi gelap sekalipun.","neutral"),
("PALOMA Smart Lock dilengkapi backup kunci mekanik darurat, jadi tetap bisa dibuka kalau baterai habis.","neutral"),
("Garansi resmi PALOMA Smart Lock selama dua tahun, jadi kalian bisa belanja dengan tenang dan percaya diri.","happy"),
("PALOMA Smart Lock sudah tersertifikasi dan diuji ribuan kali buka-tutup, kualitasnya terjamin banget.","neutral"),
("Dengan PALOMA Smart Lock, rumah kalian naik level jadi smart home yang modern dan berteknologi tinggi.","happy"),
]
for i,(text,emotion) in enumerate(paloma_demo,1):
    clips.append({"id":f"B_paloma_demo_{i:03d}","category":"B_paloma_demo","text":text,"tags":["paloma","smart_lock","demo","product"],"emotion":emotion})
paloma_cta=[
("Yuk langsung order PALOMA Smart Lock sekarang, klik keranjang di bawah atau ketik PALOMA di kolom chat!","happy"),
("Stok PALOMA Smart Lock terbatas lho, jangan sampai kehabisan! Order sekarang sebelum terlambat.","dramatic"),
("Dapatkan PALOMA Smart Lock hari ini dan nikmati keamanan rumah yang lebih canggih mulai malam ini juga.","happy"),
("Promo spesial PALOMA Smart Lock hanya berlaku selama live ini, jangan lewatkan kesempatan emas ini!","dramatic"),
("Ketik PALOMA di chat sekarang dan tim kita siap bantu proses orderan kalian dengan cepat.","happy"),
("PALOMA Smart Lock dengan harga spesial live, lebih hemat dibanding beli di toko offline manapun.","happy"),
("Jangan tunda lagi, PALOMA Smart Lock adalah investasi keamanan terbaik untuk rumah kalian.","neutral"),
("Klik tombol beli sekarang untuk PALOMA Smart Lock, pengiriman cepat ke seluruh Indonesia!","happy"),
("Terbatas hanya untuk penonton live hari ini, PALOMA Smart Lock dengan bonus aksesori eksklusif!","dramatic"),
("Sudah ribuan keluarga Indonesia mempercayai PALOMA Smart Lock, sekarang giliran rumah kalian!","happy"),
("Order PALOMA Smart Lock sekarang dan dapatkan gratis ongkir ke seluruh wilayah Indonesia.","happy"),
("Jangan sampai nyesel, PALOMA Smart Lock dengan harga live ini nggak akan ada lagi setelah live selesai.","dramatic"),
("Yuk buruan order PALOMA Smart Lock, ketik BELI di chat dan kita proses langsung!","happy"),
("PALOMA Smart Lock pilihan tepat untuk keamanan rumah modern, order sekarang dan rasakan bedanya.","neutral"),
("Harga spesial PALOMA Smart Lock hanya untuk kalian yang nonton live sekarang, jangan sampai kehabisan!","dramatic"),
("Klik keranjang belanja sekarang untuk PALOMA Smart Lock, stok hari ini sangat terbatas!","dramatic"),
("Investasi keamanan terbaik dimulai dari PALOMA Smart Lock, order sekarang dan proteksi rumah kalian.","neutral"),
("Yuk langsung checkout PALOMA Smart Lock, tim kita siap bantu dari order sampai instalasi!","happy"),
]
for i,(text,emotion) in enumerate(paloma_cta,1):
    clips.append({"id":f"B_paloma_cta_{i:03d}","category":"B_paloma_cta","text":text,"tags":["paloma","cta","order","beli"],"emotion":emotion})
pintu_lipat_demo=[
("Sekarang kita lihat Reaim Pintu Lipat, solusi cerdas untuk memaksimalkan ruang di rumah kalian.","neutral"),
("Reaim Pintu Lipat ini bisa dilipat hingga 90 persen dari ukuran aslinya, hemat tempat banget!","happy"),
("Material Reaim Pintu Lipat menggunakan aluminium premium yang ringan tapi kuat dan tahan lama.","neutral"),
("Dengan Reaim Pintu Lipat, ruangan sempit pun bisa terasa lebih luas dan fungsional.","happy"),
("Sistem rel Reaim Pintu Lipat sangat halus dan senyap, nggak berisik sama sekali saat dibuka tutup.","neutral"),
("Reaim Pintu Lipat tersedia dalam berbagai ukuran custom sesuai kebutuhan ruangan kalian.","neutral"),
("Finishing Reaim Pintu Lipat sangat rapi dan elegan, cocok untuk berbagai gaya interior rumah.","happy"),
("Pemasangan Reaim Pintu Lipat mudah dan cepat, bisa selesai dalam hitungan jam saja.","happy"),
("Reaim Pintu Lipat ideal untuk kamar tidur, ruang kerja, dapur, atau area mana saja yang butuh privasi.","neutral"),
("Ketebalan panel Reaim Pintu Lipat dirancang optimal untuk kekuatan maksimal dengan bobot minimal.","neutral"),
("Reaim Pintu Lipat hadir dalam pilihan warna dan motif yang beragam, bisa disesuaikan selera kalian.","happy"),
("Sistem kunci Reaim Pintu Lipat aman dan mudah dioperasikan oleh semua anggota keluarga.","neutral"),
("Reaim Pintu Lipat cocok untuk renovasi rumah lama maupun pembangunan rumah baru.","neutral"),
("Dengan Reaim Pintu Lipat, kalian bisa bagi ruangan besar menjadi dua area fungsional dengan mudah.","happy"),
("Reaim Pintu Lipat tahan terhadap kelembaban dan perubahan suhu, cocok untuk iklim tropis Indonesia.","neutral"),
("Desain Reaim Pintu Lipat yang minimalis modern akan memperindah tampilan interior rumah kalian.","happy"),
("Reaim Pintu Lipat sudah diuji kekuatannya dan terbukti tahan hingga puluhan ribu kali buka tutup.","neutral"),
("Solusi pintu lipat terbaik untuk rumah Indonesia, Reaim Pintu Lipat kualitas premium harga bersahabat.","happy"),
]
for i,(text,emotion) in enumerate(pintu_lipat_demo,1):
    clips.append({"id":f"C_pintu_lipat_demo_{i:03d}","category":"C_pintu_lipat_demo","text":text,"tags":["pintu_lipat","reaim","demo","product"],"emotion":emotion})
pintu_lipat_cta=[
("Yuk order Reaim Pintu Lipat sekarang, ketik PINTU di chat atau klik keranjang di bawah!","happy"),
("Stok Reaim Pintu Lipat terbatas, jangan sampai kehabisan! Order sekarang sebelum sold out.","dramatic"),
("Dapatkan Reaim Pintu Lipat dengan harga spesial live, lebih hemat dari harga normal!","happy"),
("Reaim Pintu Lipat solusi terbaik untuk rumah kalian, order sekarang dan transformasi ruangan dimulai!","happy"),
("Ketik LIPAT di kolom chat sekarang dan tim kita akan bantu proses orderan kalian segera.","happy"),
("Promo Reaim Pintu Lipat hanya berlaku selama live ini, jangan lewatkan penawaran terbatas ini!","dramatic"),
("Klik tombol beli untuk Reaim Pintu Lipat sekarang, pengiriman ke seluruh Indonesia tersedia!","happy"),
("Reaim Pintu Lipat dengan harga live eksklusif, hemat lebih banyak dibanding beli offline!","happy"),
("Jangan tunda renovasi rumah kalian, Reaim Pintu Lipat siap dikirim ke alamat kalian hari ini!","happy"),
("Order Reaim Pintu Lipat sekarang dan dapatkan bonus konsultasi desain gratis dari tim kami!","happy"),
("Ribuan rumah di Indonesia sudah pakai Reaim Pintu Lipat, sekarang giliran rumah kalian!","happy"),
("Harga spesial Reaim Pintu Lipat hanya untuk penonton live hari ini, buruan order sebelum habis!","dramatic"),
("Yuk langsung checkout Reaim Pintu Lipat, tim instalasi kami siap membantu pemasangan di rumah kalian.","happy"),
("Reaim Pintu Lipat investasi terbaik untuk kenyamanan dan estetika rumah kalian, order sekarang!","neutral"),
("Klik keranjang belanja untuk Reaim Pintu Lipat, stok hari ini sangat terbatas jangan sampai kehabisan!","dramatic"),
("Transformasi ruangan kalian dengan Reaim Pintu Lipat, order sekarang dan rasakan perbedaannya!","happy"),
("Reaim Pintu Lipat dengan garansi resmi, order sekarang dan belanja dengan tenang!","neutral"),
("Yuk buruan order Reaim Pintu Lipat, ketik BELI di chat dan kita proses langsung sekarang!","happy"),
]
for i,(text,emotion) in enumerate(pintu_lipat_cta,1):
    clips.append({"id":f"C_pintu_lipat_cta_{i:03d}","category":"C_pintu_lipat_cta","text":text,"tags":["pintu_lipat","reaim","cta","order","beli"],"emotion":emotion})
tnw_demo=[
("Sekarang kita kenalan sama TNW Chopper Blender, blender serbaguna yang wajib ada di dapur kalian!","happy"),
("TNW Chopper Blender ini bisa mencacah, menggiling, dan memblender berbagai bahan makanan dalam hitungan detik.","neutral"),
("Kapasitas TNW Chopper Blender cukup besar, bisa sekaligus proses bahan untuk masakan satu keluarga.","neutral"),
("Motor TNW Chopper Blender sangat bertenaga tapi tetap hemat listrik, cocok untuk pemakaian sehari-hari.","neutral"),
("Pisau TNW Chopper Blender terbuat dari stainless steel premium yang tajam dan tidak mudah berkarat.","neutral"),
("TNW Chopper Blender mudah dibersihkan, cukup isi air dan sabun lalu nyalakan sebentar, bersih sempurna!","happy"),
("Desain TNW Chopper Blender compact dan elegan, tidak makan banyak tempat di meja dapur kalian.","happy"),
("TNW Chopper Blender bisa digunakan untuk membuat jus, smoothie, saus, bumbu, dan masih banyak lagi.","happy"),
("Tingkat kebisingan TNW Chopper Blender sangat rendah, nggak akan ganggu aktivitas lain di rumah.","neutral"),
("TNW Chopper Blender dilengkapi fitur keamanan otomatis yang mencegah penggunaan yang tidak aman.","neutral"),
("Material bowl TNW Chopper Blender food grade dan BPA free, aman untuk seluruh keluarga termasuk anak-anak.","neutral"),
("TNW Chopper Blender hadir dalam beberapa pilihan warna yang cerah dan modern untuk dapur kalian.","happy"),
("Dengan TNW Chopper Blender, memasak jadi lebih cepat, mudah, dan menyenangkan setiap harinya.","happy"),
("TNW Chopper Blender cocok untuk ibu rumah tangga, chef rumahan, maupun pelaku usaha kuliner.","neutral"),
("Garansi resmi TNW Chopper Blender memberikan ketenangan pikiran dalam setiap pembelian kalian.","neutral"),
("TNW Chopper Blender sudah diuji dan terbukti tahan lama untuk pemakaian intensif setiap hari.","neutral"),
("Teknologi blade TNW Chopper Blender memastikan hasil cacahan yang merata dan konsisten setiap saat.","neutral"),
("TNW Chopper Blender adalah partner memasak terbaik yang akan mengubah pengalaman dapur kalian.","happy"),
]
for i,(text,emotion) in enumerate(tnw_demo,1):
    clips.append({"id":f"D_tnw_demo_{i:03d}","category":"D_tnw_demo","text":text,"tags":["tnw","chopper","blender","demo","product"],"emotion":emotion})
tnw_cta=[
("Yuk order TNW Chopper Blender sekarang, ketik TNW di chat atau klik keranjang di bawah!","happy"),
("Stok TNW Chopper Blender terbatas, jangan sampai kehabisan! Order sekarang sebelum sold out.","dramatic"),
("Dapatkan TNW Chopper Blender dengan harga spesial live, lebih hemat dari harga normal!","happy"),
("TNW Chopper Blender solusi dapur terbaik, order sekarang dan masak jadi lebih mudah dan menyenangkan!","happy"),
("Ketik CHOPPER di kolom chat sekarang dan tim kita akan bantu proses orderan kalian segera.","happy"),
("Promo TNW Chopper Blender hanya berlaku selama live ini, jangan lewatkan penawaran terbatas ini!","dramatic"),
("Klik tombol beli untuk TNW Chopper Blender sekarang, pengiriman ke seluruh Indonesia tersedia!","happy"),
("TNW Chopper Blender dengan harga live eksklusif, hemat lebih banyak dibanding beli di toko offline!","happy"),
("Jangan tunda upgrade dapur kalian, TNW Chopper Blender siap dikirim ke alamat kalian hari ini!","happy"),
("Order TNW Chopper Blender sekarang dan dapatkan bonus resep eksklusif dari chef profesional kami!","happy"),
("Ribuan dapur di Indonesia sudah pakai TNW Chopper Blender, sekarang giliran dapur kalian!","happy"),
("Harga spesial TNW Chopper Blender hanya untuk penonton live hari ini, buruan order sebelum habis!","dramatic"),
("Yuk langsung checkout TNW Chopper Blender, pengiriman cepat dan aman ke seluruh Indonesia!","happy"),
("TNW Chopper Blender investasi terbaik untuk kemudahan memasak sehari-hari, order sekarang!","neutral"),
("Klik keranjang belanja untuk TNW Chopper Blender, stok hari ini sangat terbatas jangan kehabisan!","dramatic"),
("Upgrade dapur kalian dengan TNW Chopper Blender, order sekarang dan rasakan kemudahannya!","happy"),
("TNW Chopper Blender dengan garansi resmi, order sekarang dan belanja dengan tenang dan percaya diri!","neutral"),
("Yuk buruan order TNW Chopper Blender, ketik BELI di chat dan kita proses langsung sekarang!","happy"),
]
for i,(text,emotion) in enumerate(tnw_cta,1):
    clips.append({"id":f"D_tnw_cta_{i:03d}","category":"D_tnw_cta","text":text,"tags":["tnw","chopper","blender","cta","order","beli"],"emotion":emotion})
reply_price=[
("Untuk harga produk ini, kalian bisa cek langsung di link bio atau ketik HARGA di kolom chat ya!","neutral"),
("Harga spesial live hari ini lebih murah dari harga normal, langsung klik keranjang untuk lihat harganya!","happy"),
("Soal harga, kita kasih yang terbaik buat kalian! Cek di keranjang belanja ya untuk harga terupdate.","happy"),
("Harga produk ini sangat terjangkau dan worth it banget untuk kualitas yang kalian dapatkan!","happy"),
("Untuk info harga lengkap, ketik HARGA di chat dan tim kita akan langsung balas kalian ya!","neutral"),
("Harga live kita selalu lebih murah, jadi jangan lewatkan kesempatan beli sekarang!","happy"),
("Soal harga jangan khawatir, kita selalu kasih harga terbaik dan paling kompetitif di pasaran.","neutral"),
("Harga produk ini udah termasuk garansi resmi dan layanan purna jual yang memuaskan lho!","happy"),
("Untuk harga grosir atau pembelian dalam jumlah banyak, DM kita ya di akun interiorhack!","neutral"),
("Harga yang kalian lihat di keranjang sudah termasuk diskon live eksklusif hari ini!","happy"),
("Soal harga kita transparan banget, nggak ada biaya tersembunyi, yang kalian lihat itu yang kalian bayar.","neutral"),
("Harga produk ini sangat kompetitif, coba bandingkan dengan toko lain pasti kita lebih murah!","happy"),
("Untuk pertanyaan harga lebih detail, kalian bisa chat langsung dengan tim kita ya!","neutral"),
("Harga spesial ini hanya untuk penonton live, jadi manfaatkan kesempatan ini sebaik mungkin!","dramatic"),
("Soal harga kita fleksibel, ada berbagai pilihan paket yang bisa disesuaikan dengan budget kalian.","neutral"),
("Harga terbaik ada di live kita hari ini, jangan sampai menyesal karena tidak order sekarang!","dramatic"),
("Untuk info harga dan promo terbaru, follow akun kita dan aktifkan notifikasi ya!","neutral"),
("Harga produk ini sudah sangat terjangkau untuk kualitas premium yang kalian dapatkan, worth it banget!","happy"),
]
for i,(text,emotion) in enumerate(reply_price,1):
    clips.append({"id":f"E_reply_price_{i:03d}","category":"E_reply_price","text":text,"tags":["reply","price","harga","promo"],"emotion":emotion})
closing=[
("Makasih banyak semuanya udah nemenin live kita hari ini, sampai jumpa di live berikutnya ya!","happy"),
("Terima kasih sudah hadir di live interiorhack, jangan lupa follow dan aktifkan notifikasi untuk live selanjutnya!","happy"),
("Live kita hari ini sampai di sini dulu, makasih buat semua yang udah join dan support kita!","happy"),
("Sampai jumpa di live berikutnya teman-teman! Jangan lupa share ke teman-teman kalian ya.","happy"),
("Terima kasih sudah belanja dan support interiorhack, semoga produknya memuaskan dan bermanfaat!","happy"),
("Live selesai, makasih buat semua yang udah order hari ini! Pesanan kalian segera kami proses.","happy"),
("Sampai ketemu lagi di live interiorhack berikutnya, stay tuned untuk promo dan produk baru!","happy"),
("Makasih udah setia nemenin live kita, kalian adalah penonton terbaik yang pernah ada!","happy"),
("Live hari ini resmi ditutup, terima kasih atas kepercayaan dan dukungan kalian semua!","happy"),
("Jangan lupa kasih bintang lima dan review positif ya, itu sangat membantu kita berkembang!","happy"),
("Sampai jumpa di live berikutnya, semoga hari kalian menyenangkan dan penuh berkah!","happy"),
("Terima kasih sudah menjadi bagian dari keluarga besar interiorhack, see you next live!","happy"),
("Live kita tutup dulu ya, makasih buat semua yang udah hadir dan berinteraksi hari ini!","happy"),
("Sampai ketemu lagi teman-teman, jaga kesehatan dan semoga produk interiorhack bermanfaat untuk kalian!","happy"),
("Terima kasih sudah setia menonton live interiorhack, sampai ketemu di live berikutnya yang lebih seru!","happy"),
("Akhir kata, makasih banyak buat semua yang udah hadir dan berbelanja, kalian luar biasa!","happy"),
]
for i,(text,emotion) in enumerate(closing,1):
    clips.append({"id":f"Z_closing_{i:03d}","category":"Z_closing","text":text,"tags":["closing","goodbye","terima_kasih"],"emotion":emotion})
print(f"Total: {len(clips)}")
import pathlib,yaml
out=pathlib.Path("livetik/apps/worker/config/clips_script.yaml")
with open(out,"w",encoding="utf-8") as f2:
    yaml.dump({"clips":clips},f2,allow_unicode=True,default_flow_style=False,sort_keys=False)
print("Written:",out)
