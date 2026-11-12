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
- Aynı belgenin iki sürümü farklı değer verdiğinde model bazen sormak yerine ikisini de listeliyor. Taban ölçümünde görüldü ([0004](decisions/0004-olcum-sonuclari.md)): değerler ve kaynakları doğru, yalnız netleştirme atlandı. `dikim-revizyon-netlestir`: seed 7'de 5/5, seed 11'de 1/5; fark belgeden mi modelin rastgeleliğinden mi geliyor, ölçülmedi. Gerçek belgelerde ne sıklıkla olduğuna bakılacak.
- Model değişince önceki beden düşüyor; sistem o zaman bedeni yeniden soruyor. `dikim-sohbet-1-t4` iki sette önbelleksiz 10 tekrarın hiçbirinde geçmedi, yani her seferinde oluyor: takip sorusunu tamamlayan yardımcı model bedeni düşürüyor. Çözüm bekliyor.
- Alıntı denetimi (sade yol): satır içi kod içindeki alt çizgi ya da kelime içi yıldız (`` `my_var` ``, `` `x**2` ``) ayrıştırıcıdan önce kaçışla korunduğu için kodun içinde ters bölü kalıyor; bu kodu ters tırnaksız alıntılayan doğru alıntı reddediliyor (Bugbot, PR #4, "Code spans keep pre-escaped marks"). Yalnız haksız ret, gerileme değil; sonra ele alınacak.
- Doğrulama anlam düzeyinde denetim yapmıyor: olumsuzlama ("zorunludur" → "zorunlu değildir") ve aynı satırda başka sütunun değerini yazmak ("Beden S: 72 | Beden M: 74" satırından "M beden 72") alıntı ve sayılar doğru olduğu için doğrulanıyor. İkisi de biçim düzeyinde bir kuralla çözülemiyor, ayrı tasarım ister.
- Kaynakta birimi olmayan değere cevapta birim ekleniyor ("M: 40,5" → "40,5 cm"); doğrulama bunu reddetmiyor, yalnız kaynaktaki birimle çelişen birimi reddediyor. Mac'teki önbellek ölçümünde iki setin 51 cevap öğesinden 19'unda oldu. Reddetmek büyük haksız ret demek; çözümü cevap istemini değiştirmek (önbellek geçersizleşir), ayrıca ölçülecek.
- Cevap tamlığı kuralı (istem, 9. kural) FastReact'ta 1, 3 ve 7. sorulara ayar adı ya da menü yolu ekletti; 4. soruda model "Hide sequence characters" adını, getirilen ilk parçada olduğu halde yazmadı. 8. soruda cevap `[Screenshot: LL undo]` yer işaretini ad gibi aktardı. İstem ikinci kez denenmedi (her soru bir kez soruldu).
- Cümle başında büyük harfle başlayan sayı ("30. Gün") hâlâ madde işareti sayılıp denetimden çıkıyor; küçük harfle başlayan artık denetleniyor.

## Belge yönetimi

- Hazır bir belge yeniden işlenirken, işlem bitene kadar aramada görünmüyor; eski hali de kullanılamıyor. Pilot için kabul edildi. Eski sürümü işlem bitene kadar aramada tutmak ayrı bir tasarım ister (iki sürümün parçaları ve vektörleri bir süre birlikte durur).

## Yayına almadan önce

- Soru kaydının saklama süresi açık: her soru (kullanıcının yazdığı metin dahil) SQLite'ta süresiz kalıyor, silme ya da anonimleştirme yok. Yayına almadan önce saklama süresi ve kimin okuyabileceği kararlaştırılmalı; ses ve cevap metninin tamamı zaten kaydedilmiyor.
- Giriş kapalı: arayüz ağa açılırsa ağdaki herkes belge görebilir ve yükleyebilir. Şu an yalnız `127.0.0.1` adresine açık; tabletler için açmadan önce giriş ya da ağ kısıtı gerekir.
- Yüklenen Office dosyaları işçide LibreOffice ile açılıyor; işçinin internet erişimi kapatılabilir.
- Yerel kurulumda arayüzü nginx değil API sunuyor: nginx'teki güvenlik başlıkları (CSP, X-Frame-Options, nosniff, Referrer-Policy) ve `/api/ask`, `/api/speak`, `/api/transcribe` için hız sınırı yerelde yok. Ağa açmadan önce bunlar API'ye ya da önündeki bir vekil sunucuya eklenmeli.

## Kurulum

- Sunucu (Docker) kurulumundaki Docling model indirme komutu (`docling-tools models download`) önceki bilgisayarda takıldı ve hiç doğrulanmadı. Yerel kurulumda bu komut kullanılmıyor, modeller ilk belgede kendiliğinden iniyor. Sunucuya ilk kurulumda denenecek; takılırsa nedeni bulunacak.
- Docker paketi (compose, imajlar) SQLite ve tek süreç değişikliğinden sonra bu bilgisayarda denenemedi; yalnız CI'daki `services` işi açılışı sınıyor. Sunucuya kurulurken API ve işçinin aynı SQLite birimini paylaşması uçtan uca denenecek.
