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

## İkinci set: A-q1 (Windows, 2026-11-27, bir koşu)
Doğru cevaplar ve ölçüt: `evals/okuma_planlari_dogru_cevaplar_2.md` (ölçümden önce yazıldı; birinci setin sayfaları
kullanılmadı). 163 değer: QM 8, 21, 22, 27, 28, 39, 41, 43; Bold 4, 9, 11, 14, 17, 22, 23, 25; föy 6026412 1, 5, 6,
7, 8, 10, 13, 15. Aynı eşleştirme kuralları; elle karar 86 (`elle_set2.json`, ölçüm klasöründe; repoda değil).

| | Taban | A-q1 |
|---|---|---|
| Doğru gösterilen | 95 | 119 |
| Yanlış gösterilen | 0 | 0 |
| Gizlenen doğru | 17 | 14 |
| Gizlenen yanlış | 5 | 7 |
| Okunamayan | 46 | 23 |
| Metinli sayfada bozulan | – | 0 |
| Şekil değerlerinde gösterilen (114) | %46 (52) | %66 (75) |
| Föy kesirli değerler (23), doğru gösterilen | 2 | 11 |

Belge bazında doğru gösterilen: QM 56 / 56, Bold 20 / 27, föy 19 / 36. Tabandan farklı 31 değer; biri kötüleşti:
F2-1-4 doğru gösterilen → gizlenen doğru. F2-15-2 (−2) iki planda da gösterilmedi (gizli).
Ölçüt 1 (yanlış gösterilen tabandan fazla değil): geçti (0 / 0). Ölçüt 2 (metinli QM sayfalarında bozulma yok): geçti.
Okuyucu sayfalarında doğrulanan değer parçası: Tesseract %51 (655/1.295), Qwen %74 (962/1.295).

Gözlenen sorunlar:
- DeepInfra 429 (istek sınırı): Qwen bölge okumasında bekleyip yeniden denendi (15, 30, 60 sn); okuma tamamlandı.
- Qwen Bold s.25'te bir şekil kırpıntısında döngüye girip token sınırına takıldı (`length`); değerleri gizli kaldı
  (B2-25-2 "55mm" ve B2-25-3 gizlenen yanlış).
