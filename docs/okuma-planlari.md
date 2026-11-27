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
