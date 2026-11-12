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
- Cümle başında büyük harfle başlayan sayı ("30. Gün") hâlâ madde işareti sayılıp denetimden çıkıyor; küçük harfle başlayan artık denetleniyor.
- Netleştirme adayları aynı adımı farklı menü yoluyla anlatıyorsa netleştirme sürüyor: FastReact'ta "Planlama tahtasından siparişin teslim tarihini nasıl değiştiririm?" iki belgede aynı gövde metnini taşıyor, ama menü yolları farklı ("Main Menu > Planning > …" ve "Main Menu > Low Level Planning > …"); ikinci cevap menü yolunu alıntıladığı için "aynı cevap" sayılmadı. İki yolu kaynaklarıyla birlikte vermek ayrı bir karar.
- Belgelerin kendisi hakkındaki takip soruları ("bunların hepsi gerçekten release notes mu") çıkmaz sokakta: envanter cevabı sohbet bağlamı bırakmıyor, belge adları ve türleri hakkındaki soru katalogdan değil aramadan cevaplanıyor. Öneri: envanterin gösterdiği belgeleri bağlama koymak ve başlık ya da sayı soran takip sorusunu katalogdan cevaplamak; ayrı tasarım ister. Aynı türdeki "release notes dosyalarında ne var" sorusunu niyet sınıflandırıcı bir koşuda envanter, bir koşuda belge sorusu saydı.
- Grafiklerde değer ile etiketi arasındaki bağ kopuyor: çubuk grafikteki `331`, `268`, `214` ve ay adları ayrı parçalara düşüyor, "Mart ayında fire adedi kaç?" bulunamadı oluyor. Grafik okuma ayrı tasarım ister.
- Excel değerleri gösterilen biçimden farklı okunuyor: `%12` → `0.12`, `1.234,50 TL` → `1234.5`. Kayıtlı değeri olmayan formül hücresi (`=C2*2`) uyarısız kayboluyor (`ingest/spreadsheet.py`). Kaynaktaki yazılışla eşleşme bozulur, değer sessizce eksilir.

## Belge yönetimi

- Hazır bir belge yeniden işlenirken, işlem bitene kadar aramada görünmüyor; eski hali de kullanılamıyor. Pilot için kabul edildi. Eski sürümü işlem bitene kadar aramada tutmak ayrı bir tasarım ister (iki sürümün parçaları ve vektörleri bir süre birlikte durur).

## Yayına almadan önce

- Soru kaydının saklama süresi açık: her soru (kullanıcının yazdığı metin dahil) SQLite'ta süresiz kalıyor, silme ya da anonimleştirme yok. Yayına almadan önce saklama süresi ve kimin okuyabileceği kararlaştırılmalı; ses ve cevap metninin tamamı zaten kaydedilmiyor.
- Giriş kapalı: arayüz ağa açılırsa ağdaki herkes belge görebilir ve yükleyebilir. Şu an yalnız `127.0.0.1` adresine açık; tabletler için açmadan önce giriş ya da ağ kısıtı gerekir.
- Yüklenen Office dosyaları işçide LibreOffice ile açılıyor; işçinin internet erişimi kapatılabilir.
- Yerel kurulumda arayüzü nginx değil API sunuyor: nginx'teki güvenlik başlıkları (CSP, X-Frame-Options, nosniff, Referrer-Policy) ve `/api/ask`, `/api/speak`, `/api/transcribe` için hız sınırı yerelde yok. Ağa açmadan önce bunlar API'ye ya da önündeki bir vekil sunucuya eklenmeli.

## Sağlayıcı

- İlk token için konan zaman aşımı (`answer_first_token_seconds`, varsayılan 2,5 sn) akışın her okumasına uygulanıyor (`generation/openrouter.py`). İlk tokendan sonra sağlayıcı 2,5 sn'den uzun duraklarsa cevap `ReadTimeout` ile düşüyor.

## Kurulum

- Sunucu (Docker) kurulumundaki Docling model indirme komutu (`docling-tools models download`) önceki bilgisayarda takıldı ve hiç doğrulanmadı. Yerel kurulumda bu komut kullanılmıyor, modeller ilk belgede kendiliğinden iniyor. Sunucuya ilk kurulumda denenecek; takılırsa nedeni bulunacak.
- Docker paketi (compose, imajlar) SQLite ve tek süreç değişikliğinden sonra bu bilgisayarda denenemedi; yalnız CI'daki `services` işi açılışı sınıyor. Sunucuya kurulurken API ve işçinin aynı SQLite birimini paylaşması uçtan uca denenecek.
