# Okuma planları: tasarım, adaylar, maliyet

Doğru cevaplar ve ölçüt: `evals/okuma_planlari_dogru_cevaplar.md` (ölçümden önce yazıldı).
Onay (2026-11-27, ürün sahibi): taban ve C yerel; A ve B bulutta, ana VLM qwen3-vl-30b, üst sınır 0,20 $;
B'de tüm sayfa görüntüsünün buluta gitmesi yalnız bu test için kabul, canlı kullanım kararı sonuçlardan sonra.
Ölçümde bulunan üç hata bu turda düzeltilmez; her planın onları düzeltip düzeltmediği raporda ayrıca yazılır.

Ölçüm indeks dışında, okuma çıktısı üzerinde; betikler scratchpad'de; repo ve canlı veri değişmez.
Taban = bugünkü kodun bu sayfalar için ürettiği parçalar (veritabanında; QM ve Bold bugün bu kodla işlendi,
föyler aynı kural sürümüyle Mac'te). Taban için yeniden okuma gerekmez.

## Plan A: Paddle aynen + boş görsel/grafik bloklarına bulut VLM
1. Seçilen sayfaların görüntüsünde PP-DocLayoutV3 (bugünkü düzen modeli) blokları bulunur.
2. Etiketi image/chart/figure olan ve bugünkü çıktıda karşılığı boş kalan bloklar kırpılır (bugünkü kırpma
   ölçeğiyle, `page_reader._image_scale` mantığı).
3. Kırpıntı, ZDR'li VLM'e tek istemle gider: "Görseldeki bütün yazıları, sayıları ve etiketleri satır satır
   aynen yaz; tablo varsa satır/sütunla; yorum ekleme" (JSON).
4. İkinci okuma, karşılaştırma için üç yol:
   (a) aynı kırpıntı PaddleOCR-VL'e yalnız metin tanıma ("OCR:") olarak, yerelde;
   (b) Tesseract tur+eng psm 11, yerelde (bugünkü kontrol);
   (c) ikinci, farklı aileden ZDR'li VLM.
   Değer, VLM ile ikinci okuma bugünkü sayma kuralıyla (`count_mismatches`) uyuşursa gösterilir.
5. VLM öğeleri bölge kutusuyla sayfaya yerleşir (`page_elements(..., region=box)` gibi), from_ocr=True.
Buluta yalnız kırpıntı gider.

## Plan B: OCR kaldırılır, sayfayı bulut VLM okur
1. Her seçilen sayfa (metinli dahil) bugünkü `_native_scale` ile görüntüye çevrilir.
2. VLM-1'e istem: sayfadaki bütün metin, başlıklar, tablolar (satır/sütun), şekil etiketleri; Markdown/JSON.
3. İkinci okuma: (i) farklı aileden VLM-2 aynı istemle, ya da (ii) PaddleOCR-VL (bugünkü okuyucu).
4. Değerler sayma kuralıyla karşılaştırılır; uyuşmayan gizli.
5. Konum kutusu yok (VLM kutu vermiyor): kaynak sayfa düzeyinde gösterilir. Bu bir yetenek kaybı, raporda ayrı.
Buluta bütün sayfa görüntüsü gider.

## Plan C: her sayfa görüntü olarak bugünkü okuyucudan
1. Metin katmanı olsun olmasın sayfa `_native_scale` ile çizilir, `read_scanned_pages` (PaddleOCR-VL +
   Tesseract) ile okunur; kod değişmez, yalnız sayfa sınıflandırması atlanır (betikte).
2. Fark yalnız bugün metin katmanından okunan sayfalarda olur (QM'nin 8 sayfası, Bold s.12); diğerleri tabanla
   aynı yoldan geçiyor, yeniden koşulmaz.
3. Yerel, bulut yok. Bir sayfa 5 dakikayı geçerse durdurulur.

## VLM adayları (OpenRouter, şu an ZDR uç noktası olan, görüntü alan)
| Model | ZDR sağlayıcı | Fiyat (girdi / çıktı, $/M token) | Neden |
|---|---|---|---|
| qwen/qwen3-vl-30b-a3b-instruct | deepinfra (tek) | 0.15 / 0.60 | 0005'te 627/627 hücre doğru; tek sağlayıcı: erişim riski |
| qwen/qwen3-vl-235b-a22b-instruct | deepinfra, parasail, venice | 0.21 / 1.90 | aynı ailenin büyüğü, üç ZDR sağlayıcı; ölçülmedi |
| google/gemma-4-26b-a4b-it | akashml, cloudflare, coreweave… | 0.09 / 0.30 | bugünkü cevap modeli, farklı aile (ikinci okuyucu için bağımsız); okuma doğruluğu ölçülmedi |
Gemini Flash Lite (0005'te 625/627) şu an ZDR listesinde yok: aday değil.
Öneri: VLM-1 qwen3-vl-30b (ölçülmüş), ikinci okuyucu (A-c, B-i) gemma-4-26b (farklı aile).

## Çağrı, maliyet, süre tahmini (24 sayfa: QM 8 + Bold 8 + föy 8)
Varsayım: sayfa görüntüsü ~1.500–2.500 girdi token, sayfa çıktısı ~800–1.500 token; kırpıntı ~400–900 girdi,
~100–300 çıktı. Fiyat tablodaki gibi. Gerçek değer ölçümde yazılır; önbellek: istem + görüntü sha256.

| Plan | Çağrı | Tahmini maliyet | Tahmini süre |
|---|---|---|---|
| Taban | 0 (veritabanından) | 0 $ | dakikalar |
| A (a veya b ikinci okuma) | ~60–120 kırpıntı × 1 VLM | ~0,01–0,03 $ | bulut birkaç dk; (a) yerelde kırpıntı başına 20–60 sn |
| A (c) | ~60–120 × 2 VLM | ~0,02–0,05 $ | birkaç dk |
| B (iki VLM) | 24 sayfa × 2 | ~0,03–0,10 $ | birkaç dk |
| C | 0 bulut; ~9 sayfa yerelde | 0 $ | sayfa başına 1–5 dk → ~10–45 dk |
Toplam bulut üst sınırı ~0,20 $ (önbellekli). Aşarsa durulur ve sorulur.

## Sonuç (Windows, 2026-11-27; 150 değer, bir koşu)
Puanlama yarı otomatik, ~60 değer elle (kararlar ölçüm klasöründeki `elle.json`'da; klasör repoda değil).
Bulut: 62 çağrı (A 38, B 24), 0,0476 $, hepsi DeepInfra ZDR. Plan C koşulamadı (aşağıda).

| Plan | Doğru gösterilen | Yanlış gösterilen | Gizlenen doğru | Gizlenen yanlış | Okunamayan |
|---|---|---|---|---|---|
| Taban | 81 | 3 | 27 | 8 | 31 |
| A-b (VLM + Tesseract) | 94 | 3 | 38 | 8 | 7 |
| A-a (VLM + PaddleOCR-VL metin tanıma) | 89 | 3 | 43 | 8 | 7 |
| B (VLM + Paddle; önceden kayıtlı kural) | 48 | 0 | 79 | 0 | 23 |
| B-yedek (metinli sayfada ikinci okuma = metin katmanı; kayıtlı değil, bilgi) | 84 | 0 | 43 | 0 | 23 |

Belge bazında doğru gösterilen: QM taban 45 / A-b 46 / B 5; Bold 14 / 17 (A-a 20) / 14; föy 22 / 31 / 29.
Şekil ve görsel değerleri (114): gösterilen taban %46, A-b %58, A-a %54, B %39; okunan taban %70, A %91, B %90.

Ölçüt 1 (yanlış gösterilen tabandan fazla değil): hepsi geçti. Taban ve A'daki 3 yanlışın üçü de bilinen QM s.16 hatası.
Ölçüt 2 (metinli sayfada bozulma yok): A geçti (0); B kaldı (24; yedek kuralla 9: QM-16 tabloları çıktı döngüsünde kayboldu).
Plan C: QM s.7 iki denemede de (model önceden yüklüyken dahil) 300 saniyeyi aştı; ölçüt gereği durduruldu, puanlanmadı.
C Mac'te koşulacak (aynı sayfalar, aynı doğru cevaplar, aynı ölçüt).

Bilinen üç hata:
- QM s.16 (PTH satırları "OQL/SQL" altında): A dokunmuyor, B düzeltmiyor (tablo çıktısı döngüde kayboldu), C ölçülmedi.
- Bold s.21 (parça yok): A ve B okuyor (4/4); 1 değer gösterilen, 3 gizli.
- Föy s.14 (dikiş talimatları yok): A-b 9/9 doğru gösterilen (Qwen ve Tesseract uyuştu); A-a okuyor ama ikinci okuma
  300 sn'yi aştığı için gizli; B okuyor ama ikinci okuma (bugünkü boş parçalar) olmadığından gizli.

Gözlenen VLM hataları (hepsi gizli kaldı): Qwen "FW26" → "P128" (A), "64mm" → "44mm" (B); B'de 24 sayfanın 4'ünde çıktı
döngüye girip token sınırına takıldı, 1 sayfada JSON bozuk. PaddleOCR-VL metin tanıma (A-a) kırpıntı başına 14–282 sn.

Yöntem notu: A'da 10 öğeye kadar olan kırpıntı tek etiket–değer birimi, B'de ardışık 3 öğe bir birim sayıldı; sonucu etkileyebilir.
Ölçülmeyenler: ikinci VLM (Gemma) ile A-c ve B-i; Plan C.

## Plan A-q (ürün sahibi tasarımı; Windows, 2026-11-27, bir koşu)
Paddle ana okuyucu (bugünkü okumalar); Paddle bölgelerinin kontrolcüsü Tesseract yerine Qwen3-VL-30B (kırpıntı);
Paddle'ın boş bıraktığı şekil blokları Qwen, ikinci okuyucu A-q1 Gemma 4 26B, A-q2 Tesseract. Buluta yalnız kırpıntı.
Aynı 150 değer, ölçüt ve eşleştirme kuralları; yeni elle karar 8 (7'si tabandan devralınan gizli-yanlış, 1 değişen: F-28-1).

| | Taban | A-b | A-q1 | A-q2 |
|---|---|---|---|---|
| Doğru gösterilen | 81 | 94 | 115 | 106 |
| Yanlış gösterilen | 3 | 3 | 3 | 3 |
| Gizlenen doğru | 27 | 38 | 17 | 26 |
| Gizlenen yanlış | 8 | 8 | 8 | 8 |
| Okunamayan | 31 | 7 | 7 | 7 |
| Metinli sayfada bozulan | – | 0 | 0 | 0 |
| Şekil değerlerinde gösterilen (114) | %46 | %58 | %76 | %68 |
| Föy kesirli değerler (18), doğru gösterilen | 0 | 7 | 15 | 15 |

Yanlış gösterilen 3 değerin üçü de bilinen QM s.16 etiket hatası (metinli sayfa, bu turda kontrol dışı). 8 yanlış okuma
dört planda da gizli kaldı; Qwen ile Paddle ya da Qwen ile Gemma'nın birlikte yanlış okuyup gösterdiği değer yok.
Okuyucu bölgelerinde doğrulanan değer parçası: Tesseract %59 (784/1.321), Qwen %87 (1.143/1.321).
A-q2'de Bold s.6'da iki değer (B-6-1, B-6-3) tabanda gösterilirken gizlendi (metinli sayfa değil; ölçüt 2'yi bozmaz).

Maliyet ve süre: tahmin ~0,021 $, gerçek 0,0136 $ (Qwen 43 çağrı DeepInfra, Gemma 38 çağrı AkashML; ZDR). İki turun toplamı
0,0612 $. Föy tablo sayfası başına ek ~37–42 sn ve ~0,0018 $ (bütün tablo tek kırpıntı); diğer sayfalar 3–44 sn.

Sınırlar: (1) QM s.15 ve s.29'daki gömülü görsel tablolarını bu ölçümde hâlâ Tesseract kontrol ediyor (tasarımda
"Tesseract tamamen çıkar" tam uygulanmadı). (2) Kontrol birimi bugünkü blok; föy tablosunda bütün tablo tek bölge.
(3) İki VLM (Paddle ve Qwen) aynı hatayı yaparsa yakalanmaz; bu 150 değerde görülmedi, örneklem küçük. (4) Qwen yalnız
tek ZDR sağlayıcıda (DeepInfra). (5) Puanlamanın bir kısmı elle.
