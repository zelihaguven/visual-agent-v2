# Açık notlar

Kararı ya da işi sonraya bırakılan konular. Biten madde silinir.

## Gerçek belgelerle ince ayar

- **Kod türleri ve biçimleri:** Kodlar belge işlenirken metinden otomatik çıkarılıyor, ama gerçek belgelerde kodların biçimi ve sırası aynı olmayabilir. Harf ve rakam içeren her şey "kod" sayılıyor: etiket kodu ile ürün kodu ayrılmıyor, `A4` gibi ifadeler fazladan sayılabilir, `1162/A` gibi biçimler kaçabilir. Gerçek dosyalar gelince ölçülecek; gerekirse belge işlerken kodları türüne ayıran bir adım eklenecek.
- **Tablo düzenleri:** Üretilmiş tablolar düzenli. Farklı sütun sırası ve başlıklarda bedene göre netleştirme yeniden denenecek.

## Ses

- Sesle söz kesme bilgisayarda hoparlörle çalıştı; atölye gürültüsünde ve tablette eşik yeniden denenecek.
- Söylenen kodlar yazıya çevrilirken bozulabiliyor ("PNT-1162" yerine "NT1162"). Konuşma modunda soru otomatik gönderildiği için gerçek konuşmacıyla ölçülecek.
- Tablet Safari'de otomatik ses çalma denenmedi.
- Ağdaki tabletlerden mikrofon için HTTPS gerekiyor.

## Cevap kalitesi

- Taranmış belgede bir etiket sorusu son sınavda "bulunamadı" oldu; gerçek taramalarda izlenecek.
- Fotoğraf, gömülü görsel ve taramadan OCR ile okunan değerlerde iki okuma uyuşursa değer gösterilir, cevap "Kısmen doğrulandı" olur; uyuşmazsa değer gizlenir, cevap "Doğrulanamadı" olur. Kısa kenarı 50 pt'den ya da alanı sayfanın %2'sinden küçük görseller okunmaz, belge listesinde uyarı çıkar. Gerçek fotoğraflarla denenecek.
- GPT-OSS 120B ve GLM 5.3 Flash isteklerimize cevap vermedi; istemci uyumsuzluğu çözülürse hız için yeniden ölçülebilir.
- Aynı belgenin iki sürümü farklı değer verdiğinde model bazen sormak yerine ikisini de listeliyor. Taban ölçümünde görüldü ([0004](decisions/0004-olcum-sonuclari.md)): değerler ve kaynakları doğru, yalnız netleştirme atlandı (son sınavda 5 tekrarın 4'ünde). Gerçek belgelerde ne sıklıkla olduğuna bakılacak.
- Model değişince önceki beden bazen düşüyor; sistem o zaman bedeni yeniden soruyor.

## Yayına almadan önce

- Giriş kapalı: arayüz ağa açılırsa ağdaki herkes belge görebilir ve yükleyebilir. Şu an yalnız `127.0.0.1` adresine açık; tabletler için açmadan önce giriş ya da ağ kısıtı gerekir.
- Yüklenen Office dosyaları işçide LibreOffice ile açılıyor; işçinin internet erişimi kapatılabilir.
- Yerel kurulumda arayüzü nginx değil API sunuyor: nginx'teki güvenlik başlıkları (CSP, X-Frame-Options, nosniff, Referrer-Policy) ve `/api/ask`, `/api/speak`, `/api/transcribe` için hız sınırı yerelde yok. Ağa açmadan önce bunlar API'ye ya da önündeki bir vekil sunucuya eklenmeli.

## Kurulum

- Sunucu (Docker) kurulumundaki Docling model indirme komutu (`docling-tools models download`) önceki bilgisayarda takıldı ve hiç doğrulanmadı. Yerel kurulumda bu komut kullanılmıyor, modeller ilk belgede kendiliğinden iniyor. Sunucuya ilk kurulumda denenecek; takılırsa nedeni bulunacak.
- Docker paketi (compose, imajlar) SQLite ve tek süreç değişikliğinden sonra bu bilgisayarda denenemedi; yalnız CI'daki `services` işi açılışı sınıyor. Sunucuya kurulurken API ve işçinin aynı SQLite birimini paylaşması uçtan uca denenecek.