- Bold s.14'te düzen modeli hiç blok bulamadı; sayfa okunmadı (sonra kural: blok yoksa sayfa tek şekil bloğu, 0035).
- Paddle föy POM tablolarında kesirleri yanlış okudu ("-3/8" → "-3 3/8", "5/8" → "5 1/8"); hepsi gizli kaldı (taban
  ve A-q1'de 5 gizlenen yanlış).
- Puanlamada 86 elle karar.

Maliyet: bu set 113 çağrı (Qwen 83 DeepInfra, Gemma 30 AkashML; ZDR), 0,0160 $. Bütün okuma ölçümleri: birinci set
0,0476 $, A-q 0,0136 $, ikinci set 0,0160 $; toplam 0,0772 $. Sayfa başına ek süre 1–74 sn (föy tablo sayfaları
30–52 sn, Bold s.25 74 sn).

## Mac kontrol listesi (A-q1'i işlenmiş veride doğrulama)
Plan C yok (0034'te elendi). Komutlar repo kökünde; uygulama `http://127.0.0.1:8080` (`WEB_PORT`).

**Hazırlık**
1. `git fetch && git switch okuma-planlari && git pull`; `uv sync --frozen --extra retrieval --extra ingest`.
2. `.env`: `VA_OPENROUTER_API_KEY` dolu (boşluk değil); `VA_PAGE_READER=mlx-vlm-server@http://localhost:8111/` ve
   okuyucu sunucusu ayrı pencerede açık (README, "Taranmış sayfalar"). Anahtar yoksa okuma eski yoldan (Tesseract) yapılır
   ama belge yine 27 damgası alır (0035, bilinen sınırlar); koşudan önce anahtarı denetle.
3. Uygulama kapalıyken `cp -R data data-yedek-$(date +%Y%m%d)` (silinmez).
4. Belge sayısı: Mac'te `sqlite3 data/visual_agent.db 'select count(*) from documents'`. Windows'ta 396 belge; 26 Kasım'dan
   sonra Windows'a yüklenen iki belge Mac'te yoksa yeniden işlemeden önce yüklenir: "Quality Manual - v8.3.pdf" ve
   "Bold 3 Stripes Global Quality Standard.pdf" (2026-11-27).
5. Denetimler geçmeli: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run pytest`
   (Mac'te LF olduğu için 3 donmuş hash testi de geçer).
6. Ön kontrol: tek bir ZDR okuma çağrısı (küçük görüntü, Qwen, boş geçici önbellek; 1 çağrı). Cevap gelirse "tamam"
   yazar; anahtar yoksa, ZDR sağlayıcısı yoksa ya da çağrı başarısızsa çıkış kodu 1. **Başarısızsa koşu başlamaz:**
   anahtarsız ya da bulutsuz işlenen belge sessizce 27 damgası alır (0035, bilinen sınırlar).
   `uv run --no-sync python -c "import dataclasses, sys, tempfile; from pathlib import Path; from PIL import Image, ImageDraw; from apps.worker.run import cloud_config; from visual_agent.ingest.page_reader import CHECK_MAX_TOKENS, CHECK_PROMPT, cloud_reader; from visual_agent.settings import Settings; c = cloud_config(Settings()); c is not None or sys.exit('anahtar yok'); c = dataclasses.replace(c, cache=Path(tempfile.mkdtemp())); im = Image.new('RGB', (160, 40), 'white'); ImageDraw.Draw(im).text((10, 12), 'TEST 42', fill='black'); t = cloud_reader(c, c.reader_model, CHECK_PROMPT, CHECK_MAX_TOKENS)(im); print('tamam:', t.strip()) if t.strip() else sys.exit('bos cevap')"`

**Kapsam** (Windows verisine göre; Mac'te yüklemeden sonra yeniden sayılır): 31 belge "Eski kural" olur: 25 PDF (337
sayfa), 4 Office, 1 görsel, 1 `.sql` (SQL kural sürümü 4). Okuyucu 20 belgede 276 taranmış sayfa ve 45 gömülü görsel
sayfası okur. Markdown (362) ve Excel değişmez.

**Koşu** (uzun koşuyu ürün sahibi başlatır). İşçi API sürecinin içindedir; ayrı süreç yok.
- Başlatma: `caffeinate -i uv run --no-sync python -m apps.local`
- Yeniden işleme (tek komut; `outdated` alanı `GET /api/documents` cevabında, uç nokta
  `POST /api/documents/{doc_id}/reprocess`; zaten sıradaki belge 409 döner):
  `curl -s http://127.0.0.1:8080/api/documents | python3 -c "import json,sys;[print(d['doc_id']) for d in json.load(sys.stdin) if d.get('outdated')]" | while read id; do curl -s -X POST "http://127.0.0.1:8080/api/documents/$id/reprocess" >/dev/null; done`
- İlerleme (kalan "Eski kural" ve durumlara göre belge sayısı):
  `curl -s http://127.0.0.1:8080/api/documents | python3 -c "import json,sys,collections;d=json.load(sys.stdin);print('eski kural:', sum(x['outdated'] for x in d), dict(collections.Counter(x['status'] for x in d)))"`
- Tahmini süre 3–4,5 saat. Tahmini bulut maliyeti 0,5–0,8 $; **sınır 1 $, aşarsa dur** (uygulamayı Ctrl+C ile kapat;
  yarım kalan iş açılışta kendiliğinden yeniden başlar). Okuma çağrılarının maliyeti uygulama günlüğüne yazılmaz:
  OpenRouter panosunda (Activity) anahtarın harcaması izlenir. Yaklaşık çağrı sayısı:
  `ls data/okuma-onbellegi | wc -l` (önbelleğe yazılan her cevap bir ödenmiş çağrı).

**Kontroller**
- "Eski kural" 0 (ilerleme komutu).
- Devresi açılan belge 0:
  `sqlite3 data/visual_agent.db "SELECT d.doc_id, d.filename, w.value FROM documents d, json_each(d.report, '\$.warnings') w WHERE w.value LIKE '%bulut alınamadı%'"`.
  0 değilse yalnız bu belgeler yeniden işlenir (`POST /api/documents/{doc_id}/reprocess`).
- Bulutça reddedilen bloklar (ayrı sorgu, aynı biçim, `LIKE '%bulutça reddedildi%'`): sayı raporlanır; 0 değilse
  birleştirmeden önce ürün sahibine getirilir, yeni çözüm (görüntü küçültme vb.) yazılmaz.
- `status` `failed` ya da `waiting_reader` olan belge 0 (ilerleme komutu).
- Testler geçiyor.

**Yeniden puanlama** (313 değer: set 1 150, set 2 163; işlenmiş veriden, yeni bulut çağrısı yok). Geçme şartı:
doğrulanmış yanlış değer 0 (QM s.16 düzeldiği için set 1'de de 0 beklenir). Değer satır etiketiyle birlikte
denetlenir: değer doğru ama yanlış satıra (yanlış etikete) bağlıysa "yanlış gösterilen" sayılır. Prototiple farklar değer değer yazılır;
elle karar sayısı ayrı. **Bir tane bile yanlış değer gösterilirse dur, birleştirme.** Yöntem bu belgedeki tasarım ve
sonuç bölümlerinde (sınıflar, eşleştirme, ölçütler); prototip betikleri repoda değil, Mac oturumu yöntemi izleyerek
yeniden kurar.

**Bold beklentileri**: s.21'de B-21-3 gösterilmeli; B-21-1/2/4 gizli kalabilir. s.14: okunan ve gösterilen değerler
raporlanır, beklenti yok.

Windows duman testi (2026-11-27, dal kodu, yalnız Bold s.14 ve s.21 tek sayfalık PDF olarak, veritabanı ve indeks
dışında; yerel PaddleOCR-VL; 7 bulut çağrısı, hepsi 200, uyarı yok, < 0,01 $; s.14 208 sn, s.21 121 sn):
- s.21: eşiksiz tam sayfa şekil bloğu Qwen'le okundu, Gemma'yla denetlendi. Dört değerin metni parçalarda var
  (B-21-1 "18 mm/16 mm single stripe width … bubbling/puckering", B-21-2 "tapes or elastics … upfront alignment with
  CCDA", B-21-3 "color migration", B-21-4 "best fit insert panel width to avoid 4 stripes optic"); belirsiz işaret
  yalnız "3S" sözcüğünde. **Ama Qwen'in tablo okumasında RISK MITIGATION sütunu bir satır kaydı:** ilk satırın iki
  azaltma maddesi ayrı satır sayıldı, sonraki satırlar bir öncekinin azaltmasını taşıyor (ör. "Color Block … color
  migration | RISK MITIGATION: Over seam 3 stripes …"). Sayma denetimi satır bağını görmüyor (0035, bilinen sınır).
  Değerin kendi etiketi hücre metninde ("Trims selection: …") olduğu için 313 değerin puanında etkisi elle karar; ama
  "Color Block riski nasıl azaltılır?" gibi bir soru yanlış satırdan cevaplanabilir.
- s.14: tam sayfa yolu tetiklenmedi; Windows'taki yerel düzen modeli sayfada blok buldu (prototipte bulmamıştı).
  7 değerden hiçbiri okunmadı; çıkan iki parça bozuk ("35 APPEARANCE STANDARD …", "FL to follow …"), bozuk kodlar
  ("35", "FL") gizli. Tam sayfa yolu uçtan uca sınanmadı.

Mac'te ek kontrol: s.21 tablosunda satır bağı (her RISK IDENTIFICATION kendi azaltmasıyla mı?). Kayma görülürse
birleştirmeden önce ürün sahibine getirilir; düzeltme yazılmaz. s.14'te düzen modeli blok bulup bulmadığı ve tam
sayfa yolunun tetiklenip tetiklenmediği yazılır.

**Taban setleri ve FastReact** (1. sıra): parçalar değiştiği için cevap önbelleği tutmaz; önce çağrı sayısı ve maliyet
tahmini, sonra koşu.

**Elle sorular** (arayüzde, her biri bir kez):
- "OQL/SQL %90-94.99 puanı kaç?" (4 göstermemeli; o satır PTH tablosunun).
- "Poly bag (BG-CV0007) rengi ne?"
- "6013448 LG bel ölçüsü ne?"
- B-21-3'ü soran bir soru (ör. "Bold 3 Stripes'ta color block riski nedir?" → color migration).

**Bölüm yolu** değişen parçalardan üç örnek uygulamada kaynak olarak doğru görünmeli: 6013448 "POMs", QM s.16
"4.3.2 QA Scorecard", `.sql` belgesinden bir bölüm.

**Sonra**: kontroller tutunca PR açılır ve birleştirilir (CLAUDE.md birleştirme kuralı). İşlenmiş veri Windows'a
`va-veri-<tarih>.zip` olarak, sha256 ile aktarılır (açık notlar, "Windows'a veri gönderme"); Windows'ta açılır,
"Eski kural" 0 ve belge sayısı denetlenir.
