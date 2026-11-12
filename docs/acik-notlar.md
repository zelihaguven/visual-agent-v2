# Açık notlar

Kararı ya da işi sonraya bırakılan konular. Biten madde silinir.

## Gerçek belgelerle ince ayar

- **Kod türleri ve biçimleri:** Kodlar belge işlenirken metinden otomatik çıkarılıyor, ama gerçek belgelerde kodların biçimi ve sırası aynı olmayabilir. Harf ve rakam içeren her şey "kod" sayılıyor: etiket kodu ile ürün kodu ayrılmıyor, `A4` gibi ifadeler fazladan sayılabilir, `1162/A` gibi biçimler kaçabilir. Gerçek dosyalar gelince ölçülecek; gerekirse belge işlerken kodları türüne ayıran bir adım eklenecek.
- **Tablo düzenleri:** Üretilmiş tablolar düzenli. Farklı sütun sırası ve başlıklarda bedene göre netleştirme yeniden denenecek.

## Markdown belgeler

- Hazır gelen markdown'da OCR kökenli metin işaretlenmiyor: FastReact sürüm notları OCR'dan çıkarılmış ("Text extracted by OCR" notuyla), ama `.md` metni OCR'dan gelmemiş sayılıyor; OCR değerlerine uygulanan "Kısmen doğrulandı" kuralı bu metinde çalışmıyor.

## Ses

- Sesle söz kesme bilgisayarda hoparlörle çalıştı; atölye gürültüsünde ve tablette eşik yeniden denenecek.
- Söylenen kodlar yazıya çevrilirken bozulabiliyor ("PNT-1162" yerine "NT1162"). Konuşma modunda soru otomatik gönderildiği için gerçek konuşmacıyla ölçülecek.
- Tablet Safari'de otomatik ses çalma denenmedi.
- Ağdaki tabletlerden mikrofon için HTTPS gerekiyor.

## Cevap kalitesi

