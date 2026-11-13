# Karar kaydı

Bugüne kadar alınmış önemli kararlar: ne, ne zaman, neden, hangi durumda yeniden düşünülür.
Kararların tek kaydı bu dosya. "0001"–"0004" diye anılan karar belgelerinin tam metni en sonda:
[Karar belgeleri 0001–0004](#karar-belgeleri-00010004).

**Kural:** Burada "çıkarıldı", "eklenmedi" ya da "reddedildi" yazan bir şeyi yeniden önermek
için yeni bir kanıt gerekir: yeni ölçüm, yeni belge türü ya da değişen gereksinim.
"Eklemeye değer olabilir" yeterli değil.

**Kaynaklar ve okuma notları**

- `#abc1234`: bu repodaki commit. `PR #n`: bu repodaki birleşmiş PR.
- **Eski pilot:** `visual_agent` reposu (bu bilgisayarda `Desktop/visual_agent`). Yollar o
  reponun içinden; ölçüm dosyaları `Pilot/eval/bench/` altında. Eski pilot kodu bu repoya
  taşınmadı. Oradaki ölçümler başka bir hatta, başka bir belge setiyle alındı; burada
  yalnız kararın gerekçesi olarak geçerli, bugünkü hattın sonucu değil.
- Eski pilotun 36 soruluk arama ölçümlerinde 5–8 puanın altındaki farklar gürültüdür
  (`Pilot/eval/bench/README.md`). 160 soruluk ölçümler onaylanmamış bir setten ve aşırı
  uyum uyarısı taşır (`b4/ozet_dondurulan_aday_2026-11-03.md`).
- **Neden bilinmiyor:** gerekçesi hiçbir yerde yazılmamış karar. Tahmin edilmedi.
- PR açıklamaları bu bilgisayardan okunamadı (`gh` yok, repo özel). Gerekçeler commit
  mesajlarından ve belgelerden alındı.

---

## Arama

### Reranker kullanılmıyor (eklendi, sonra çıkarıldı)
- **Ne zaman:** Eski pilotta ilk sürümle eklendi (bge-reranker-v2-m3, `d36b304`, 2026-10-10).
  Varsayılanda kapatıldı (`f130ac4`, 2026-10-27). Bu repo reranker olmadan başladı
  (0001, `#a32170c`).
- **Neden:** Ölçüm, 36 soru (`b4/asama4_matris_2026-10-27.md`):

  | Yapılandırma | hit@1 | hit@5 | Toplam p50 |
  | --- | --- | --- | --- |
  | Rerank yok | 0,72 | 0,89 | 227 ms |
  | + bge-reranker-v2-m3 int8 | 0,72 | 0,86 | 5,56 sn |
  | + qwen3-reranker-8b (bulut) | 0,72 | 0,94 | 611 ms |

  - 2026-11-03 ölçümü (158–160 soru, onaysız set, `b4/ozet_dondurulan_aday_2026-11-03.md`
    §2; qwen3-reranker-8b) iki yönlü:
    - Qwen3-8B + BM25 yolunda hit@1 0,74'ten 0,80'e çıktı.
    - Üçlü füzyonda 0,81'den 0,83'e çıktı.
    - Yalnız en güçlü aday listede (üçlü füzyon + çevrilmiş BM25) hit@1 0,86'dan 0,83'e
      düştü, hit@5 0,98'den 0,99'a çıktı.
    - `b4/README.md`: "reranker üç yolda da kazandırıyor".
  - Bu üç yol da Qwen3-8B kolunu içeriyor. **Bu reponun yapılandırmasında (bge-m3 +
    çevrilmiş BM25) reranker hiç ölçülmedi.** Kapalı kalmasının dayanağı 36 soruluk ölçüm
    ve gecikme.
  - Reranker skoru "bulunamadı" eşiği olarak da kullanılamadı: 18 soruda cevapsız ve
    cevaplı soruların skorları örtüştü (`docs/PILOT-RAPORU.md` §5.4).
- **Yeniden düşünülür:**
  - "Bulunamadı" kararı için bir skor eşiği gerekirse. Eski pilot bunu açık bıraktı,
    hiç ölçülmedi (kaynakta yazılı koşul).
  - Gerçek belgelerde doğru parça ilk 8'e giremiyorsa (hit@8 düşükse). Bu koşul kaynakta
    yok, kaydı yazanın önerisi.
- **Onay:** Yeni bileşen ve yeni model olduğu için ekip onayı gerekir.

### Yoğun vektör: yerel bge-m3, CPU
- **Ne zaman:** Eski pilotta ilk günden. Bu repoda 0001, `#a32170c`.
- **Neden:**
  - 9 embedding karşılaştırıldı (eski pilot, `b4/asama4_embedding`, 36 soru, 2026-10-27).
    Qwen3-8B (bulut) hit@1 0,78 verdi; bge-m3 + BM25 0,72 / 227 ms.
  - Qwen3-8B "reddedildi" diye yazılı bir karar yok:
    - `3d69fc2` (2026-11-03) Qwen3-8B'li üçlü füzyonu "dondurulan aday" yaptı, ama "hatta
      bağlanmadı". Aynı gün 20 çağrılık gecikme ölçümünde Qwen embed p95 23,9 sn çıktı
      (sağlayıcı kuyruğu).
    - `25df029`: "onaysız set, karar değil".
  - Yerel bge-m3 ile kalınmasının yazılı gerekçesi bu gecikme ve yukarıdaki maddeler.
  - bge-m3 çok dilli: Türkçe soru İngilizce belgede aranabiliyor.
  - Tek süreçte arama ve indeksleme aynı modeli bir kez yükler (0003).
  - Mac'te MPS hep 1,0 benzerlik verdi; o yüzden CPU'ya sabitlendi (eski pilot
    `PILOT-RAPORU` §6.1).
- **Yeniden düşünülür:** Yerel vektörleme gerçek belge hacminde kabul edilemez kalırsa.
  Bu bilgisayarda parça başına ~0,9 sn (açık notlar). Model değişikliği bütün indeksin
  yeniden kurulması demek.

### Seyrek kol: BM25 (bge-m3'ün sözcük ağırlıkları yerine)
- **Ne zaman:** Eski pilot `f130ac4` (2026-10-27). Bu repoda `#a32170c`.
- **Neden:** Rerank'sız hit@1 0,44'ten 0,72'ye çıktı (36 soru).
- **Yeniden düşünülür:** Koşul yazılmamış.

### Birleştirme: istemci tarafında, belirli sırayla RRF
- **Ne zaman:** Eski pilot `5f35276`. Bu repoda `#a32170c` (`retrieval/fusion.py`).
- **Neden:**
  - Qdrant'ın kendi RRF'i ile istemci RRF'i 39 sorunun yalnız 4'ünde aynı sırayı verdi.
  - İstemci tarafında gömülü ve sunucu kipi 39/39 aynı sırayı verdi; sonuç her koşuda aynı.
  - Eşitlikte önce dense skoru, sonra parça kimliği karar verir.
- **Bilinmeyen:** `_RRF_K = 2`, kol başına 30 aday ve birleşik 20 aday değerlerinin
  nedeni bilinmiyor.

### BM25 sorgusu belge diline çevrilir
- **Ne zaman:** Eski pilotta eklendi (2026-11-03) ve hatta bağlandı (2026-11-06). Bu repoda
  `generation/translate.py`, sınır 1,2 sn.
- **Neden:**
  - Eski pilot (`adim2/hat_rapor_2026-11-06.md`, Ek): yanlış ret 25'ten 11'e düştü.
    - Ölçüm onaylı 199 sorunun cevaplı 160'ında yapıldı (kural çıkışları hariç), 245
      sorunun tamamında değil.
    - Karşılaştırılan iki hat ("varsayılan yol" ve "ikili yol") yalnız çeviriyle
      ayrılmıyor. Farkın tamamı çeviriye bağlanamaz (`docs/MIMARI.md` A4.13).
  - Çeviri modeli Gemma 4, NextBit üzerinde. p95 1,04 sn, %2'si sınırı aşıyor.
    Gemma 3 ile DeepInfra'da %96'sı aşıyordu
    (`b4/asama4_ceviri_karsilastirma_2026-11-05`).
  - Yoğun arama özgün soruyla yapılır. Çeviri yalnız soru dili belge dilinden farklıysa
    çalışır; süreyi aşarsa özgün soruyla aranır.
- **Yeniden düşünülür:** Belgeler ve sorular aynı dilde olursa gereksiz kalır. FastReact
  ölçümünde 18 sorunun birinde sınır aşıldı.

### Modele 8 kaynak gider (5'ten artırıldı)
- **Ne zaman:** Eski pilot, Adım 2 (2026-11-06). Bu repoda `DEFAULT_TOP_K = 8` (0001).
- **Neden:** Ölçüm `adim2/hat_rapor_2026-11-06.md`, Ek (onaylı 199 sorunun cevaplı 160'ı).
  5 kaynakla 1 doğrulanmış yanlış değer çıktı (B012, "bulunamadı" beklenen soru), 8 kaynakla
  0. Maliyet 0,0525 $'dan 0,0614 $'a çıktı.
- **Yeniden düşünülür:** Yalnız yeni ölçümle. Kaynak sayısını düşürmek bilinen bir
  doğrulanmış yanlışı geri getirmişti.

### İçindekiler parçaları aramadan elenir
- **Ne zaman:** Eski pilot `5f35276`. Bu repoda `#a32170c` (`is_table_of_contents`).
- **Neden:** Eski pilotta hit@5 0,86'dan 0,89'a çıktı, hit@1 0,75'ten 0,72'ye indi. Bu
  fark "±1 soru, gürültü" olarak yazılmış. Etkisi kanıtlanmış değil.
- **Not:** Yalnız noktalı satır biçimini tanıyor. FastReact'taki `00_Keyword_Index.md`
  elenmiyor; bir soruda 1. sıraya çıktı (`evals/output/fastreact/gozlemler.md`; bu dosya
  yerel ölçüm çıktısı, repoda yok).

### Soruda geçen kod, kodu içeren parçayı doğrudan kaynağa ekler
- **Ne zaman:** `#a32170c` (kod başına en fazla 2 parça). Sesli yazımlar `#2ad898d`, takip soruları `#c41089d`.
- **Neden:** Kod hiçbir belgede yoksa arama ve model çalışmadan "geçmiyor" denir.
  Parça sınırının (2) nedeni bilinmiyor.

## Parçalama ve dönüştürme

### Parça en fazla 900 karakter; başlık sınırı, tablo satırı ayrı parça
- **Ne zaman:** Eski pilotta `d36b304`'ten beri hiç değişmedi. Bu repoda `#1475acb`
  (`ingest/chunking.py`).
- **Neden:**
  - Eski pilotta 1.500 karakterden uzun paragraflarda değer kayboluyordu. Bu yüzden
    paragraflar cümle sınırından bölünüyor (`PILOT-RAPORU` §6.2).
  - 900 değerinin kendisinin nedeni bilinmiyor; hiç ölçülmedi.
- **Yeniden düşünülür:** Gerçek belgelerde değer parçalar arasında bölünüyorsa.
- **Onay:** Ekip onayı ve yeniden indeksleme gerekir.

### Vektörlenen metin: "belge başlığı | bölüm" + parça metni
- **Ne zaman:** `#1475acb` (`Chunk.embed_text`).
- **Neden:**
  - Eski pilot öneke kayıttan marka ve ürün adını da koyuyordu. Bunun nedeni, reranker'ın
    ceket ve pantolon belgelerini ayıramamasıydı (`docs/SIMPLIFY.md` D19 ve H-R4: tek
    belge ailesine göre ayarlı).
  - Bu repoda yalnız başlık ve bölüm adı var. Değişikliğin ölçümü yok.

### Markdown başlıklarıyla okunur (değiştirildi: önce düz metindi)
- **Ne zaman:**
  - İlk hâl: `#1475acb`, `.md` düz metin olarak okunuyordu. Neden bilinmiyor.
  - Değişiklik: `#c44c599` (PR #16, 2026-11-12), `ingest/markdown.py`.
- **Ne değişti:**
  - CommonMark ve tablolarla okunuyor (markdown-it-py, zaten bağımlılıktı).
  - Başlıklar düzeyleriyle bölüm yolu oluyor ("Ayarlar · Genel · Hafta numaraları").
  - Vurgu, satır içi kod işareti ve kaçış ters bölüsü metinden çıkıyor. Bağlantının metinde
    yazmayan adresi parantez içinde kalıyor. HTML aynen kalıyor; yalnız `<br>` satır sonu
    oluyor.
  - Tablo satırları başlıklarıyla ayrı parça. Sıralı listede madde numarası kalıyor.
  - Sayfası ve sayfa adı olmayan parçanın konumu bölüm yolu (`SourceLocation.section`).
    Kaynak etiketi ve kaynak paneli bunu gösteriyor.
  - Kural biçim düzeyinde. Başlık düzeyi bildirmeyen biçimlerde (PDF, Excel) bölüm kuralı
    değişmedi.
- **Neden:**
  - Ürün hedefi "cevabın kaynak bölümü görünür" ve FastReact belgeleri markdown.
  - Önce başlıklar bölüm adı olmuyordu ve kaynak yalnız dosya adıyla görünüyordu.
  - Kaynak panelinde ham `**` ve `\*` işaretleri görünüyordu.
- **Onay:** Bölme mantığı değişikliği ve markdown belgelerinin bir kez yeniden işlenmesi
  ekip tarafından onaylandı (2026-11-12).
- **Ölçüm** (FastReact 18 soru, her soru bir kez):
  - Parça sayısı 1847'den 3648'e çıktı; 967'si tablo satırı.
  - Doğrulanmış cümle 30'da kaldı, gizlenen cümle 0'dan 2'ye çıktı. İkisi de modelin
    alıntı seçimi; kalıcı olup olmadığı bilinmiyor (açık notlar).
  - Beklenen dosya 1. sırada: 9/17'den 14/17'ye. Aynı belgenin bölümleri (`_partN`) tek
    belge sayılınca 11/17'den 14/17'ye. Beklenen dosyalar
    `ornek-belgeler/03_Test_Sorulari.md` tablosundan.
  - Seed 7 ve seed 11 soru bazında aynı: 37/40, doğrulanmış yanlış 0. Soruların 38 ve
    39'u önbellekten geldi, yani modele giden bağlam değişmedi. Bu sonuç modelin yeniden
    davranışını değil, örnek belgelerin parçalarının etkilenmediğini gösteriyor.
  - Vektörleme süresi: ölçüm indeksi 1655 sn'den 3468 sn'ye çıktı. Ama bu sırada uygulama
    da aynı anda vektörlüyordu; temiz süre ölçülmedi. Parça sayısı iki katına çıktığı için
    sürenin de yaklaşık iki katına çıkması bekleniyor (çıkarım, ölçüm değil).
- **Yeniden düşünülür:** Gerçek markdown belgelerinde parça sayısı ve süre kabul edilemez
  olursa, ya da gizlenen cümleler kalıcı çıkarsa.

### PyMuPDF kullanılmaz; Docling ve pypdfium2
- **Ne zaman:** 0001. Eski pilot PyMuPDF kullanıyordu.
- **Neden:**
  - PyMuPDF AGPL lisanslı (eski pilot `docs/arastirma/02-pdf-isleme.md`).
  - Eski pilotta PyMuPDF metin katmanı yedeği 143 sayfa kurtarmıştı. Docling bir belgenin
    sayfalarının %94'ünü görsel saymıştı.
  - Bu repoda aynı iş pypdfium2 ile yapılıyor: ayrıştırıcının metin katmanının yarısından
    azını yakaladığı sayfa yeniden okunur (`pages_missing_text`).
- **Yeniden düşünülür:** Lisans durumu değişirse.

### Office dosyaları LibreOffice ile PDF'e çevrilir; .xlsx doğrudan okunur
- **Ne zaman:** `#1475acb`. Eski pilot yalnız PDF okuyordu.
- **Neden:** Gerçek belgeler karışık türde geliyor (CLAUDE.md kural 3).
- **Not:** Ağır araçlar yalnız işçide çalışır; belgeler internetsiz işlenir (0001).

### Excel sayıları gösterildiği biçimde yazılır; Türkçe bölge ayarı varsayılır
- **Ne zaman:** `#c44c599` (PR #16, 2026-11-12), `ingest/spreadsheet.py`. Önce kayıtlı ham
  değer yazılıyordu: yüzde biçimli hücre `0.12`, tutar `1234.5`.
- **Ne yapılıyor:**
  - Biçim kodunun ilk bölümü uygulanıyor: yüzde, binlik ayraç, ondalık hane, tırnaklı sabit
    metin, sıfır doldurma.
  - Tarih, kesir ve bilimsel gösterim desteklenmiyor. Tarih ISO biçiminde, diğerleri genel
    biçimde yazılıyor.
  - **Bilinen sınır, para birimi simgesi:** Excel'in kendi para birimi biçimindeki köşeli
    parantezli simge (`[$₺-41F]`, `[$TL-41F]`) yazıdan düşüyor: `1.234,50`. Tırnaksız `TL`
    içeren biçim genel biçime düşüyor: `1234,5`. Yalnız tırnaklı `"TL"` korunuyor:
    `1.234,50 TL`. Önceki hâlde de simge yoktu, gerileme değil. Ama içerik kaybı (kural 3);
    açık notlarda.
  - Eksi değer her zaman eksi işaretiyle yazılıyor. Biçimin eksi bölümü (parantez, yalnız
    renk) kullanılmıyor; işaret kaybolup değer değişmesin diye.
  - Kayıtlı değeri olmayan formül hücresi okunamıyor. Belge raporunda hücresiyle birlikte
    uyarı olarak çıkıyor; önceden sessizce kayboluyordu.
- **Bölge ayarı kararı:** Excel sayıyı açan bilgisayarın bölge ayarıyla gösterir ve dosyada
  bölge yazmaz. Türkçe bölge ayarı (ondalık virgül, binlik nokta) varsayıldı; ekip onayladı
  (2026-11-12).
- **Yüzde işaretinin yeri:** Biçim kodundaki gibi kalıyor (`12%`). Türkçe Excel'in `%12`
  gösterip göstermediği denenmedi; ekip kararıyla dokunulmadı.
- **Neden:** Kaynaktaki yazılışla eşleşme bozuluyordu ve değer sessizce eksilebiliyordu
  (kural 3: içerik kaybı olmamalı).
- **Ölçüm:** Örnek Excel dosyalarında bütün hücreler metindi; taban sonuçları değişmedi.
  Biçimli sayı içeren gerçek dosyayla ölçülmedi.
- **Yeniden düşünülür:** Belgeler başka bölge ayarlı bilgisayarlardan gelirse, ya da gerçek
  dosyalarda yüzde ve tarih yazılışı kaynakla eşleşmezse.

### Parçalama kuralının sürümü belgeye kaydedilir
- **Ne zaman:** `#c44c599` (PR #16, 2026-11-12), `ingest/formats.py` (`RULES_VERSIONS`).
- **Ne yapılıyor:**
  - Her biçimin kural sürümü belge raporuna yazılıyor.
  - Eski sürümle işlenmiş belge listede "eski okuma kuralıyla işlendi" diye görünüyor.
  - Bir biçimin parçalarını ya da konumlarını değiştiren her değişiklikte o biçimin sürümü
    artırılıyor. Markdown, metin, SQL ve Excel 2'de; PDF, Office ve görsel 1'de.
- **Neden:** Parçalama kuralı değişince eski belgeler sessizce eski parçalarıyla kalıyordu.
  Hangi belgelerin yeniden işlenmesi gerektiği bilinmiyordu.
- **Neden kodla engellenmedi:**
  - Uygulama hiçbir zaman toplu yeniden indeksleme yapmıyor.
  - Ölçümde indeks zaten parmak iziyle korunuyor.
  - Yeniden işleme elle (ekip kararıyla) yapılıyor.
- **İlk kullanım:** 366 belge (362 md, 3 xlsx, 1 sql) tek seferde yeniden işlendi. Sonuç:
  377/377 hazır, eski kuralla kalan 0.
- **Onay:** Bu yeniden işleme ekip tarafından bir kez onaylandı (2026-11-12). Sonraki
  sürüm artışları yeniden onay ister.

### OCR: OCRmyPDF, belge başına dil (ilk okuma tur+eng), iki okuma
- **Ne zaman:**
  - Eski pilotta plan Docling ve Tesseract'tı (`docs/PLAN-OCR.md` §7). Yerine OCRmyPDF
    geldi (Ghostscript'siz, §9).
  - İki okuma kuralı: eski pilot `87f91c1`. Bu repoda 0001, `#f2a8c6d`, `#236e789`.
- **Neden:**
  - OCRmyPDF ile bilinen bütün kesir hataları düzeldi. Cevaplanabilir OCR sorusu 9'dan
    16'ya çıktı. Süre sayfa başına 1,1 sn; önceki yolda 5–7 sn'ydi.
  - Pilotta `tur+eng` birlikte kullanılınca 70 Türkçe harften 40'ı bozuldu. Bu yüzden OCR
    tek dille yapılıyordu. Bu repoda ilk OCR artık `tur+eng` (aşağıda, yeni kanıt).
    - Bu repoda dil belge başına seçiliyor: `run_ocr(..., meta.language, ...)` ve
      Tesseract'a tek `-l` veriliyor.
    - Pilotta da kayıttaki dil esastı; sayfa aralığı yalnız `lang_ranges` verilirse
      kullanılıyordu (`PLAN-OCR.md` §9).
  - **İlk OCR `tur+eng` (değiştirildi, 2026-11-12, `ocr-tur-eng` dalı):**
    - Yüklemede belgenin dili "bilinmiyor" kaydediliyor (`UNDETECTED_LANGUAGE`). İlk OCR
      Türkçe ve İngilizce birlikte yapılıyor (`ingest/external.py`, `tesseract_language`).
    - Belge işlenince dil parçalardan okunuyor. Yeniden işlemede tespit edilen dil (`tur` ya
      da `eng`) kullanılıyor.
    - Önce yüklemedeki dil hep `tr` idi, ilk OCR her belgede yalnız Türkçeydi.
    - Mevcut indeks yeniden işlenmedi; değişiklik yeni yüklemelerde geçerli.
  - **Yeni kanıt (8 okumalık ölçüm, yerel, Tesseract 5.4.0):**
    - Belgeler: 2 İngilizce (bir FastReact metni, sayı, kod ve birim içeren bir teknik föy)
      ve 2 Türkçe. Her biri iki açıyla taranıp `tur`, `eng` ve `tur+eng` ile okundu.
    - `tur`: İngilizce föyde tablo hücresi 12.5 "25" okundu. Türkçe sayfada "%3'ü" iki
      okumada "963'ü" oldu.
    - `eng`: Değer hatası yok, ama Türkçe harflerin hepsi bozuldu (0/41).
    - `tur+eng`: İngilizcede hata yok; Türkçede bir okumada "963'ü". Türkçe harfler
      korundu.
    - Pilottaki "`tur+eng` 70 Türkçe harften 40'ını bozdu" bulgusu bu kurulumda tekrar
      etmedi.
    - Bugünkü akışta hatalı okunan iki değeri de ikinci okuma belirsiz işaretleyip gizledi.
  - **Sınırı:** Temiz yazı tipiyle üretilmiş taramalar, 4 belge, belge başına 1–2 sayfa.
    Gerçek taramalarla tekrarlanmalı.
  - İki okuma 303 dizede 0 yanlış değer kabul etti. RapidOCR yalnız ikinci okuma: Türkçe
    harflerde 70'te 48 doğru.
  - Uyuşmayan değer gizlenir; uyuşan değer "Kısmen doğrulandı" olur.
- **Bilinmeyen:** Küçük görsel eşiğinin (kısa kenar 50 pt, alan %2) nedeni bilinmiyor.
- **Yeniden düşünülür:** Gerçek fotoğraf ve taramalarla (açık notlar).

### SQL komutları kod bloğu olur; komut aynen gösterilir
- **Ne zaman:** 0001, `#1475acb`, `#cae391f`.
- **Neden:** Kural "sistem komutu yerleştirmez, değiştirmez, çalıştırmaz" (0001). Model
  komutu yazmaz, yalnız kaynak numarasını verir (`kod_kaynak_no`). Ölçüm yok.

## Cevap modeli ve istem

### Cevap modeli: Gemma 4 26B A4B (OpenRouter, ZDR)
- **Ne zaman:** Eski pilotta yerel qwen2.5:7b'den buluta geçildi. Bu repoda 0001 ve 0002.
- **Neden:**
  - Yerel 7B modeli 18 sorunun 9'unu doğru cevapladı (`PILOT-RAPORU` §1).
  - Bu repoda 35 soruda (0002) Gemma 4 26B 33 geçti, 0 yanlış değer verdi; ortanca süre
    1,57 sn, maliyet 35 soru için toplam 0,0068 $. Sıradaki aday Qwen 3.6 35B: 31 geçti,
    0 yanlış değer, 3,14 sn.
  - Gemma 4 31B 25 geçti. Eski pilotta Crusoe sağlayıcısında 32 kesik cevap vermişti
    (`adim2/okuma_nihai_ara_2026-11-05.md`). Aynı tabloda 26B de Parasail'de 34 kesik
    veriyor; kesiklerin kaynağı modelden çok sağlayıcı.
  - Sıralama ölçütü: önce yanlış değer, sonra doğruluk, sonra süre ve maliyet.
  - İstem Gemma üzerinde ayarlandı; karşılaştırmada ona biraz avantaj var.
- **Yeniden düşünülür:**
  - Model değişikliği yalnız ölçümle yapılır (kural 5).
  - GPT-OSS 120B ve GLM 5.3 Flash istemci uyumsuzluğu yüzünden ölçülemedi.

### Sağlayıcı sırası: DeepInfra, Venice, Parasail; yedeğe yalnız kesintide geçilir
- **Ne zaman:** Eski pilotta önce Venice birinciydi; 2026-11-06'da DeepInfra'ya geçildi.
  Bu repoda `settings.answer_providers`.
- **Neden:**
  - Venice girintili JSON yazmaya başladı; JSON ortasında boşluk kaçağı oldu. Kaçak sayısı
    Venice'te 16, Parasail'de 12, DeepInfra'da 0 (`adim2/okuma_nihai_ara_2026-11-06.md`,
    `adim2/plan_cevap_modeli_2026-11-05.md`).
  - Yedeğe geçme koşulları: 2,5 sn içinde ilk token gelmezse ya da üst üste 40 boşluk
    karakteri gelirse.

### İlk token sınırı yalnız ilk tokene kadar; sonra akışın durma sınırı 10 sn (düzeltildi)
- **Ne zaman:** `#bf3248a` (PR #18 ile birleşti, 2026-11-12),
  `generation/openrouter.py`.
- **Ne değişti:**
  - 2,5 sn'lik ilk token sınırı httpx okuma zaman aşımı olarak veriliyordu ve akıştaki her
    okumaya uygulanıyordu. İlk tokendan sonra sağlayıcı 2,5 sn'den uzun durursa cevap
    `ReadTimeout` ile düşüyor, yedek sağlayıcıya ya da yarım cevaba geçiliyordu.
  - Artık ilk token sınırı deneme başında kurulan `asyncio.timeout`; ilk içerik gelince
    kalkıyor. Akışın okuma sınırı ayrı bir durma sınırı (`_STALL_SECONDS = 10`).
- **Neden:** Hata düzeltme. Model, istem ve ayar değişmedi.
- **Bilinmeyen:** 10 sn değeri ölçülmedi. Sağlayıcının normal cevaplarında ilk tokendan
  sonraki en uzun duraklama bilinmiyor.
- **Yeniden düşünülür:** Soru kaydında cevaplar 10 sn'lik durma yüzünden düşüyorsa.

### Yalnız ZDR uçları; yerel modele otomatik geri dönüş yok
- **Ne zaman:** 0001. Eski pilotta `5f35276` (ZDR zorunlu), `323efdb` (uç düzeyinde
  denetim). Bu repoda `fetch_zdr_index` ve `select_providers`.
- **Neden:**
  - Buluta yalnız parçalar gider; sağlayıcı veri saklamamalı (kural 4).
  - Hata durumunda "servis kullanılamıyor" mesajı ve bulunan kaynaklar gösterilir (eski
    pilot PRD A7). Yerel modelin kalitesi ölçümde yetersiz bulundu (yukarıda).
  - Gemini 3.1 Flash Lite ZDR denetiminden geçmedi (0002).

### İstem şeması: her öğede önce alıntı, sonra cümle; tek satır JSON
- **Ne zaman:** Eski pilotta şema C (§15, 2026-11-05), c150b-J ve c150b-JSN. Bu repoda
  `#cae391f` (`answer_v1.md`, `answer_v1.schema.json`).
- **Neden ve reddedilen sürümler** (eski pilot, `adim2/okuma_nihai_ara_2026-11-06.md`):
  - **Önce cümle sonra alıntı (c150b-JM):** reddedildi. ✖ 20'den 27'ye çıktı ve
    doğrulanmış yanlış (B012) geri geldi.
  - **Ayrı sesli metin alanı:** kaldırıldı (JS). Ses yalnız doğrulanmış öğelerden
    üretiliyor.
  - **Niteleyici kuralı (JSN):** B012 10 tekrarın 10'unda doğrulanmış yanlıştı, 0'a indi.
    Yanlış ret 6'dan 10'a çıktı; bu bedel kabul edildi.
  - **Gevşek niteleyici eşleşmesi (JSNE):** reddedildi. Yanlış ret 10'da kaldı, ✓ 5 düştü.
  - **max_tokens 700'den 1200'e çıktı:** 700 sınırında uzun cevaplar kesiliyordu. 1200
    sınırı kesiklerin 6'sından 4'ünü kapattı. İlk doğrulanmış cümle süresi değişmedi
    (1,5–2,4 sn) (`adim2/okuma_nihai_ara_2026-11-06.md` §3). 2026-11-05 notu ise 1200'ün
    bazı retleri düzeltmediğini yazıyor.
- **Not:** Eski pilotun istemi tekstile özgüydü (`SIMPLIFY.md` D1–D3). Bu repodaki istem
  alandan bağımsız (0001).

### Bu repodaki istem değişiklikleri
| Commit | Değişiklik | Ölçüm |
| --- | --- | --- |
| `#a2eaf46` | Farklı değerler tek satırdaysa da netleştirme sorulur | Yazılmamış |
| `#2ad898d` | Kural 7: beden, model ya da sürüm anlaşılmıyorsa tahmin etmeden netleştirme. Kural 9: yalnız sorulan değer (diğer bedenler ve ayrı sütundaki tolerans eklenmez); cevap sesle de okunduğu için tek kısa cümle, parantezsiz. Kural 11 (yeni): sesten gelen dolgu sözleri, tiresiz ya da küçük harfli kod, taranmış tablolarda gürültülü sütun etiketi | Yazılmamış |
| `#0e60352` (PR #14) | Kural 9: ayarın adı, yeri ve yanındaki not ayrı öğe | seed 7 37/40, seed 11 37/40, yanlış 0, önce ve sonra aynı |
| `#676e9e0` (PR #24) | Kural 10 (şekil kaynakları) ve kural 11'deki bedene özgü gürültülü etiket maddesi silindi | Aşağıda, "Birim kuralı" |
| `#87860fa` (`sadakat-turu-2`) | Kural 3: "Birimi yalnız kaynakta yazılıysa yaz; kaynakta birim yoksa sayıyı kaynaktaki gibi ver." | Aşağıda, "Birim kuralı" |

- **Bedene özgü kural silindi (ekip kararı):** `#2ad898d`'nin gürültülü etiket kuralı
  ("Etiketin son harfi sorudaki bedenle aynıysa o sütun aranan sütundur") bedene özgüydü ve
  CLAUDE.md kural 2'ye aykırıydı.
  - Yerine genel bir kural yazılmadı.
  - Sadakat turu ölçümünde kötüleşen 18 sorunun hiçbiri bu silmeden değil (önbellekten neden
    ayrımı, 2026-11-12).
- **Ölü şekil açıklaması kaldırıldı:** İstemin 10. kuralı, `generated` alanını okuyan kod ve
  doğrulamadaki ilgili dal kaldırıldı (aşağıda, "Şekil açıklaması modeli taşınmadı").

Bundan sonra istem değişikliği ekip onayı ister (CLAUDE.md). İstem değişince cevap önbelleği
geçersiz olur.

## Doğrulama

### Doğrulama yalnız kodla yapılır; LLM hakem yok
- **Ne zaman:** 0001. Eski pilot `docs/MIMARI.md` B2.1.
- **Neden:**
  - Eski pilot LLM hakemini ve ajanlı RAG'ı öngörülemez buldu. Küçük modeller tek bir
    talimatı bile tutarlı izlemedi.
  - Ölçümde de cevaplar LLM ile puanlanmaz.
- **Yeniden düşünülür:** Anlam düzeyindeki boşluklar (olumsuzlama, yanlış sütun) biçim
  kuralıyla kapanmıyor (açık notlar). Ayrı tasarım gerekir.

### Sayı, kod ve teknik ad cümlenin kendi alıntısında birebir geçer
- **Ne zaman:**
  - Eski pilotun ilk doğrulayıcısı model ve hata kodu rakamlarını sayı denetiminden muaf
    tutuyordu (`MIMARI.md` A4.10).
  - Bu repoda kodlar da denetleniyor: 0001, `#cae391f`. Küçük harfli kodlar `#d0fdd01`
    ile eklendi.
- **Neden:** Kodları kapsama kararının gerekçesi bilinmiyor. Genel ilke: yanlış değer
  gösterilmez.

### Alıntı karşılaştırması: elle yazılmış işaret kuralları yerine markdown ayrıştırıcısı (değiştirildi)
- **Ne zaman:**
  1. `#2805840`: elle yazılmış biçim kuralları (`quote_form`).
  2. `#60fa7ad`: Bugbot bulgusuyla düzeltildi.
  3. `#deb693d` (PR #4): kurallar kaldırıldı, yerine markdown-it-py geldi.
- **Neden:**
  - FastReact'ta 4 doğru cümle yalnız biçim farkı (`**`, `\*`, tırnak türü) yüzünden
    gizleniyordu.
  - Elle yazılmış düzenli ifade eşsiz `**` işaretini yanlış eşleştiriyordu. Sonuç hem
    haksız kabul hem haksız retti.
  - Önbellekten ölçüm: FastReact'ta gizlenen cümle 5'ten 0'a indi, kaynakta olmayan değer
    0, taban setleri değişmedi.
- **Bilinen kalan:** Satır içi kodda kaçış artığı yüzünden haksız ret oluyor (açık notlar).

### Sayı kuralları sertleştirildi (PR #7, #8, #9; 2026-11-11)
Bu kurallar haksız kabulü kapatır:

- Alıntı bir sayının ortasından başlayamaz, ortasında bitemez (`#8a6141e`).
- Kesik alıntının denetlenmeyen kuyruğunda sayı, kod ya da yazıyla sayı olamaz
  (`#40f0850`, `#2ec350a`, `#c9d44c5`).
- Binlik ayraç ve eksi işareti değeri değiştiremez (`#9104a31`, `#2c1fca6`).
- Netleştirme sorusu kullanıcının söylemediği değeri taşıyamaz (`#c96aede`).

Her birinin bulgusu commit mesajında. Sınır durumlarını sınayan set: `#f603b5f`.

### Birim kuralı: birim alıntıda ya da değerin kendi başlığında yazılı olmalı (değiştirildi)
- **Önceki hâl:** `#3059a93` ile yalnız kaynaktaki birimle çelişen birim reddediliyordu.
  - Kaynakta birimi olmayan değere eklenen birim reddedilmiyordu.
  - Gerekçe: Mac'teki önbellek ölçümünde 51 cevap öğesinin 19'unda görülmüştü; reddetmek
    büyük haksız ret sayılmıştı.
- **Ne zaman:** `#676e9e0`, `#f509be4` (PR #24); `#87860fa` (`sadakat-turu-2`).
- **Kural** (`verification/answer.py`, `_unit_problems`):
  - Cümlede sayının yanındaki birim, alıntıda o sayıyla birlikte yazılı olmalı. Ya da sayıyı
    taşıyan hücrenin kendi sütun başlığında yazılı olmalı.
  - Başlıkta yalnız parantez ya da köşeli parantez içindeki birim sayılır ("Ücret (TL)",
    "Boy [mm]"). Parantezsiz tek harfli sütun adı ("Beden M") birim sayılmaz.
  - Başka sütunun başlığı sayılmaz. "(cm)" yalnız Tolerans sütunundaysa beden değeri "cm"
    alamaz.
  - Devrik tabloda satırın ilk hücresindeki parantezli birim ("Tork (Nm)") o satırın
    değerlerine sayılır.
  - Kodun içindeki rakam ("PNT-1126 S") değer sayılmaz.
  - Geçemeyen cümle gizlenir; yeniden yazılmaz.
- **İstem:** Cevap isteminin 3. kuralına eklendi: "Birimi yalnız kaynakta yazılıysa yaz;
  kaynakta birim yoksa sayıyı kaynaktaki gibi ver."
- **Ürün sahibi kararı (2026-11-12):** Desteklenmeyen birim silinmez, uyarıyla da gösterilmez;
  cümle gizlenir. Gerekçe: gösterilen ve seslendirilen her şey doğrulanmış olmalı.
- **Neden:** Kaynakta yazmayan birim değeri doğrulanmış gösteriyordu. Sadakat turundan önce
  iki taban setinde gösterilen 51 öğenin 13'ünde vardı (örnek: "PNT-1162 L beden bel 42,5
  cm"; kaynakta "(cm)" yalnız Tolerans sütununda).
- **Ölçüm** (seed 7, seed 11, FastReact, sınır seti; iki kez canlı, `sadakat-turu-2`):
  - Gösterilen birim eklenmiş öğe 0.
  - Doğrulanmış yanlış her sette 0.
  - Sınır setinde yanlış sütun 7/7, olumsuzlama 5/5.
  - Geçen soru seed 7'de 34 ve 33, seed 11'de iki koşuda da 35 (önce 37 / 37).
  - Gösterilen doğru cümle sadakat öncesine göre %12,2 az: 49'dan 43'e.
  - Kalan düşüşlerin hepsi, model birimsiz değere "cm" eklediği için gizlenen cümle (açık
    notlar).
- **Bedeli:** Doğru değerli bir kısım cümle gösterilmiyor. Ürün sahibi bu bedeli doğrulanmamış
  birime tercih etti.
- **Yeniden düşünülür:** Ürün sahibinin denemesi ve gerçek belgelerle. Gizlenen doğru cümle
  kabul edilemez çıkarsa.

### Birim yüzünden gizlenen cümlenin yerine kaynak alıntısı gösterilir
- **Ne zaman:** Ürün sahibi kararı, 2026-11-12. `birim-alinti` dalı.
- **Kural:**
  - Cümle yalnız "kaynakta yazmayan birim" yüzünden geçemiyorsa "gösterilmiyor" yazısı
    yerine o cümlenin doğrulanmış alıntısı olduğu gibi gösterilir: `Kaynakta yazan: "…"`.
    Yanında belge ve sayfa düğmesi durur.
  - Modelin cümlesi gösterilmez, değiştirilmez; birim silinmez.
  - Başka bir nedenle de geçemeyen cümle eskisi gibi gizlenir. Alıntı birebir doğru değilse,
    sayı alıntıda yoksa ya da OCR değeri belirsizse cümle gizlenir.
  - **Ses (ürün sahibi kararı, 2026-11-12, `alinti-ses` dalı):**
    - Alıntı sesle okunmaz. Ses yalnız "Kaynaktaki satır ekranda gösteriliyor." der.
      Konuşma modunda da "Cevabı seslendir" düğmesinde de aynı.
    - Gizlenen her cümlenin yerine alıntı gösterildiyse "doğrulanamadı" bildirimi ("Bazı
      değerler doğrulanamadı, ekrana bakın") çalmaz.
    - Alıntısız gizlenen bir cümle de varsa bildirim eskisi gibi çalar.
    - Gerekçe: Alıntı birden çok bedenin değerini taşıyabilir ("S: 38,5 | M: 40,5 | L:
      42,5"). Sesle okunursa işçi yanlış bedenin değerini duyabilir.
    - İlk sürümde (`birim-alinti`) ses alıntıyı okuyordu; bu kararla değişti.
  - Kod: `ItemCheck.quote`, `AnsweredItem.source_quote`, akıştaki `item_unverified`
    olayının `quote` alanı.
- **Neden:** Gösterilen ve seslendirilen her şey doğrulanmış olmalı. Alıntı kaynakta birebir
  geçtiği için doğrulanmış; modelin eklediği birim gösterilmiyor. Kullanıcı değeri yine de
  kaynağın kendi yazımıyla görüyor.
- **Ölçüm** (seed 7, seed 11, sınır seti; önbellekten, canlı maliyet 0,0002 $):
  - Doğrulanmış yanlış 0.
  - Gösterilen, kaynakta olmayan birim 0. Gösterilen birimli öğelerin hepsinde birim kendi
    sütun ya da satır başlığında: "Aylık tutar (TL)", "Ücret (TL)", "(°C)", "Tork (Nm)".
  - Geçen soru değişmedi (34/40, 35/40, 27/27).
  - Alıntıyla gösterilen cümle 6, hepsi birimsiz beden değerine "cm" eklenen cümle (seed 7'de
    3, seed 11'de 3).
- **Bilinen:**
  - Alıntı tablo satırının tamamı olabilir ("Ölçü noktası: Bel | S: 38,5 | M: 40,5 | L:
    42,5 | Tolerans (cm): 1,0").
  - Taranmış belgeden gelen alıntı OCR gürültüsünü olduğu gibi taşır ("Ölçü noktau", "ıi").

### Yanlış sütun ve olumsuzlama için kural yazılmadı (önce ölçüldü)
- **Ne zaman:** `#f5b4ec5` (PR #19, 2026-11-12).
- **Karar:** Ekip yön olarak biçim ve dil düzeyinde kuralı seçti; yerel model (NLI) ya da
  LLM ile denetim yok. Ama kural yalnız hata gerçekten görülürse ve yalnız görülen kısım
  için yazılacak.
- **Ölçüm:**
  - Sınır setine 7 yanlış sütun sorusu eklendi: komşu sütunda yakın değer; Excel, PDF ve
    Word tablosu; biri yanlış değeri onaylatan soru.
  - 5 olumsuzlama sorusu eklendi: Türkçe ve İngilizce kaynak; biri olumlu denetim.
  - Her soru bir kez soruldu. 12 cevabın hepsi doğru, doğrulanmış yanlış 0. Olumsuzlama
    cevapları cevap metni okunarak sınıflandırıldı.
- **Neden kural yazılmadı:** Model bu hatayı yapmadı. Kural her cevaba haksız ret riski
  ekler.
- **Yeniden düşünülür:** Gerçek belgelerde ya da tablolarda yanlış sütun ya da tersine
  çevrilmiş olumsuzluk görülürse; yalnız görülen kısım için.
- **Reddedilenler:** Yerel çıkarım (NLI) modeli ve yardımcı LLM ile anlam denetimi. Neden:
  yeni model gerektirir ya da "LLM hakem yok" kararıyla çelişir.

### Tablo varyant denetimi (K9) eklenmedi
- **Ne zaman:** 0002. Eski pilotta vardı (`73852bc`), ama ölçülen hatta (c modu)
  kullanılmıyordu.
- **Neden:** Son sınav dahil hiç doğrulanmış yanlış değer çıkmadı. Denetim gereksiz soru
  riski taşıyor.
- **Yeniden düşünülür:** Gerçek tablolarda yanlış satır ya da sütun görülürse.

### Sayı sözcükleri ve birimler tek tabloda; ses değeri yorumlamaz
- **Ne zaman:** 2026-11-13. `deger-dogrulugu` dalı (inceleme listesi #1, #4, #5).
- **Kural:**
  - Yazıyla sayılar ve birimler `verification/text.py`'de tek tabloda. Doğrulama, akış maskesi
    ve sesli okuma oradan beslenir.
  - Bir sayı bütün ayraçlarıyla tek değerdir: "1,234.50", "1.234,50", "12.05.2024" bölünmez.
    Ondalığı düşmüş "1,234" ya da tarihten koparılmış "2024" doğrulanmaz.
  - Türkçe "on" (10), "on bir", "on iki" yalnız Türkçe metinde sayıdır. Cümlede cevabın dili,
    alıntıda belgenin katalogdaki dili kullanılır; dili bilinmeyen kaynakta sayılmaz. Belge dili
    `document_language` ile belirlendiği için onun düzeltmesi (#6) buraya da yansır.
  - Kaynaktaki "on", cümledeki "on"u yalnız ikisinin ardındaki sözcük aynıysa karşılar ("on
    dakika" ↔ "on dakika"). Rakamla yazılmış 10'un kanıtı olamaz ("click on Save", "ON
    konumu"). Tamamı büyük harfli "ON" hiçbir tarafta sayı değildir (anahtar konumu).
  - "lt", "l"nin eş anlamlısı. "gr" yalnız Türkçe belgede "g" ile eş; İngilizce belgede grain
    olabileceği için ayrı birim kalır. Kaynakta birimsiz değere eklenen birim cümleyi gizler.
  - Ses yalnız Türkçe binlik biçimini ("1.234,50", "1.234.567") değeriyle okur. Öteki her
    ayraç adıyla, sonrası rakam rakam okunur: "1.500" bir nokta beş sıfır sıfır, "14.30" on
    dört nokta üç sıfır, "42,5" kırk iki virgül beş. Tek harfli birim yalnız küçük harfle
    birimdir ("38 M" beden); "g" okunmaz (ivme de olabilir).
- **Neden:** Sesli okuma "1.500"ü 1,5 okuyordu; "on dakika" kaynakta ne yazdığına bakılmadan
  geçiyordu; kaynakta "1,234.50" varken "1,234" doğrulanıyordu (kural 1).
- **Ölçüm** (seed 7, seed 11, FastReact; önbellekten, 0 $, ıska 0): hiçbir soru ve madde
  değişmedi; gizlenen cümle 10'da kaldı, doğrulanmış yanlış 0. Ölçülen cümlelerin ve taban
  belgelerinin okunuşu da değişmedi; etkiyi yalnız yeni testler gösteriyor.

## Netleştirme ve sohbet

### Elle yazılmış netleştirme kuralları çıkarıldı
- **Ne zaman:**
  - Eski pilotta eklendiler (2026-10-10…16): soru öncesi netleştirme, sözlük, marka takma
    adları, K7 arama sonrası netleştirme, skor tabanı.
  - Kaldırıldılar (2026-11-03…06): `b34efc1`, `e23525e`, `3f4ad00`, `a6d3e03`. K7
    varsayılanda kapatıldı.
  - Bu repoda hiç yok (0001: belgeye özel kural yok).
- **Neden:**
  - Kurallar, 7B modelinin sormak yerine tahmin etmesi yüzünden eklenmişti.
  - Şema C kurallar kapalıyken de tabana yetişti.
  - K7 ölçümü (62 soru × 3 durum, `okuma_nihai_ara_2026-11-06.md` §14): K7 kapatılınca
    değer farklı netleştirme 12/15'ten 13/15'e çıktı, "bulunamadı" 17/18'den 18/18'e
    çıktı, değer aynı soruda 10/13'ten 8/13'e indi. Doğrulanmış yanlış her durumda 0.
  - Belge skoruna göre netleştirme yöntemi olumsuz sonuç verdi (10/5/0'dan 7/8/2'ye;
    `PILOT-RAPORU` §7).
- **Yeniden düşünülür:** Yalnız alandan bağımsız bir kural olarak.

### Netleştirmeyi model önerir; aynı cevabı veren adaylar sorulmaz
- **Ne zaman:** `#4d6b971` (PR #13).
- **Neden:** Model birden çok belge arasında netleştirme isterse, en üstteki adayla bir
  kez daha cevap istenir. Her alıntı (en az 3 kelime) diğer adaylarda da birebir geçiyorsa
  cevap verilir. Düğmeler yalnız 2–4 aday belgede gösterilir. Ölçüm: seed 7 ve 11'de
  37/40, yanlış 0, önce ve sonra aynı.
- **Bilinen kalan:** Aynı adımı farklı menü yoluyla anlatan adaylar (açık notlar).

### Selam, envanter ve bekleme cümleleri sabit metin; modele gitmez
- **Ne zaman:** `#607714a`, `#de50e4c`, `#0791a80`, `#4d6b971`.
- **Neden:**
  - Gecikme yok ve ses önceden hazır.
  - Envanter 4'ten çok belge listelemez. Önceden soruya bakmadan "377 belge… Hangisini
    soruyorsunuz?" diyordu.

### Niyet sınıflandırıcı: selam, envanter ya da belge sorusu (yardımcı model)
- **Ne zaman:** `#607714a`, `#2ad898d` (`generation/intent.py`; sınır 1,5 sn).
- **Ne yapıyor:** Mesajın selam, hal hatır, teşekkür, veda, "soracağım" gibi bir giriş,
  envanter sorusu ya da belge sorusu olduğunu ayırıyor.
- **Neden:**
  - Commit mesajlarında yazan gerekçe: sabit cevaplar aramaya ve modele gitmeden, gecikmesiz
    verilsin; ses önceden hazır olsun.
  - Ölçümü yok.
- **Not:** Eski pilotun önerdiği "soru niyeti" sınıflandırması (makine ayarı / ürün
  gereksinimi / arıza / hata kodu; `PILOT-RAPORU` §8) bu değil. O hiç yapılmadı.

### Sohbet bağlamı ve takip soruları
- **Ne zaman:** `#fcab57c`, `#c41089d`, `#350c4c2`.
- **Ne yapılıyor:**
  - Takip sorusu önceki soruyla tamamlanıyor (yardımcı model, `generation/rewrite.py`).
  - Önceki cevap kaynak sayılmıyor.
  - Kullanıcının söylemediği kod, sayı ya da beden tamamlanmış soruya girerse soru geri
    soruluyor.
  - Takip sorusu son doğrulanmış cevabın belgesinde aranıyor. Yeni söylenen kod bu kapsamı
    kaldırıyor.
  - Bağlamın belgeleri silindiyse hangi belge olduğu soruluyor.
- **Neden:** Commit mesajlarında davranış yazılı; ölçülmüş bir gerekçe yok.
- **Bilinen kalan:** Model değişince önceki beden düşüyor (`dikim-sohbet-1-t4`, 10 tekrarın
  hiçbirinde geçmedi; açık notlar).

### Gizlenen cevabın turunda da kullanıcının sorusu bağlama girer (değiştirildi)
- **Ne zaman:** 2026-11-12, `sohbet-baglami` dalı, `ask/context.py` (`next_context`).
- **Kural:**
  - Takip sorusu kullanıcının önceki sorularından tamamlanır.
  - Gizlenen ya da doğrulanmamış cevap bağlama girmez. Cevabın kendisi zaten hiç girmiyor;
    belgeler yalnız doğrulanmış cümlelerin kaynaklarından gelir.
  - Cevap gizlense de kullanıcının o turdaki (tamamlanmış) sorusu bağlama girer. Belgeler o
    turda gerçekten aranan belgelerdir: tur yeni bir kodla bütün belgelerde arandıysa kapsam
    boştur.
  - Önce, tümü gizlenen cevapta bağlam bir önceki turda kalıyordu.
  - **Düzeltme (`kapsam-mesaji` dalı, 2026-11-12):** İlk sürümde gizlenen turda belgeler
    önceki bağlamdan kalıyordu. Ürün sahibinin denemesinde şu oldu:
    - "PNT-1126 M beden iç paça kaç?" ve ardından "PNT-1162 S beden bel kaç?" (cevap
      gizlendi, ama tüm belgelerde arandı).
    - "peki l beden?" sorusu PNT-1126'nın belgesine (dikim-excel) sınırlandı.
    - Sonuç "PNT-1162 belgelerde geçmiyor" oldu; kod aslında dikim-pdf'te var.
  - **Mesaj kuralı:**
    - "X belgelerde geçmiyor" yalnız kod hiçbir görünür belgede yoksa çıkar.
    - Kapsam önceki sohbetten miras alındıysa ve kod başka belgede varsa sebep metni boş
      kalır. Arayüz "Bu bilgi bu belgede yok" der ve "Tüm belgelerde ara" düğmesini gösterir.
    - Kullanıcı belge seçtiyse ve kod başka belgede varsa "seçilen belgelerde geçmiyor"
      çıkar.
- **Neden:** Sadakat turu ölçümünde (`main`, PR #24) `dikim-sohbet-2` sohbetinde şu oldu:
  - "S beden bel?" sorusunun ardından "L beden?" sorusunun cevabı birim kuralıyla gizlendi.
  - Bağlam S bedende kaldı. "Etiketi ne?" sorusu "S beden etiketi" diye tamamlandı.
  - Kullanıcı L bedeni sorarken S bedenin etiketi doğrulanmış gösterildi (seed 7,
    doğrulanmış yanlış 1).
- **Ölçüm** (bugünkü `main` üzerine; doğrulama ve istem değişmediği için ilk turlar
  önbellekten):
  - `dikim-sohbet-2-t3` iki sette de L bedenle tamamlandı ve doğru.
  - Doğrulanmış yanlış 0.
  - `main`e göre kötüleşen soru yok; iyileşen takip sorusu seed 7'de 1, seed 11'de 3.
- **Yeniden düşünülür:** Gizlenen turun sorusu yanlış tamamlanmışsa, sonraki tur bu yanlışı
  taşır. Böyle bir durum görülürse yeniden ele alınır.

### Gerekçesiz "bulunamadı"da en yakın başlıklar gösterilir
- **Ne zaman:** `#0e60352` (PR #14), `ask/related.py`.
- **Ne yapılıyor:** Aramada en yakın çıkan en fazla 4 başlık (bölüm ya da belge adı)
  gösteriliyor; parça içeriği aktarılmıyor.
- **Neden:** Commit mesajında davranış yazılı. Ayrı ölçümü yok; aynı commit'in ölçümü (seed 7
  ve 11 37/40, yanlış 0) istem değişikliğiyle birlikte alındı.

### Kapsam: ilk sürüm yalnız yazılı cevap verir; görsel gösterme ve şekil yorumlama yok
- **Ne zaman:** Ekip kararı, 2026-11-12.
- **Karar:**
  - Görsel göstermek ve şekil yorumlamak ilk sürümün kapsamı dışında. Ürün hedefinde
    ("gerektiğinde görsel gösterme") var, ama v2'de yok.
  - Pilottaki şekil açıklaması modeli taşınmadı; nedeni bilinmiyor (aşağıda).
  - Tasarım, pilot biriminin belgeleri görülünce sıfırdan yapılacak.
- **Beklenen davranış:** Şekildeki bilgi sorulursa cevap "bulunamadı" olur ya da yalnız
  metinde yazan söylenir. Değer uydurulmaz.
- **Yeniden düşünülür:** Pilot biriminin belgeleri görülünce.

### Şekil açıklaması modeli taşınmadı
- **Ne zaman:** Eski pilotta görselden şekil açıklaması bir VLM ile üretiliyordu
  (qwen2.5vl:3b, `figures.py`). Bu repoya taşınmadı.
- **Neden:** Neden bilinmiyor.
- **Durum:** Alanı dolduran kod yoktu. İstemin 10. kuralı, `PromptSource` ve `Element`
  içindeki `generated` alanı, doğrulamadaki ilgili dal ve `Chunk.generated` tanımı kaldırıldı
  (`#676e9e0`, `#301b76a`, PR #24).
  - Kayıtlı parçalar ve indeks bu alanı taşısa da model onu yok sayıyor.
  - Veri değişmedi; indeks yeniden işlenmedi.

## Altyapı

### Postgres yerine SQLite (değiştirildi)
- **Ne zaman:** Bu repo Postgres ile başladı (`#80037b2`). `#2fd96e8` ile SQLite'a geçildi
  (0003).
- **Neden:**
  - Bu bilgisayarda yönetici yetkisi yok; Postgres hizmet olarak kurulamıyor.
  - Yük küçük.
  - Sunucuda da aynı kod çalışsın diye orada da SQLite kullanılıyor.
- **Yeniden düşünülür:** Yük büyürse ya da sunucuda çok işçi gerekirse. Yalnız
  `catalog/repository.py` değişir.

### Qdrant: yerelde gömülü klasör, sunucuda servis; yerelde tek süreç
- **Ne zaman:** `#8a9b388`, `#39fa785` (0003).
- **Neden:**
  - Gömülü klasör tek sürece kilitleniyor.
  - Embedding modeli (~2,3 GB) tek süreçte bir kez yükleniyor.
  - Eski pilotta Qdrant sunucu kipi arama gecikmesini p50 306 ms'den 13 ms'ye indirmişti
    (B2, `9140f79`). Eski PRD üretimde sunucu kipini seçmişti.
- **Bedeli:** Belge işlenirken cevaplar yavaşlayabilir.
- **Yeniden düşünülür:** Sunucu kurulumunda ya da arama gecikmesi sorun olursa.

### Bağımlılık temizliği; httpx2 geri eklendi
- **Ne zaman:** `#e048dde` (PR #20, 2026-11-12); geri ekleme `httpx-dev` dalı (2026-11-12).
- **Ne yapıldı (PR #20):**
  - `httpx2` dev bağımlılığı "hiçbir dosya import etmiyor" diye kaldırıldı.
  - Ana bağımlılıklarda olan `pillow` ve `pypdfium2`'nin `ingest` ve `dev` gruplarındaki
    tekrarları kaldırıldı.
  - Yalnız testte kullanılan üç işlev silindi.
- **Hata:** "Doğrudan import edilmiyor" kontrolü dolaylı kullanımı kaçırdı.
  - FastAPI ve Starlette'in test istemcisi `httpx2`'yi kendisi kullanıyor.
  - Paket kaldırılınca testler `StarletteDeprecationWarning` vermeye başladı.
  - `httpx2>=2.16.0` dev bağımlılığı olarak geri eklendi (ekip onayıyla). Uyarı gitti,
    testler geçiyor.
- **Ders:** Bir bağımlılık kaldırılmadan önce kod içi import araması yetmez. Paketi kaldırıp
  testleri uyarılarla birlikte çalıştırmak ve kilitteki dolaylı kullanımına bakmak gerekir.

### Docker paketi sunucu için kalır; denenmedi
- **Ne zaman:** 0003.
- **Neden:** Bu bilgisayarda Docker yok. Paketi yalnız CI'daki `services` işi sınıyor.
- **Not:** nginx'teki güvenlik başlıkları ve hız sınırı yerelde yok (açık notlar).

## Ses

### Yazıya çevirme: elevenlabs/scribe-v2 (bulut)
- **Ne zaman:** 0002. Eski pilotta faster-whisper small, yerel CPU kullanılıyordu (4,1 sn;
  turbo 13,8 sn, 5 cümle).
- **Neden:** 5 sentetik cümlede "M beden"i doğru duyan tek aday.
- **Yeniden düşünülür:** Gerçek konuşmacı ve atölye gürültüsüyle ölçülünce (açık notlar).

### Seslendirme: google/gemini-3.8-flash-lite-tts
- **Ne zaman:** İlk ses `#c5313b3`; `#b264b64` ile Gemini varsayılan oldu (0002). Eski pilotta Chatterbox vardı: CPU'da cümle başına
  12 sn – 1 dk, kabul edilemez bulundu (`SIMPLIFY.md`).
- **Neden:** Kullanıcı dinleyerek seçti. ElevenLabs daha hızlıydı ama daha az anlaşılır
  bulundu.
- **Not:** Ses saklanmaz. Ses yalnız sabit cümlelerden ve doğrulanmış cümlelerden
  üretilir.

## Ölçüm

### Geçerli taban bu bilgisayarda; 0002 sayıları yalnız referans
- **Ne zaman:** `#b06ea63` (0004).
- **Neden:** 0002'deki 35 soruluk ölçüm yeniden üretilemiyor. `--seed 7` bugün 40 soru
  üretiyor ve eski sonuçlar saklanmamış. Taban: seed 7 ve seed 11'in her ikisinde 37/40,
  doğrulanmış yanlış 0.

### Atlanan netleştirme, doğrulanmış yanlıştan ayrı sayılır
- **Ne zaman:** `#95e1870`.
- **Neden:** Bütün değerleri kaynağıyla veren cevap tahmin değildir. Kısmi, kaynaksız ya da
  yabancı değer içeren cevap doğrulanmış yanlış sayılmaya devam eder.

### Ölçüm uygulamanın kendi kodunu kullanır; cevap önbelleği yalnız ölçümde
- **Ne zaman:** `#df44663` (önbellek), `#2d54507` (birleştirme, PR #5).
- **Neden:**
  - Beş tekrar eden kod tek yere indi.
  - Önbellekten ölçüm: 98 soruda cevaplar ve kaynaklar birleştirme öncesiyle birebir aynı.
  - Aynı istek ikinci kez gönderilmez.

### Ölçümde indeks yalnız parçalar değişince yeniden kurulur
- **Ne zaman:** `#2d54507` (`evals/index_cache.py`).
- **Neden:** Parçalar `chunks.json`'da saklanıyor. Vektörler parça kimliği ve vektörlenen
  metnin parmak iziyle işaretleniyor; parmak izi aynıysa yeniden vektörlenmiyor.

### Örnek belgeler repoda; vektör önbelleği değil
- **Ne zaman:** `#0aa7595` (PR #11).
- **Neden:**
  - set7 belgeleri aynı komutla birebir üretilemiyor (docx, xlsx ve tarama her seferinde
    farklı bayt).
  - Gömülü Qdrant klasörü (22 MB) 20 MB sınırını aşıyor.

## Karar belgeleri 0001–0004

Eskiden `docs/decisions/` altındaki dört belgenin tam metni. Yukarıdaki maddelerde "0001"–"0004" diye anılan belgeler bunlar.

<a id="karar-0001"></a>

### 0001: Yeni sürümün temel kararları

Tarih: 2026-11-08

Bu repo, eski `visual_agent` pilotunun yerine temiz yapıyla yazılan sürümdür. Eski repo olduğu gibi durur; kod ve ölçüm sonuçları oradan okunabilir.

| Konu | Karar |
| --- | --- |
| Kapsam | Herkesin önceden yüklenmiş belgelere soru sorduğu genel araç |
| İlk kullanım | Önce SQL aracı kullanan uzmanlar ve iş analistleri, sonra dikim departmanı |
| Arayüz | Tablet ve bilgisayara uyumlu web |
| Giriş | İlk sürümde kapalı; Microsoft girişi ve departmanlar sonra eklenir |
| Cevap modeli | OpenRouter üzerinden, ZDR zorunlu, 8 kaynak. Başlangıç Gemma 4 26B; seçim yeni test setinde verimlilik ve maliyete göre yapılır |
| Arama | Yerel bge-m3, BM25, RRF; reranker yok |
| Kurallar | Yalnız her belgede geçerli ana kurallar; belgeye özel elle yazılmış kural yok |
| Doğrulama | Sayı, kod ve teknik ad, cümlenin kendi alıntısında birebir geçer |
| Komutlar | Belgedeki komut aynen gösterilir; sistem yerleştirmez, değiştirmez, çalıştırmaz |
| Ses | Anlık işlenir, saklanmaz; sağlayıcıda veri saklamama aranır |
| Test belgeleri | Gerçekleri baştan bilinen, kontrollü üretilmiş belgeler |
| PDF işleme | Docling ve pypdfium2; AGPL lisanslı PyMuPDF kullanılmaz |
| Ağır araçlar | LibreOffice, Tesseract ve Docling yalnız işçi imajında; belgeler internetsiz işlenir |
| OCR güvenliği | İki okumada uyuşmayan değer belirsiz işaretlenir ve doğrulanmış gösterilmez |

<a id="karar-0002"></a>

### 0002: Ölçümle verilen kararlar

Tarih: 2026-11-09. Ölçümler üretilmiş test setiyle yapıldı. Gerçek belgelerle yeniden denenecek konular [açık notlarda](acik-notlar.md).

#### Cevap modeli: `google/gemma-4-26b-a4b-it`

Yalnız veri saklamayan uçlar denendi. Geliştirme setinin 35 sorusu; süre cevabın tamamıdır.

| Model | Geçen | Yanlış değer | Ortanca süre | Maliyet (35 soru) |
| --- | --- | --- | --- | --- |
| Gemma 4 26B | 33 | 0 | 1,57 sn | 0,0068 $ |
| Qwen 3.6 35B | 31 | 0 | 3,14 sn | 0,0026 $ |
| DeepSeek V4.1 Flash | 31 | 1 | 1,05 sn | 0,0200 $ |
| Claude Haiku 5.5 | 31 | 1 | 1,20 sn | 0,0184 $ |
| Mistral Small 3.2 | 30 | 2 | 1,11 sn | 0,0050 $ |
| Qwen 3.8 27B | 27 | 1 | 0,68 sn | 0,0311 $ |
| Gemma 4 31B | 25 | 1 | 0,91 sn | 0,0144 $ |

Önce yanlış değer, sonra doğruluk, süre ve maliyet ölçüt alındı. İstem Gemma üzerinde ayarlandığı için karşılaştırma ona biraz avantaj sağlar. GPT-OSS 120B ve GLM 5.3 Flash isteklere cevap vermediği için ölçülemedi; Gemini 3.1 Flash Lite istemcinin ZDR denetiminden geçmedi.

#### Son sınav

Hiç işlenmemiş yeni tohumlu set (`--seed 11`), sonucuna göre ayar yapılmadı: 40 sorudan 37'si geçti, doğrulanmış yanlış değer 0, gereksiz ret 1. Geçmeyenler: taranmış belgede etiket sorusu "bulunamadı" oldu, fotoğraftaki değer doğrulanamadı, model değişince beden yeniden soruldu.

İlk İK sorularını içeren eski set bütün ayar koşularında çalıştığı için görülmemiş sayılmadı.

#### Tablo varyant denetimi (K9): eklenmedi

Son sınav dahil doğrulanmış yanlış değer çıkmadı. Eklenecek denetim gereksiz soru riski taşıyor. Gerçek tablolarda yanlış satır ya da sütun görülürse yeniden ele alınacak.

#### Konuşma

- Yazıya çevirme: `elevenlabs/scribe-v2`. Beş sentetik cümlede `M beden`i doğru duyan tek aday.
- Seslendirme: `google/gemini-3.8-flash-lite-tts`. Kullanıcı dinleyerek seçti; ElevenLabs daha hızlı ama anlaşılırlığı daha düşük bulundu.
- Selamlaşma, envanter ve bekleme cümleleri sabit metindir; ses yalnız bunlar ve doğrulanan cümlelerden üretilir.

<a id="karar-0003"></a>

### 0003: Docker'sız yerel kurulum, SQLite ve tek süreç

Tarih: 2026-11-10

Pilot, Docker kurulamayan ve yönetici yetkisi olmayan bir Windows bilgisayarda çalışacak. Bu yüzden ana yol yerel kurulum oldu; Docker paketi sunucu için kalıyor.

| Konu | Karar |
| --- | --- |
| Ana kurulum | Yerel, Docker'sız, yönetici yetkisi olmadan, tek komut (`baslat.bat`) |
| Veritabanı | Postgres yerine SQLite; yerelde ve sunucuda aynı kod |
| Süreç | Yerelde API, belge işçisi ve arayüz tek süreçte |
| Arama dizini | Qdrant yerelde gömülü klasör, sunucuda ayrı servis |
| Dış araçlar | Tesseract ve LibreOffice kullanıcı klasöründe; PATH'ten ya da ayarla bulunur, eksikse yalnız ilgili belge türü durur |
| Sunucu | Docker paketi kalır; bu bilgisayarda denenemez, CI açılışı sınar |

#### Neden SQLite

- Postgres yönetici yetkisi olmadan bir hizmet olarak kurulamıyor; taşınabilir sürümü de ayrı bir süreç ve bakım demek. SQLite Python'un içinde geliyor, yeni bağımlılık gerekmedi.
- Yük küçük: birkaç yüz belge, onlarca kullanıcı. Yazmalar seyrek (yükleme, işleme sonucu); okumalar kısa.
- İki kod yolu olmasın diye sunucuda da SQLite kullanılıyor. Depo protokolleri (`Repository`, `JobRepository`, `SnapshotSource`) değişmedi; ileride Postgres'e dönmek gerekirse yalnız `catalog/repository.py` değişir.
- API ve işçi ayrı süreç olabildiği için dosya WAL kipinde açılıyor ve kilitte 30 sn bekleniyor. Kuyruktan iş alma tek `UPDATE ... RETURNING` cümlesi olduğu için iki işçi aynı belgeyi alamıyor; bu, aynı dosyayı açan iki bağlantıyla test ediliyor.

#### Neden tek süreç

- Gömülü Qdrant klasörü tek sürece kilitleniyor. Ayrı bir işçi süreci için Qdrant sunucusu gerekirdi; Windows ikilisi yönetici istemeden çalışır, ama ikinci bir süreci açık tutmak ve izlemek gerekirdi.
- Arama ve indeksleme aynı embedding modelini (bge-m3, ~2,3 GB bellek) kullanıyor. Tek süreçte model bir kez yükleniyor.
- Bedeli: belge işlenirken (Docling, OCR) aynı işlemci cevaplarla paylaşılıyor, o sırada cevaplar yavaşlayabilir. Pilotun kullanımında belge yükleme seyrek olduğu için kabul edildi. Kapatırken süren belge işi bir sonraki açılışta baştan alınıyor.

#### Sunucuda ne değişir

- `compose.yaml` içinde postgres servisi yok. API ve işçi ayrı konteyner, aynı SQLite birimini (`/data/db`) paylaşıyor; işçi API'nin içinde çalışmıyor (`VA_WORKER_IN_PROCESS=false`).
- Qdrant ayrı servis olarak kalıyor (`VA_QDRANT_URL`); ayrı işçi gömülü klasörle açılmayı reddediyor.
- Arayüzü nginx sunuyor; güvenlik başlıkları ve hız sınırı yalnız orada. Yerelde bunlar yok ([açık notlar](acik-notlar.md), "Yayına almadan önce").
- Docling modelleri sunucuda `docling-tools` komutuyla birime iniyor; yerelde ilk belgede kendiliğinden iniyor.
- Paket bu bilgisayarda denenemedi. Yalnız CI'daki `services` işi derleyip açılışı sınıyor.

#### Ölçüm

`evals.run_questions` yerelde kendi gömülü Qdrant klasörüyle çalışıyor. Model cevapları yalnız ölçüm için önbelleğe alınıyor; önbellekten gelen soruların süresi ve maliyeti rapora girmiyor.

Bundan sonraki karşılaştırmalar bu bilgisayarda alınan tabana göre yapılıyor. [0002](#karar-0002)'deki 33/35 ve 37/40 Docker imajındaki araç sürümleriyle ölçüldü, yalnız referans. Taban sonuçları ve sonraki ölçümler [0004](#karar-0004)'te.

<a id="karar-0004"></a>

### 0004: Yerel kurulumda ölçüm sonuçları

Tarih: 2026-11-10. Ölçümler üretilmiş test setiyle, Docker'sız yerel kurulumda ([0003](#karar-0003)) yapıldı. Soru bazındaki sonuçlar ve ölçüm bilgileri: [`evals/baselines/taban/`](../evals/baselines/taban).

#### Geçerli taban

[0002](#karar-0002)'deki sayılar (geliştirme 33/35, son sınav 37/40) Docker imajındaki araç sürümleriyle ölçüldü ve yalnız referanstır. 35 soruluk geliştirme ölçümü yeniden üretilemiyor: test üreticisi o tarihten beri değişmediği halde `--seed 7` bugün 40 soru veriyor, eski koşuların soru bazındaki sonuçları da saklanmamış. Bundan sonraki her karşılaştırma bu bilgisayardaki tabana göre yapılır.

Araçlar: Tesseract 5.4.0, LibreOffice 26.8.2, Docling 2.149.0, OCRmyPDF 17.13.0, RapidOCR 3.10.0. Cevap modeli `google/gemma-4-26b-a4b-it`. Ölçülen kod `441a394`, puanlama `95e1870`.

| Set | Geçen | Doğrulanmış yanlış değer | Atlanan netleştirme | Gereksiz ret | Maliyet (canlı sorular) |
| --- | --- | --- | --- | --- | --- |
| Geliştirme (`--seed 7`) | 37/40 | 0 | 0 | 1 | 0,0084 $ |
| Son sınav (`--seed 11`) | 37/40 | 0 | 1 | 0 | 0,0065 $ (30 soru) |

Son sınavda 10 sorunun bazı yardımcı model istekleri geliştirme koşusuyla birebir aynı olduğu için önbellekten geldi; bu soruların süre ve maliyeti özete girmedi.

Geçmeyenler:

| Soru | Belge türü | Set | Sonuç |
| --- | --- | --- | --- |
| `dikim-tarama-etiket` | tarama | geliştirme | "Bulunamadı" (gereksiz ret); 0002'de son sınavda da görülmüştü |
| `dikim-foto-olcu` | fotoğraf | ikisi de | Değer doğrulanamadı |
| `dikim-sohbet-1-t4` | metinli PDF | ikisi de | Model değişince beden düştü, beden yeniden soruldu |
| `dikim-revizyon-netlestir` | metinli PDF (iki sürüm) | son sınav | Netleştirme yerine iki sürümün değeri kaynağıyla listelendi (atlanan netleştirme) |

#### Puanlama: atlanan netleştirme ayrı sayılır

Netleştirme beklenen soruda rozetli cevap, altın verideki farklı değerlerin hepsini kaynağıyla ve başka değer olmadan veriyorsa "atlanan netleştirme" sayılır ve ayrı raporlanır; durma koşulu değildir. Değerlerin yalnız bir kısmı verildiyse (tahmin), kaynak gösterilmediyse ya da cevapta başka değer varsa "doğrulanmış yanlış değer" sayılır; bu her ölçümde 0 olmalıdır. Ayrım yalnız altın veriden yapılır. Eski sayımla son sınavdaki tek "doğrulanmış yanlış" bu soruydu; kayıtlı cevaplar modele gitmeden yeniden puanlandı.

#### Kararsız sorular

İki soru önbelleksiz 5'er kez soruldu. Adım 5 karşılaştırmasında bu sorular gerileme sayılmadan önce ayrıca incelenir.

| Soru | Geliştirme | Son sınav | Not |
| --- | --- | --- | --- |
| `dikim-revizyon-netlestir` | 5/5 | 1/5 | Geçmeyen 4 tekrarın hepsi atlanan netleştirme; doğrulanmış yanlış değer yok |
| `dikim-sohbet-1-t4` | 0/5 | 0/5 | Takip sorusu tamamlanırken beden her seferinde düşüyor |
