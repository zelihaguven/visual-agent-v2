# Sesli test altın soru seti

Yığın: `http://127.0.0.1:8080`. Belgeler: `sql-kilavuz.pdf`, `dikim-tarama.pdf`, `dikim-excel.xlsx`, `dikim-pdf.pdf`.

"Beklenen cevap" sütununda değer yok, kaynağın yeri var. Değeri belgeyi açıp oradan kontrol edin. Excel satır numaraları dosyanın kendi satırlarıdır.

## Söyleyiş

| Kod | Nasıl söylenir | Hangi belgede |
| --- | --- | --- |
| PNT-1162 | pe ne te bin yüz altmış iki | dikim-pdf |
| PNT-1126 | pe ne te bin yüz yirmi altı | dikim-excel |
| GML-6473 | ge me le altı bin dört yüz yetmiş üç | dikim-tarama |

İki PNT kodu yalnız son iki rakamda ayrılır. Yazıya çevirme bunları karıştırırsa cevap başka modelden gelir; önce ekrandaki soruya bakın.

## Duyuru anahtarı

"Sesli modda dikkat" sütunundaki harfler, cevaptan sonra duyulması gereken sabit cümledir.

| Harf | Durum | Duyulması gereken |
| --- | --- | --- |
| A | Doğrulandı | Yalnız cevap. Ek duyuru **yok**. |
| B | Kısmen doğrulandı | Cevap, ardından: "Bu cevap görsel ya da taramadan okundu, kaynağı ekrandan kontrol edin." |
| C | Doğrulanamadı | Değer **okunmaz**. "Bazı değerler doğrulanamadı, ekrana bakın." |
| D | Bulunamadı | "Bu bilgi belgelerde bulunamadı. Bir model ya da konu söylerseniz yardımcı olabilirim." |
| E | Netleştirme | Soruda rakam yoksa sorunun kendisi okunur; rakam varsa "Netleştirmem gereken bir nokta var, ekrana bakın." |
| K | Komut | Komut okunmaz, "Komut ekranda gösteriliyor." duyulur. |

Okuma biçimi: ondalık "kırk virgül beş" gibi, kodun rakamları tek tek ("pe ne te bir bir altı iki"), beden harfi "me", "le", "se" olarak okunur.

## Sınırlar

- Bu dört belgede aynı modelin iki sürümü yok, gerçek bir değer çelişkisi kurulamıyor. 21-24 yalnız netleştirme sınar.
- Netleştirme için arayüzde rozet yok. Bu satırlarda rozet yerine "Rozet yok" yazıyor.
- Ölçü değerlerinin birimi belgelerde yazmıyor; yalnız `Tolerans (cm)` sütununda birim var. Cevapta geçen "santimetre" sorudan gelmiş olabilir.
- Belgeler neredeyse tamamen tablodur, düzyazı yok. "Normal" sorular tablo ve komutlardan gelir.

## Set

### Normal (1-10)