- Taranmış belgede bir etiket sorusu son sınavda "bulunamadı" oldu; gerçek taramalarda izlenecek.
- Fotoğraf, gömülü görsel ve taramadan OCR ile okunan değerlerde iki okuma uyuşursa değer gösterilir, cevap "Kısmen doğrulandı" olur; uyuşmazsa değer gizlenir, cevap "Doğrulanamadı" olur. Kısa kenarı 50 pt'den ya da alanı sayfanın %2'sinden küçük görseller okunmaz, belge listesinde uyarı çıkar. Gerçek fotoğraflarla denenecek.
- GPT-OSS 120B ve GLM 5.3 Flash isteklerimize cevap vermedi; istemci uyumsuzluğu çözülürse hız için yeniden ölçülebilir.
- Aynı belgenin iki sürümü farklı değer verdiğinde model bazen sormak yerine ikisini de listeliyor. Taban ölçümünde görüldü ([0004](kararlar.md#karar-0004)): değerler ve kaynakları doğru, yalnız netleştirme atlandı. `dikim-revizyon-netlestir`: seed 7'de 5/5, seed 11'de 1/5; fark belgeden mi modelin rastgeleliğinden mi geliyor, ölçülmedi. Gerçek belgelerde ne sıklıkla olduğuna bakılacak.
- Model değişince önceki beden düşüyor; sistem o zaman bedeni yeniden soruyor. `dikim-sohbet-1-t4` iki sette önbelleksiz 10 tekrarın hiçbirinde geçmedi, yani her seferinde oluyor: takip sorusunu tamamlayan yardımcı model bedeni düşürüyor. Çözüm bekliyor.
- Alıntı denetimi (sade yol): satır içi kod içindeki alt çizgi ya da kelime içi yıldız (`` `my_var` ``, `` `x**2` ``) ayrıştırıcıdan önce kaçışla korunduğu için kodun içinde ters bölü kalıyor; bu kodu ters tırnaksız alıntılayan doğru alıntı reddediliyor (Bugbot, PR #4, "Code spans keep pre-escaped marks"). Yalnız haksız ret, gerileme değil; sonra ele alınacak.
- Doğrulama anlam düzeyinde denetim yapmıyor: olumsuzlama ("zorunludur" → "zorunlu değildir") ve aynı satırda başka sütunun değerini yazmak ("Beden S: 72 | Beden M: 74" satırından "M beden 72") alıntı ve sayılar doğru olduğu için doğrulanıyor. Önce davranış ölçüldü: sınır setine 7 yanlış sütun sorusu (komşu sütunda yakın değer; Excel, PDF ve Word tablosu, biri yanlış değeri onaylatan soru) ve 5 olumsuzlama sorusu (Türkçe ve İngilizce kaynak, biri olumlu denetim) eklendi, her soru bir kez soruldu (2026-11-12, `google/gemma-4-26b-a4b-it`). 12 cevabın hepsi doğruydu: komşu sütunun değeri yazılmadı, olumsuzluk tersine çevrilmedi; doğrulanmış yanlış 0. Olumsuzlama cevapları puanlayıcıyla değil, cevap metni okunarak sınıflandırıldı. Hata görülmediği için kural yazılmadı (yön kararı: biçim ve dil düzeyinde kural; model ya da LLM denetimi yok). Doğrulama bu hataları hâlâ yakalayamıyor; gerçek belgelerde ve tablolarda görülürse yalnız görülen kısım için kural önerilecek.
- Kaynakta birimi olmayan değere cevapta birim ekleniyor ("M: 40,5" → "40,5 cm"); doğrulama bunu reddetmiyor, yalnız kaynaktaki birimle çelişen birimi reddediyor. Mac'teki önbellek ölçümünde iki setin 51 cevap öğesinden 19'unda oldu. Reddetmek büyük haksız ret demek; çözümü cevap istemini değiştirmek (önbellek geçersizleşir), ayrıca ölçülecek.
- Alıntı denetiminde birimler büyük-küçük harf farkı yok sayılarak karşılaştırılıyor; anlamı harfe bağlı birimler ("MB"/"Mb", "mA"/"MA") ayrılmıyor.
- Markdown okuma değişikliğinden sonraki FastReact ölçümünde (her soru bir kez) iki soruda doğru bilgi gizlendi: soru 5'te model alıntıyı kaynaktan farklı kopyaladı ("name, and,", "theproduct"), soru 17'de sürüm numarasını (4.44) taşıyan satırı alıntıya almadı. İkisi de modelin alıntı seçimi; kaynak metin parçada var. Önceki koşuda aynı sorular doğrulanmıştı; tekrar ölçülmedi, kararlılığı bilinmiyor.
- Cümle başında büyük harfle başlayan sayı ("30. Gün") hâlâ madde işareti sayılıp denetimden çıkıyor; küçük harfle başlayan artık denetleniyor.
- Netleştirme adayları aynı adımı farklı menü yoluyla anlatıyorsa netleştirme sürüyor: FastReact'ta "Planlama tahtasından siparişin teslim tarihini nasıl değiştiririm?" iki belgede aynı gövde metnini taşıyor, ama menü yolları farklı ("Main Menu > Planning > …" ve "Main Menu > Low Level Planning > …"); ikinci cevap menü yolunu alıntıladığı için "aynı cevap" sayılmadı. İki yolu kaynaklarıyla birlikte vermek ayrı bir karar.
- Belgelerin kendisi hakkındaki takip soruları ("bunların hepsi gerçekten release notes mu") çıkmaz sokakta: envanter cevabı sohbet bağlamı bırakmıyor, belge adları ve türleri hakkındaki soru katalogdan değil aramadan cevaplanıyor. Öneri: envanterin gösterdiği belgeleri bağlama koymak ve başlık ya da sayı soran takip sorusunu katalogdan cevaplamak; ayrı tasarım ister. Aynı türdeki "release notes dosyalarında ne var" sorusunu niyet sınıflandırıcı bir koşuda envanter, bir koşuda belge sorusu saydı.
- Yeniden parçalamadan sonra FastReact ek sorularında "release notes dosyalarında ne var" ve takibi "bunların hepsi gercekten release notes mu" "bulunamadı" oldu; önceki koşuda ikisi de doğrulanmış tek cümleyle cevaplanmıştı (sürüm notlarının başındaki "Source: … Release notes (version history …)" satırından). Tek koşu; nedeni ve kalıcı olup olmadığı incelenmedi.
- Grafiklerde değer ile etiketi arasındaki bağ kopuyor: çubuk grafikteki `331`, `268`, `214` ve ay adları ayrı parçalara düşüyor, "Mart ayında fire adedi kaç?" bulunamadı oluyor. Grafik okuma ayrı tasarım ister.
- Excel sayıları gösterilen biçimle yazılıyor, ama dosyada bölge ayarı yok: Türkçe bölge ayarı varsayılıyor (ondalık virgül, binlik nokta; `ingest/spreadsheet.py`). Yüzde işaretinin yeri biçim kodundaki gibi (`12%`); Türkçe Excel'in `%12` gösterip göstermediği denenmedi. Tarih, kesir ve bilimsel gösterim biçimleri desteklenmiyor: tarih ISO biçiminde, diğerleri genel biçimde yazılıyor. Eksi bölümü parantez ya da yalnız renk olan biçimlerde değer eksi işaretiyle yazılıyor. Gerçek Excel dosyalarıyla denenecek.

## Belge yönetimi

- Aynı belgenin eski ve yeni sürümü birlikte yüklenebiliyor; ikisi de aramaya giriyor, aralarındaki sürüm ilişkisi bilinmiyor. Farklı değer verdiklerinde ne olduğu "Cevap kalitesi"ndeki maddede. Yüklemede aynı başlık uyarısı ya da sürüm yönetimi ayrı tasarım ister.
- Yerel vektörleme yavaş: bu bilgisayarda parça başına ~0,9 sn (FastReact, 1847 parça, 1655 sn ≈ 27,6 dk). Daha büyük belge setlerinde ilk yükleme saatler sürebilir; ölçek için ayrıca ölçülmedi.
- Markdown tablolarının her satırı ayrı parça olunca FastReact 1847 parçadan 3648 parçaya çıktı (967'si tablo satırı). Vektörleme süresi parça sayısıyla doğru orantılı olduğu için ilk yükleme ve yeniden işleme yaklaşık iki katına çıkar; ölçüm indeksi 3468 sn sürdü, ama bir kısmında uygulama da aynı anda vektörlüyordu, temiz süre ölçülmedi. Arama kalitesine etkisi tek koşuda olumlu görüldü (beklenen belge 1. sırada: 11/17 → 14/17); gerçek belgelerdeki tablolarda parça sayısı ve süre ayrıca izlenecek.
- Hazır bir belge yeniden işlenirken, işlem bitene kadar aramada görünmüyor; eski hali de kullanılamıyor. Pilot için kabul edildi. Eski sürümü işlem bitene kadar aramada tutmak ayrı bir tasarım ister (iki sürümün parçaları ve vektörleri bir süre birlikte durur).

## Yayına almadan önce

- Soru kaydının saklama süresi açık: her soru (kullanıcının yazdığı metin dahil) SQLite'ta süresiz kalıyor, silme ya da anonimleştirme yok. Yayına almadan önce saklama süresi ve kimin okuyabileceği kararlaştırılmalı; ses ve cevap metninin tamamı zaten kaydedilmiyor.
- Giriş kapalı: arayüz ağa açılırsa ağdaki herkes belge görebilir ve yükleyebilir. Şu an yalnız `127.0.0.1` adresine açık; tabletler için açmadan önce giriş ya da ağ kısıtı gerekir.
- Yüklenen Office dosyaları işçide LibreOffice ile açılıyor; işçinin internet erişimi kapatılabilir.
- Yerel kurulumda arayüzü nginx değil API sunuyor: nginx'teki güvenlik başlıkları (CSP, X-Frame-Options, nosniff, Referrer-Policy) ve `/api/ask`, `/api/speak`, `/api/transcribe` için hız sınırı yerelde yok. Ağa açmadan önce bunlar API'ye ya da önündeki bir vekil sunucuya eklenmeli.

## Kurulum

- LibreOffice dönüştürmesinin 180 sn sınırı işlemci doluyken aşılabiliyor: iki vektörleme işi aynı anda çalışırken taban ölçümünde `sql-ekran.docx` ve `sql-notlar.docx` PDF'e çevrilemedi (`TimeoutExpired`). İşlemci boşken aynı belgeler sorunsuz çevrildi. Uygulamada belge yüklemesi büyük bir yeniden işlemeyle çakışırsa Office belgesi "işlenemedi" olabilir; sınırın yükle ilişkisi ölçülmedi.
- Sunucu (Docker) kurulumundaki Docling model indirme komutu (`docling-tools models download`) önceki bilgisayarda takıldı ve hiç doğrulanmadı. Yerel kurulumda bu komut kullanılmıyor, modeller ilk belgede kendiliğinden iniyor. Sunucuya ilk kurulumda denenecek; takılırsa nedeni bulunacak.
- Docker paketi (compose, imajlar) SQLite ve tek süreç değişikliğinden sonra bu bilgisayarda denenemedi; yalnız CI'daki `services` işi açılışı sınıyor. Sunucuya kurulurken API ve işçinin aynı SQLite birimini paylaşması uçtan uca denenecek.