| # | Soru (sesli söylenecek hali) | Beklenen cevap | Beklenen rozet | Beklenen atıf | Neyi sınıyor | Sesli modda dikkat | Sonuç |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Pe ne te bin yüz altmış iki modelinde M beden iç paça kaç? (PNT-1162) | dikim-pdf s.2, Ölçü tablosu: `İç paça` satırı × `M` sütunu | Doğrulandı | dikim-pdf · s.2 | Metin katmanlı PDF'den tablo hücresi | Sayı: ondalık "virgül" ile. Kod: tek tek rakam. Duyuru: A | |
| 2 | Pe ne te bin yüz altmış iki modelinde L beden kalça kaç? (PNT-1162) | dikim-pdf s.2: `Kalça` satırı × `L` sütunu | Doğrulandı | dikim-pdf · s.2 | Son satır, son beden sütunu | Sayı: tam kısım iki basamaklı "elli" gibi okunmalı, rakam rakam değil. Duyuru: A | |
| 3 | Pe ne te bin yüz altmış iki modelinde dış paça toleransı kaç? (PNT-1162) | dikim-pdf s.2: `Dış paça` satırı × `Tolerans (cm)` sütunu | Doğrulandı | dikim-pdf · s.2 | Bedenden bağımsız sütun; netleştirme sormamalı | Sayı: "bir virgül sıfır" olmalı, "bir" ya da "on" değil. Duyuru: A | |
| 4 | Pe ne te bin yüz altmış iki modelinde S beden etiket kodu nedir? (PNT-1162) | dikim-pdf s.3, Etiket kodları: `S` satırı × `Etiket kodu` | Doğrulandı | dikim-pdf · s.3 | Kod değeri döndürme | Kod: "e te ke" + dört rakam tek tek. Son rakam kaçırılırsa yanlış bedendir. Duyuru: A | |
| 5 | Pe ne te bin yüz yirmi altı modelinde S beden bel kaç? (PNT-1126) | dikim-excel, `Ölçü tablosu` satır 6 × sütun B (`S`) | Doğrulandı | dikim-excel · Ölçü tablosu · satır 6 | Excel satır atfı | Kod: 1126'nın 1162 olarak yazılmadığını ekrandan kontrol edin. Duyuru: A | |
| 6 | Pe ne te bin yüz yirmi altı modelinde L beden dış paça kaç? (PNT-1126) | dikim-excel, `Ölçü tablosu` satır 5 × sütun D (`L`) | Doğrulandı | dikim-excel · Ölçü tablosu · satır 5 | Üç basamaklı değer | Sayı: "yüz yedi virgül sıfır" biçiminde, basamak düşmemeli. Duyuru: A | |
| 7 | Pe ne te bin yüz yirmi altı modelinde iç paça toleransı kaç? (PNT-1126) | dikim-excel, `Ölçü tablosu` satır 4 × sütun E (`Tolerans (cm)`) | Doğrulandı | dikim-excel · Ölçü tablosu · satır 4 | Tolerans; PDF modelinden farklı olmalı | Sayı: "sıfır virgül beş"; "sıfır" düşmemeli. Duyuru: A | |
| 8 | Pe ne te bin yüz yirmi altı modelinde M beden etiket kodu nedir? (PNT-1126) | dikim-excel, `Etiket kodları` satır 5 × sütun B | Doğrulandı | dikim-excel · Etiket kodları · satır 5 | İkinci Excel sayfası | Kod: tek tek rakam, PDF modelinin etiketiyle karışmamalı. Duyuru: A | |
| 9 | Kuzey Sorgu'da kolon adını nasıl değiştiririm? | sql-kilavuz s.2: `Kolon adını değiştirme` başlığı altındaki komut | Doğrulandı | sql-kilavuz · s.2 | Komutun değişmeden, kaynaktan gösterilmesi | Komut sesle okunmamalı, ekrandaki blok kaynakla birebir olmalı. Duyuru: K | |
| 10 | Depo sayım tablosuna yeni kolon nasıl eklenir? | sql-kilavuz s.3: `Yeni kolon ekleme` başlığı altındaki komut | Doğrulandı | sql-kilavuz · s.3 | Komut seçimi; s.2 komutuyla karışmamalı | Tablo ve kolon adları ses metninde okunmamalı. Duyuru: K | |

### OCR kaynaklı (11-16)

Bu satırların hepsi taranmış `dikim-tarama.pdf` belgesindendir. Sayfa görüntüsünde kontrol edin.

| # | Soru (sesli söylenecek hali) | Beklenen cevap | Beklenen rozet | Beklenen atıf | Neyi sınıyor | Sesli modda dikkat | Sonuç |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | Ge me le altı bin dört yüz yetmiş üç modelinde M beden iç paça kaç? (GML-6473) | dikim-tarama s.2: `İç paça` satırı × `M` sütunu | Kısmen doğrulandı | dikim-tarama · s.2 | Yeni davranış: OCR cevabı "Doğrulandı" olmamalı | Kod: "ge me le" + tek tek rakam. Duyuru: B; "doğrulanamadı" denirse hatadır | |
| 12 | Ge me le altı bin dört yüz yetmiş üç modelinde S beden kalça kaç? (GML-6473) | dikim-tarama s.2: `Kalça` satırı × `S` sütunu | Kısmen doğrulandı | dikim-tarama · s.2 | OCR tablo hücresi | Sayı: değer ".0" ile bitiyor, "virgül sıfır" okunmalı. Duyuru: B | |
| 13 | Ge me le altı bin dört yüz yetmiş üç modelinde L beden bel kaç? (GML-6473) | dikim-tarama s.2: `Bel` satırı × `L` sütunu | Kısmen doğrulandı | dikim-tarama · s.2 | `L` başlığının OCR'da gürültülü okunduğu sütun | Doğru sütundan geldiğini sayfa görüntüsünden kontrol edin. Duyuru: B | |
| 14 | Ge me le altı bin dört yüz yetmiş üç modelinde M beden dış paça kaç? (GML-6473) | dikim-tarama s.2: `Dış paça` satırı × `M` sütunu | Kısmen doğrulandı | dikim-tarama · s.2 | Belirsiz işaretli tolerans aynı satırdaki sağlam değere sıçramamalı | Sayı: üç basamaklı ondalık. Değer gizlenirse satıra "bilinen risk" yazın. Duyuru: B | |
| 15 | Ge me le altı bin dört yüz yetmiş üç modelinde M beden etiket kodu nedir? (GML-6473) | dikim-tarama s.3: `M` satırı × `Etiket kodu` | Kısmen doğrulandı | dikim-tarama · s.3 | Taramadan kod okuma | Kod: tek tek rakam, son rakam bedeni ayırır. Duyuru: B | |
| 16 | Ge me le altı bin dört yüz yetmiş üç modelinde dış paça toleransı kaç? (GML-6473) | dikim-tarama s.2: `Dış paça` satırı × `Tolerans (cm)`. OCR bu hücreyi hatalı okudu, belirsiz işaretli | Doğrulanamadı | dikim-tarama · s.2 | Belirsiz değer gösterilmemeli, okunmamalı | Sayı hiç duyulmamalı; duyulursa ciddi hatadır. Duyuru: C | |

### Takip zincirleri (17-20)

Her satır iki sorudur. Arada "Yeni konu" demeyin; ikinci soruyu birincinin hemen ardından sorun.

| # | Soru (sesli söylenecek hali) | Beklenen cevap | Beklenen rozet | Beklenen atıf | Neyi sınıyor | Sesli modda dikkat | Sonuç |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | 1) Pe ne te bin yüz altmış iki modelinde M beden bel kaç? (PNT-1162) 2) Peki kalçası? | 1) dikim-pdf s.2: `Bel` × `M` 2) dikim-pdf s.2: `Kalça` × `M` | 1) Doğrulandı 2) Doğrulandı | Her ikisi dikim-pdf · s.2 | Alan değişince model ve beden korunmalı | "Anlaşılan soru" satırına bakın. İkinci cevap da aynı bedenden. Duyuru: A, A | |
| 18 | 1) Pe ne te bin yüz yirmi altı modelinde L beden iç paça kaç? (PNT-1126) 2) Peki dış paça? | 1) dikim-excel `Ölçü tablosu` satır 4 × `L` 2) satır 5 × `L` | 1) Doğrulandı 2) Doğrulandı | dikim-excel · Ölçü tablosu · satır 4, sonra satır 5 | Excel'de takip | "paça" sözcüğü iki soruda da geçiyor, satır atfı değişmeli. Duyuru: A, A | |
| 19 | 1) Ge me le altı bin dört yüz yetmiş üç modelinde S beden bel kaç? (GML-6473) 2) Peki L beden? | 1) dikim-tarama s.2: `Bel` × `S` 2) dikim-tarama s.2: `Bel` × `L` | 1) Kısmen doğrulandı 2) Kısmen doğrulandı | Her ikisi dikim-tarama · s.2 | Yeni düzeltme: kısmi cevap bağlamı güncellemeli | Bağlam çubuğunda `dikim-tarama` görünmeli. Duyuru: B, B | |
| 20 | 1) Pe ne te bin yüz altmış iki modelinde M beden bel kaç? (PNT-1162) 2) Peki pe ne te bin yüz yirmi altının? (PNT-1126) | 1) dikim-pdf s.2: `Bel` × `M` 2) dikim-excel `Ölçü tablosu` satır 6 × `M` | 1) Doğrulandı 2) Doğrulandı | dikim-pdf · s.2, sonra dikim-excel · Ölçü tablosu · satır 6 | Model değişince beden korunmalı, belge kapsamı kalkmalı | Kod ikinci turda yanlış yazılırsa kapsam kalkmaz. Duyuru: A, A | |

### Netleştirme (21-24)

| # | Soru (sesli söylenecek hali) | Beklenen cevap | Beklenen rozet | Beklenen atıf | Neyi sınıyor | Sesli modda dikkat | Sonuç |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | M beden bel kaç? | Model sorulmalı. Üç belgede farklı: dikim-pdf s.2, dikim-excel satır 6, dikim-tarama s.2 (`Bel` × `M`) | Rozet yok | Seçenek düğmeleri: belge adları | Model belirsizliği, değer yazılmamalı | Hiçbir değer duyulmamalı. Duyuru: E | |
| 22 | Pe ne te bin yüz altmış iki bel ölçüsü kaç? (PNT-1162) | Beden sorulmalı. Tek satırda üç beden: dikim-pdf s.2 `Bel` satırı | Rozet yok | Yok; tek belge olduğu için seçenek düğmesi çıkmaz | Tek kaynak içinde beden belirsizliği | Üç değer sıralanırsa hatadır. Duyuru: E | |
| 23 | Etiket kodu nedir? | Model ve beden sorulmalı. dikim-pdf s.3, dikim-excel `Etiket kodları`, dikim-tarama s.3 | Rozet yok | Seçenek düğmeleri: belge adları | Hiç niteleyici olmayan soru | Kod duyulmamalı. Duyuru: E | |
| 24 | Dış paça toleransı kaç? | Model sorulmalı. Tolerans belgeler arasında farklı: dikim-pdf s.2, dikim-excel satır 5, dikim-tarama s.2 (`Dış paça` × `Tolerans (cm)`) | Rozet yok | Seçenek düğmeleri: belge adları | Değerler farklıyken tahmin etmemek | Tek değer söylenirse hatadır. Duyuru: E | |

### Kapsam dışı (25-27)

| # | Soru (sesli söylenecek hali) | Beklenen cevap | Beklenen rozet | Beklenen atıf | Neyi sınıyor | Sesli modda dikkat | Sonuç |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 25 | Pe ne te bin yüz altmış iki modelinde kol boyu kaç? (PNT-1162) | Belgede yok. dikim-pdf s.2'deki ölçü noktaları: `İç paça`, `Dış paça`, `Bel`, `Kalça` | Bulunamadı | Yok | Model var, alan yok; başka satır uydurulmamalı | Sayı duyulmamalı. Duyuru: D | |
| 26 | Yıllık izin kaç gün? | Dört belgenin hiçbirinde izin konusu yok | Bulunamadı | Yok | Konu tamamen dışarıda | Duyuru: D | |
| 27 | Xe ye ze dokuz bin dokuz yüz doksan dokuz modelinin beli kaç? (XYZ-9999) | Bu kod dört belgede yok | Bulunamadı | Yok; altta "XYZ-9999 belgelerde geçmiyor." | Kod yoksa arama ve model çalışmamalı, anında dönmeli | Yazıya çevirme kodu bozarsa farklı yola gider, ekrandaki soruyu kontrol edin. Duyuru: D | |

### Sesli moda özel (28-30)

Soruyu sesle sorun. Ekranda yazıya çevrilen metni de işaretleyin.

| # | Soru (sesli söylenecek hali) | Beklenen cevap | Beklenen rozet | Beklenen atıf | Neyi sınıyor | Sesli modda dikkat | Sonuç |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | Pe ne te bin yüz altmış iki modelinde M beden bel kırk virgül beş santimetre mi? (PNT-1162) | dikim-pdf s.2: `Bel` × `M`; sorudaki değerle karşılaştırın | Doğrulandı | dikim-pdf · s.2 | Kod, ondalık ve birim aynı cümlede; değer onayı | Yazıda ondalık "40,5" olmalı, "405" ya da "40 5" değil. Duyuru: A | |
| 29 | Pe ne te bin yüz yirmi altı modelinde M beden bel kırk virgül beş santimetre mi? (PNT-1126) | dikim-excel `Ölçü tablosu` satır 6 × `M`; sorudaki değer bu hücreyle **uyuşmuyor**, belge değeri söylenmeli | Doğrulandı | dikim-excel · Ölçü tablosu · satır 6 | Yakın kod tuzağı: aynı sayı diğer modelde doğru | Kod 1162 duyulursa model yanlış onaylar. Kullanıcının değeri tekrar edilmemeli. Duyuru: A | |
| 30 | Ge me le altı bin dört yüz yetmiş üç modelinde L beden iç paça yetmiş sekiz virgül beş santimetre mi? (GML-6473) | dikim-tarama s.2: `İç paça` × `L`; sorudaki değerle karşılaştırın | Kısmen doğrulandı | dikim-tarama · s.2 | OCR, kod, ondalık ve birim birlikte | Yazıda kod `GML-6473` olmalı. Duyuru: B | |
