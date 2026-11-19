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
    Aynı model (ayar: `VA_HELPER_MODEL` / `VA_HELPER_PROVIDERS`; eski adı
    `VA_TRANSLATION_*`) takip sorusunu tamamlama ve niyet sınıflandırmasını da yapar.
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
  - Kural biçim düzeyinde. Başlık düzeyi bildirmeyen biçimlerde (PDF) bölüm kuralı
    değişmedi. Excel'de her sayfa en üst düzey başlıktır ("Excel'de her sayfa kendi
    bölümüyle başlar").
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
    artırılıyor. Excel (xlsx, xls), PDF, görsel ve Office 3'te; Markdown, metin ve SQL 2'de.
    PDF, görsel ve Office 2: OCR kalite puanında tek büyük harf çöp sayılmaz. Office da
    2'ye çıkarıldı (ürün sahibi kararı), çünkü PDF'e çevrilip aynı OCR kararından geçiyor.
    PDF, görsel ve Office 3 (2026-11-13): yeniden işleme belgenin kayıtlı dilini ("tr") OCR'a
    veriyordu, OCR yalnız `tur` ile okunuyordu; ilk yükleme ise `tur+eng`. Aynı dosya iki yolda
    farklı okunuyordu (`dikim-foto`'da tolerans `1,0` yerine `10`). Artık OCR her işlemede
    `tur+eng`; katalog dili yine parçalardan belirlenir. Sürüm yalnız sayıya baktığı için
    sürüm 2'deki bütün PDF, görsel ve Office belgeleri (ilk yüklemede zaten tur+eng ile
    okunanlar dahil) "eski kural" görünür. Office de aynı yoldan etkilendiği için (taranmış
    sayfa ve gömülü görsel OCR'ı) ürün sahibinin kararıyla 3'e çıkarıldı.
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
    - Belge işlenince dil parçalardan okunuyor; bu dil katalog içindir. Yeniden işlemede de
      OCR `tur+eng` ile yapılıyor, kayıtlı dile bağlı değil (2026-11-13, `yeniden-isleme-ocr`;
      önce tespit edilen dil kullanılıyordu ve aynı dosya iki yolda farklı okunuyordu).
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
- **Düzeltme (2026-11-13, `ocr-sayfa-kaybi`):**
  - Sorun: Kalite puanı tek büyük harfi (beden S, M, L) çöp sayıyordu. set7 `dikim-tarama`
    s.3 doğru okunduğu hâlde 0,786 aldı, eşik 0,85; sayfa uyarısız yalnız görüntü kaldı ve
    etiket satırları indekse girmedi. set11'de OCR "S"yi "Ss" okuduğu için 0,857 ile geçiyordu.
  - Değişiklik: Tek büyük harf çöp sayılmıyor. Metni indekse girmeyen sayfa belge raporunda
    uyarı oluyor. PDF ve görsel kural sürümü 2.
  - Ölçüm (n10, set7 ve set11'in PDF ve görüntüleri yeniden işlendi): Katmanı değişen tek
    sayfa set7 `dikim-tarama` s.3 (image_only → new); çöp metinli sayfa indekse girmedi.
    Taban 7 35 → 36/40 (`dikim-tarama-etiket` doğru), taban 11 37/40 ve sınır 32/32
    değişmedi; doğrulanmış yanlış 0; canlı 0,00063 $.

### SQL komutları kod bloğu olur; komut aynen gösterilir
- **Ne zaman:** 0001, `#1475acb`, `#cae391f`.
- **Neden:** Kural "sistem komutu yerleştirmez, değiştirmez, çalıştırmaz" (0001). Model
  komutu yazmaz, yalnız kaynak numarasını verir (`kod_kaynak_no`). Ölçüm yok.

### Excel'de her sayfa kendi bölümüyle başlar
- **Ne zaman:** 2026-11-13. `excel-sayfa-bolum` dalı; ürün sahibi onayı.
- **Kural:** Excel sayfa başlığı en üst düzey başlıktır; önceki sayfanın adı ve başlığı
  sonraki sayfanın bölüm yoluna girmez. Yalnız tablo biçimleri (xlsx, xls) etkilenir; Word,
  PDF ve Markdown başlıkları değişmez. Tablo biçimlerinin kural sürümü 3: önceden yüklenmiş
  Excel'ler arayüzde "eski kuralla işlendi" görünür ve yeniden işlenmelidir.
- **Neden:** Sayfa başlığının düzeyi yoktu; ikinci sayfa ilk sayfanın altına alt bölüm
  olarak giriyordu (`PNT-3101 · … · PNT-3102 · …`). Önceki sayfanın kodu sonraki sayfaların
  parçalarında da görünüyor, arama yanlış sayfanın satırını öne çekiyordu (kural 1).
- **Ölçüm** (ölçüm indeksi n10; uygulamanın indeksine dokunulmadı. Yalnız Excel belgeleri
  yeniden işlendi, değişen yalnız çok sayfalı iki
  belge: taban setlerinde `dikim-excel` 7 parça, sınır setinde `sinir-model-sayfa` 9 parça;
  işleme ve vektör birkaç saniye; canlı maliyet toplam ~0,01 $):
  - Sınır setine model başına sayfa düzeninde bir Excel ve 5 soru eklendi (kod yalnız sayfa
    adında). Sızıntı varken 1 doğrulanmış yanlış: "PNT-3102 M beden basen 96 mı?" sorusuna
    PNT-3101 sayfasının satırı getirilip 96 doğrulandı. Düzeltmeden sonra 0: doğru sayfadan
    101. `PNT-3101 S beden boy` gizliyken doğru oldu; olmayan model (PNT-3104) iki koşuda da
    "geçmiyor".
  - Taban 7 ve 11: hiçbir sorunun sonucu değişmedi (`dikim-excel` soruları dahil).
  - Tek sayfalı Excel'lerin parçaları değişmez; sürüm biçim düzeyinde olduğu için onlar da
    "eski kuralla işlendi" görünür, ama yeniden işlenmeleri zorunlu değil.
- **Sonra düzeltilen** (`sinir-olcu-adlari` dalı):
  - Yeni belge eski beden tablosuyla aynı ölçü adlarını (Bel, Basen) taşıyordu; model adı
    vermeyen eski iki sınır sorusu (`sinir-sutun-basen-m`, `sinir-sutun-bel-l-teyit`) haklı
    olarak netleştirme soruyordu. Ölçü adları Göğüs, Omuz, Kol boyu yapıldı.
  - Üreticide grup başlığı son beden sütununa (L) uzanmıyordu; iki soru doğru değeri bulup
    alıntıdaki etiket kaynakla birebir tutmadığı için gizleniyordu. Grup başlığının kapsadığı
    sütun sayısı artık açıkça veriliyor (dikim tablolarında tolerans sütunu dışarıda kalır).
  - Yalnız bu belge yeniden işlendi (9 parça, 4 sn). Sınır seti 32/32, doğrulanmış yanlış 0;
    canlı maliyet 0,0009 $ (yeni 4 soru; değişen bağlamla sorulan 12 eski soru önbellekten).

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

### Sağlayıcı sırası: Makora, yedek DeepInfra; yedeğe yalnız kesintide geçilir
- **Ne zaman:** 2026-11-19, ürün sahibi kararı. Bu repoda `settings.answer_providers`.
  Öncesi: eski pilotta Venice birinciydi; 2026-11-06'da DeepInfra, Venice, Parasail oldu.
- **Neden:**
  - Hedef, ilk doğrulanmış cümlenin p95'inin ≤ 3 sn olması. Süre ölçümünde (2026-11-18, 20 soru)
    sürenin yarısından fazlası cevap modelinin içinde geçiyordu (ilk jeton ve ilk öğenin yazımı);
    doğrulama 1 ms.
  - Sınır setinin kilitsiz 24 sorusu × 3 koşu, üç sıra dönüşümlü, aynı kod ve aynı (eski) indeks:

    | Sıra | Doğru / güvenli / yanlış | JSON hatası | Kesik | Yedeğe geçiş | İlk doğrulanmış ortanca / p95 |
    |---|---|---|---|---|---|
    | DeepInfra, Venice, Parasail | 59 / 10 / 3* | 0 | 0 | 3 (ilk jeton 2,5 sn'de gelmedi) | 3,47 / 5,97 sn |
    | Makora, DeepInfra | 59 / 10 / 3* | 0 | 0 | 0 | 2,65 / 3,61 sn |
    | NextBit, DeepInfra | 60 / 9 / 3* | 1 | 1 | 1 (boşluk kaçağı) | 3,49 / 5,07 sn |

    \* Üçü de D1: indekste `dikim-rev-a.pdf` yoktu, cevap sürümsüz tek değerdi. Sağlayıcıdan
    bağımsız; taban ölçümünde iki sürüm yüklüyken doğruydu. Doğrulanmış yanlış değer üç sırada 0.
  - Üç sağlayıcı da bu model için OpenRouter'ın ZDR listesinde (`safety_retention: false`).
    Nicemleme OpenRouter'da: Makora "unknown", DeepInfra fp8, NextBit bf16.
  - Eski gerekçe sürüyor: Venice ve Parasail'de boşluk kaçağı görülmüştü (2026-11-06: 16 ve 12,
    DeepInfra'da 0); bu yüzden yedek DeepInfra.
  - Yedeğe geçme koşulları: 2,5 sn içinde ilk token gelmezse ya da üst üste 40 boşluk
    karakteri gelirse.
- **Bilinmeyen:** Makora'nın nicemlemesi; sağlayıcı bunu bildirmeden değiştirebilir. Ölçüm tek
  gün, 72 cevap. p95 hedefin hâlâ üstünde (3,61 sn).
- **Yeniden düşünülür:** Soru kaydında (`provider_errors`) Makora hataları ya da kaçakları
  görülürse; ilk doğrulanmış cümle süresi yeniden 5 sn'ye yaklaşırsa.

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
  - Cümledeki "on", dayanakta aynı sözcüğün önündeki "on" ya da 10 ile karşılanır ("on dakika"
    ↔ "on dakika" / "10 dakika"); "10 mm ... 3 dakika" ya da "10 adet ... beş" ("on beş")
    karşılamaz. Ardında sözcük yoksa 10 aranır. Kaynaktaki "on" rakamla yazılmış 10'un kanıtı
    olamaz ("click on Save", "ON konumu"). Tamamı büyük harfli "ON" hiçbir tarafta sayı değildir.
  - "lt", "l"nin eş anlamlısı. Türkçe belgedeki "gr", cümledeki "g"yi karşılar; tersi yok ("g"
    ivme olabilir). İngilizce belgede "gr" grain olabileceği için ayrı birim kalır. Kaynakta
    birimsiz değere eklenen birim cümleyi gizler.
  - Ses yalnız Türkçe binlik biçimini ("1.234,50") değeriyle okur (999.999 üstü rakam rakam). Öteki her
    ayraç adıyla, sonrası rakam rakam okunur: "1.500" bir nokta beş sıfır sıfır, "14.30" on
    dört nokta üç sıfır, "42,5" kırk iki virgül beş. Tek harfli birim yalnız küçük harfle
    birimdir ("38 M" beden); "g" okunmaz (ivme de olabilir). Sayı ya bütün okunur ya hiç
    dokunulmaz: "1.500-2.000" bir nokta beş sıfır sıfır tire iki nokta…, "-5" eksi beş; "x1.500"
    yazıldığı gibi kalır.
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

### Docker paketi kaldırıldı (önce: sunucu için kalır; denenmedi)
- **Ne zaman:** 0003'te kaldı; 2026-11-19'da kaldırıldı (karar 0017).
- **Not:** nginx'teki güvenlik başlıkları ve hız sınırı yerelde yok (açık notlar).

### Yetki altyapısı kaldırıldı; giriş ağa açılmadan önce ayrıca ele alınacak
- **Ne zaman:** 2026-11-13, `temizlik-5a` dalı; ürün sahibi kararı.
- **Ne kalktı:** Soru, arama ve belge kaydındaki `access` alanları, Qdrant'taki yetki süzgeci,
  `VA_AUTH_ENABLED` ayarı ve `/api/health`'teki `auth_enabled` alanı.
- **Neden:** Hiçbir istek yetki grubu vermiyordu ve her belge "all" olarak yazılıyordu; süzgeç
  hiç çalışmıyordu. "İleride lazım olur" diye bırakılan koddu. Eski `VA_AUTH_ENABLED=true`
  artık uygulamayı durdurmuyor, yok sayılıyor.
- **Veri:** Qdrant'taki mevcut parçaların `access` alanı ve eski SQLite dosyalarındaki
  `access` sütunu yerinde kaldı (yeniden indeksleme ve göç yok); kod artık okumuyor. Yeni
  parçalar ve yeni veritabanları bu alanı taşımıyor.
- **Sonra:** Giriş ve departman bazlı yetki, arayüz ağa açılmadan önce ayrıca tasarlanacak
  (açık notlar, "Yayına almadan önce").

## Arayüz

### Tek açık tema; koyu tema kaldırıldı
- **Ne zaman:** 2026-11-13, `arayuz-stil` dalı; ürün sahibi kararı.
- **Ne:** Yeni tasarım tek açık temada (açık gri zemin, beyaz kartlar, cam efekti yalnız
  çekmecelerde). İşletim sisteminin koyu tema tercihine uyan renkler silindi.
- **Neden:** Yeni tasarım tek temada sade kalsın; atölyede açık tema daha okunur.
- **Geri eklemek için:** Yeni bir gerekçe gerekir (ör. gece vardiyasında ölçülmüş bir okuma
  sorunu).

### Çalışma alanı düzeni; lacivert, mercan, krem görünüm
- **Ne zaman:** 2026-11-16, `arayuz-calisma-alani` dalı; ürün sahibi isteği ve gönderdiği örnek
  görsel. "Tek açık tema" kararının yerini alır: zemin lacivert, cevap ve kaynak krem/beyaz
  yüzeyde (koyu zemin üstünde açık kart; ayrı bir açık tema yok).
- **Ne:** 1080 px ve üstünde belgeler solda, kaynak sağda sabit panel; sohbet ortada kullanılır
  kalır (karartma yok), belgeler paneli açık başlar. Dar ekranda eskisi gibi çekmece. Açılışta
  bento karolar (büyük mercan "Sesli sor", krem "Yazarak sor", beyaz "Belge ekle"); konuşma
  modunda ses düzeyiyle büyüyen küre.
- **Nasıl:** `App.css`, `App.tsx`'te açılış durumu, `LandingActions.tsx`'te karo sınıfı ve ok
  simgesi. Metinler ve erişilebilirlik adları değişmedi. Harici yazı tipi yok.
- **Denenmedi:** atölye ışığında koyu zeminin okunurluğu; konuşma modu yalnız stil olarak
  değişti, mikrofonla denenmedi.

### İnternetsiz açılış: VA_MODELS_OFFLINE; BM25 önbelleği kalıcı klasörde
- **Ne zaman:** 2026-11-13, `cevrimdisi-acilis` dalı; ürün sahibi isteği (fabrika ağında
  internet olmayabilir).
- **Ne:** Ayar açıkken `apps.local`, Hugging Face kütüphaneleri yüklenmeden önce
  `HF_HUB_OFFLINE` ve `TRANSFORMERS_OFFLINE` koyar; bge-m3, BM25 ve Docling modellerinin
  önbellekte olmadığını görürse ne eksik olduğunu söyleyip durur. Varsayılan kapalı: ilk
  kurulum modelleri indirir.
- **Kontrol neden klasör düzeyinde:** `snapshot_download(local_files_only=True)` yanlış
  "eksik" dedi: fastembed modelin yalnız gereken dosyalarını indiriyor, Docling sabit bir
  sürüm (`v2.3.0`) kullanıyor. Bedeli: Docling sabit sürümü değiştirirse açılış kontrolü
  geçer, hata ilk belgede çıkar (Docling model adlarını kurulu sürümle eşleştiren test var).
- **BM25 önbelleği:** `%TEMP%astembed_cache` yerine `data/models/fastembed`; geçici klasör
  temizlenince model internetten yeniden inmek zorunda kalıyordu. Mevcut önbellek bu
  bilgisayarda yeni yere kopyalandı.
- **Sınırı:** Cevap modeli bulutta (OpenRouter); internetsiz ağda uygulama açılır ama soru
  cevaplanamaz.

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

### Ölçüm indeksi n10: belgeler uygulamayla aynı yoldan işlenir (OCR tur+eng)
- **Ne zaman:** 2026-11-13. `olcum-uygulama` dalı (inceleme listesi #3, #20, #21).
- **Karar:**
  - Ölçüm betikleri belgeyi uygulamadaki gibi dili bilinmeden (`UNDETECTED_LANGUAGE`)
    işler; ilk OCR `tur+eng`. Katalog dili yine parçalardan okunur.
  - Geçerli ölçüm klasörleri: `evals/output/n10/w7`, `n10/w11` (taban setleri), `n10/wfr`
    (FastReact). Altın setler `run_questions --offline` ile önbellekten ölçülür; önbellekte
    olmayan soru "miss" olur, canlı sayılmaz.
  - Bu tarihten önceki ölçümlerin sayıları n10 ile doğrudan karşılaştırılamaz: taranmış
    belge ve fotoğrafın parçaları farklı.
- **Neden:** Kararlar'daki "Ölçüm uygulamanın kendi kodunu kullanır" maddesi OCR'da
  tutmuyordu: `run_questions` dili altın metinden seçip tek dille, `run_documents` ve
  `ingest_check` varsayılan "tr" ile OCR yapıyordu.
- **Yeniden üretim:** Yalnız `dikim-tarama` ve `dikim-foto` parçaları değişti (iki sette de).
  İşleme 3 dk 24 sn ve 3 dk 3 sn, vektörler 27 sn ve 22 sn. FastReact parçaları birebir aynı
  (3648, hepsi `.md`, OCR yok); vektör yeniden üretilmedi.
- **Ölçüm** (önce: n9, aynı kod; sonra: n10):
  - Geçen soru seed 7'de 34 → 35, seed 11'de 35 → 37. Doğrulanmış yanlış 0 → 0. Seed
    11'de `dikim-foto-olcu`'yu canlıda ilk sağlayıcı cevaplamadı, yedek sağlayıcı cevapladı;
    çevrimdışı koşu önce ilk sağlayıcıyı denediği için bu soru "miss" sayılır ve özette
    puana girmez (çevrimdışı özet 36/39). Canlı sonucu doğru.
  - Değişen 3 soru, üçü de gizlenmişken doğru oldu: seed 7 `dikim-foto-olcu`, seed 11
    `dikim-tarama-olcu` ve `dikim-foto-olcu`.
  - Önbellekte olmayan 14 soru bir kez canlı soruldu (0,0026 $). FastReact'ta değişen
    soru yok.
- **Eski klasörler:** n3–n9, run7-taban, run11-taban ve fastreact karşılaştırma için
  kalıyor. `evals/output/` `.gitignore`'da; repoda izlenen dosyası yok.

## Karar belgeleri 0001–0010

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

<a id="karar-0005"></a>

### 0005: Taranmış tablo hücreleri iki okumayla doğrulanır (görüntü modeli)

Tarih: 2026-11-14. Dal: `tablo-hucre-okuma`. Kural sürümü PDF, Office ve görsel için 3 → 4.

**Sorun.** Taranmış ölçü föylerinde (tech pack) üst üste dizilmiş kesirler (½, ¼, ⅞) Tesseract'ta hiç okunmuyor ("27 ½" → "27 a", "26 ½" → "2%"), kodlarda 0 harf O okunuyor ("BW005" → "BWOO5"). Kesirli değerler gizleniyor, kodlar "belgelerde geçmiyor" deniyor; bazı yanlış okumalar ("17" → "7") işaretlenmeden geçiyordu.

**Ölçüm (tek seferlik betikler scratchpad'de).** Doğru değerler sayfa görüntüsüyle tek tek kontrol edildi.

| Okuyucu | 627 hücrede doğru | 424 kesirli hücrede doğru | Hücre başına |
| --- | --- | --- | --- |
| Tesseract (s.24, 121 hücre) | 41/121 | 0/78 | – |
| RapidOCR (yerel) | 393 | 190 | ücretsiz |
| `qwen/qwen3-vl-30b-a3b-instruct` (ZDR) | 627 | 424 | ~0,00003 $ |
| `google/gemini-3.1-flash-lite` (ZDR) | 625 | 424 | ~0,0003 $ |

İki okuyucunun uyuştuğu hücrelerde yanlış değer: RapidOCR + Qwen 396 hücrede 0, Qwen + Gemini 625 hücrede 0. Sayfalar: 6013448 s.24, 25, 28 (fark sayfası) ve 6026418 s.11. Tika incelendi: OCR için Tesseract'ı ya da dışarıdaki bir VLM'i çağırıyor, ek kazanç yok.

**Karar.** OCR'lı sayfalardaki kısa, tek sütunluk gövde hücreleri docling'in hücre kutusundan yeniden okunur. RapidOCR ile Qwen uyuşursa değer kesinleşir; uyuşmazsa Gemini hakemdir, Qwen'le uyuşursa kesinleşir. Kesinleşmeyen hücrenin sayıları belirsiz sayılır (cevapta gizlenir). Birden çok değer içeren okuma ("1 1") ve birleşik hücre kesinleşmez. Yeniden okunmayan hücrelerde sayfanın iki okuma karşılaştırması sürer. Buluta yalnız hücre görüntüsü gider (ZDR, `data_collection: deny`). Okumalar görüntü özetiyle `VA_CELL_READER_CACHE`'te saklanır; yeniden işleme aynı hücre için istek atmaz. Belge başına sınır `VA_CELL_READER_MAX_CELLS` (3000; 0 kapatır). API anahtarı yoksa eski davranış.

**Sonuç (6013448, ayrı ölçüm indeksi).** Belirsiz değer 397 → 44. 11 tech pack sorusunda: XL göğüs (26 ½) ve SL055 MD (25 ½) artık doğru ve gösteriliyor; Sepia etiket rengi doğru ("White: Black" yerine "Black"); BW005, BL005, SL055, SL095 artık bulunuyor. Doğrulanmış yanlış değer 0. İşleme süresi 97 sn → ilk işlemede 420 sn (hücre okuma), önbellekle ~200 sn. Hücre okuma maliyeti bu belge (29 sayfa) için ~0,15 $.

**Geliştirme seti (`--seed 7`).** 37/40, doğrulanmış yanlış değer 0, gereksiz ret 0 (taban 37/40, 1 gereksiz ret). `direct` 9/9 ve `in_image` 3/3 (taban 8/9, 2/3). `dikim-pdf-olcu` ve `dikim-pdf-yanlis-onay` bu koşuda geçmedi: kaynak metin katmanlı `dikim-pdf` (bu değişiklik dokunmuyor); model cümleye alıntıda olmayan "cm" ekledi, birim kuralı gizledi. Tekrar ölçülmedi.

**Açık kalanlar** [açık notlarda](acik-notlar.md): değer/fark sayfası bağlamı, kodun alıntıda geçmemesi, docling'in kaçırdığı hücreler, kapak sayfası form düzeni, s.5 satır kaybı.

<a id="karar-0006"></a>

### 0006: Taranmış çizgili tablolar çizgilerinden okunur; fark tabloları değer kaynağı değildir

Tarih: 2026-11-15. Dal: `tablo-hizalama`. Kural sürümü PDF, Office ve görsel için 6.

**Sorun.** Docling taranmış tablolarda sütunları kaydırıyordu: 17 tech pack'teki 653 ölçü satırının 72'sinde değer yanlış bedenin altındaydı (kural 1). OCR metin katmanı komşu sütunların yazısını da birleştiriyordu.

**Karar.**
- OCR'lı sayfadaki çizgili tablo, çizgilerinden okunur: kesintisiz ince çizgiler ve gri zeminin kenarları sınırdır; satırda dikey çizgi yoksa hücreler birleşir; ilk dolu satır başlıktır; çoğu boş satır bölüm etiketi ya da nottur. Her hücre iki okumayla (RapidOCR + Qwen, ayrılırlarsa Gemini hakem) okunur. Uzun metinde iki okumada da aynen geçen sayı kesindir; kısa hücre bütün olarak kesinleşmelidir. Kesinleşmeyen hücrede iki okumadan uzun olanı tutulur (model çok satırlı hücrenin ilk satırını atlayabiliyor).
- Yazıyı kesen ızgara (yazı hücre kenarına değiyor) ya da çizgi bulunamayan tablo docling'in yapısıyla okunur. Docling kutusundan kesitler OCR'lı görüntüden alınır, ızgara özgün görüntüden (0007'den önce OCR eğikliği düzeltiyordu; ayrım korunur).
- Tablo notunda fark ifadesi ("Increment", "Delta", "fark") geçen tablo satırı, soru farkı sormuyorsa cevap kaynağı olmaz. Yalnız tablo notuna bakılır (parçada ayrı alan): "Incremental Updates" gibi bir başlığın altındaki metin fark değildir (2026-11-15 düzeltmesi; ilk sürüm bölüm adının tamamına bakıyordu ve yazılım belgelerinde 11 parçayı gizleyebiliyordu). Ekip kararı (2026-11-15): model fark değerini ölçü diye veriyordu ve alıntı birebir olduğu için doğrulama yakalayamıyordu.

**Ölçüm.** 6013448: belirsiz değer 397 → 16 (ayrı ölçüm indeksi, `evals.run_documents`; kayıt: `evals/output/techpack-6013448/ingest.json` ve `evals/output/techpack-6013448-izgara/ingest.json`, `uncertain_values`; klasör repoda değil); doğrulanmış yanlış değer 0 (çizgi okuması fark sayfasını temiz okuyunca iki yanlış doğrulama görülmüştü, fark kuralıyla kalktı). 6026411 s.14 kaymasız. Geliştirme seti 38/40, doğrulanmış yanlış 0. İlk işlemede tech pack başına hücre okuma ~0,2 $.

**Açık.** Bazı doğru cevaplar (BW005 LG 25, SL055 MD 25 ½) gizleniyor. Kayıtlı sonuçtaki nedenler: BW005 "cümlede kendi alıntısında olmayan sayı: 25", SL055 "alıntı kaynakta birebir değil". Nedenin istemdeki 150 karakterlik alıntı sınırı olduğu **doğrulanmadı** (modelin alıntısı sonuç dosyasında saklanmıyor).

### 0007: OCR'da eğiklik düzeltme (--deskew) kaldırıldı
Tarih: 2026-11-15. Dal: `deskew-kaldir`. Kural sürümü PDF, Office ve görsel için 7 (bu karar ve #58'in tablo notu alanı). OCR'sız belgelerin çıktısı değişmiyor (11 belgede kuru çalıştırma, veritabanıyla aynı); yeniden işlenmeleri bulut çağrısı gerektirmez.

**Sorun.** Sistemden basılmış görüntü PDF'lerde (tech pack) "4XL" "AXL", "4XLT" "AXLI" okunuyordu. Rakam harfe döndüğü için iki okuma karşılaştırması (yalnız rakamlı parçalara bakar) bunu yakalamıyordu (kural 1).

**Neden.** Kapak sayfasında ayarlar tek tek değiştirildi (tur+eng): `--skip-text` → "4XL" doğru; `--skip-text --deskew` → "AXL". Sayfa düz (ölçülen eğiklik 248 tech pack sayfasının hepsinde 0,0°), düzeltme adımı görüntüyü yeniden örnekleyip harfleri bozuyor. Eğiklik düzeltme yalnız metin katmanı olmayan sayfalarda (`--skip-text`) uygulanıyordu; zayıf metinli sayfalar (`--force-ocr`) zaten düzeltmesizdi. Yalnız `tur` ile okumada hata düzeltmesiz de çıkıyor; uygulama `tur+eng` kullanıyor.

**Ölçüm (yerel, ücretsiz kuru çalıştırma, tur+eng).**
- 17 tech pack, 248 sayfa: "AXL/AXLI" 4 → 0 (ilk raporda 5 yazıyordu: "AXLI" iki kez sayılmıştı); iki okumanın uyuşmadığı değer 1.662 → 1.549; süre 337 → 317 sn.
- 6 sentetik taranmış/fotoğraf belge (eğiklik 0,4–2,6°): 93/93 → 93/93 doğru, gösterilen yanlış değer 0 → 0. Düzeltmenin bu belgelerde ölçülebilir yararı yoktu.
- 5–12° döndürülmüş fotoğraf denemesi sonuç vermedi (iki ayarda da okunmadı; döndürme görüntüyü bulanıklaştırdı). Güçlü eğiklik için gerçek fotoğrafla ölçüm gerekir.

**Ölçüm (ayrı ölçüm indeksi).**
- Geliştirme seti 38/40 → 38/40, doğrulanmış yanlış 0 → 0. Belirsiz: dikim-tarama 3 → 0, dikim-foto 1 → 2.
- Tech pack 6013448: belirsiz 16 → 14; parçalarda "AXL" 2 → 0. Parça metni değiştiği için sorular yeniden soruldu; cevaplar model değişkenliğiyle karıştı: BW005 LG 25 ve SL055 MD 25 ½ artık doğrulanmış, crossover 7/8 ("inch" birimi eklendi) ve NK041 28 (alıntıda sayı yok) gizlendi. Doğrulanmış yanlış sayı yok; ama "numune durumu belgede belirtilmemiştir" cümlesi doğrulandı (kapak formunda "Fit Approved, Hold Sampling" yazıyor: form eşleşmesi sorunu, açık).
- Maliyet 0,042 $ (yeni hücre okumaları ve yeniden sorulan cevaplar).

**Test.** OCR komutunu kuran `tools.py`, CI'da kurulmayan belge işleme paketlerini yüklüyor; birim testi eklenmedi. Davranış yukarıdaki kuru çalıştırmayla ölçüldü.

**Gerekenler.** Birleştikten sonra uygulamadaki 28 PDF/Office/görsel belgesi bir kez yeniden işlenmeli: 19 OCR'lı (hücre okumaları büyük ölçüde önbellekte) ve 9 OCR'sız (bulut çağrısı yok).

### 0008: Okuma katmanı ölçümü: sentetik kilitli set A ve dondurulmuş puanlama
Tarih: 2026-11-16. Dal: `sentetik-techpack` (PR #60). Hiçbir okuyucu set A'ya çalıştırılmadan donduruldu.

**Amaç.** OCR'ı test belgelerine göre ayarlamayı bırakıp görülmemiş belgelerde çalışan genel bir okuma katmanı seçmek. Adaylar: mevcut hat (resim yolundan) ve PaddleOCR-VL-1.6 (resmi akış: düzen modeli + bölge bölge, MLX) + ikinci okuma Tesseract. GLM-OCR bırakıldı (model kartında Türkçe yok; 5 geliştirme sayfasında uydurma metin ve 52 boşluğu düşmüş kesir).

**Set A.** `evals/assets/techpack_set_a/`: 5 belge × 6 sayfa, tohum 20261116, 2.277 değer (881 kesir, 314 eksi). Gerçek föylerden yalnız sayfa yapısı alındı (kapak formu, yorumlar, numune değerlendirme, BOM, ölçü tablosu, fark tablosu); bütün ad, kod ve değerler uydurma. Yazı tipi, kesir yazımı (tek karakter, küçük rakamlı, düz) ve birim belgeler arasında sırayla dağılır. Doğru cevap çizimle aynı veriden, kutusuyla kaydedilir; her değer dijital PDF'in metin katmanında kendi kutusunda bulunmazsa üretim durur (ilk denemede bir üretici hatası yakalandı: `.lower()` "İplik"i "i̇plik" yapıyordu). Dosyalar repoda (taramalar bunlara bağlı); test hem dosyaların hem üreticinin sha256 özetlerini denetler.

**Eşdeğerlik (ölçümden önce, `evals/ocr_truth.py`).** Yalnız yazım biçimi: kesir yazımları (`⅜`, `³⁄₈`, `3/8`, `\frac{3}{8}`), eksi işaretleri, boşluklar ve tırnaklar eşdeğer; `271/2 ≠ 27 1/2`; harf büyüklüğü korunur. Rakamlar arasındaki virgül–nokta eşdeğer **değil**: "1.500" ile "1,500" farklı değerler olabilir; yalnız ayraçla ayrılan değer "ayraç farkı" diye ayrı raporlanır. Bu kural ilk sürümde eşdeğerdi; hiçbir okuyucu çalışmadan değiştirildi, dondurma kuralına aykırı değil.

**Puanlama (`evals/ocr_score.py`).** Okuyucudan bağımsız okuma biçimi (sayfa → satır → hücre; konum varsa konumla, yoksa sırayla eşleşme). Sonuç türleri: doğru, ayraç farkı, yanlış karakter, bağ kopması (en ağır), atlama, gizlendi (doğruydu), gizlendi (yanlıştı). Etiket bağı, değer etiketin sağında ya da altındaysa korunur; iki etiket karışık okunursa ya da değer başka etikete bağlanırsa bağ kopmasıdır. Dijital metin katmanıyla sınama: 2.277/2.277 doğru, 0 atlama, 0 bağ kopması. Dönüştürücüler (mevcut hat parçaları, PaddleOCR-VL sayfa sonucu) 5 geliştirme sayfasında satır, sütun ve hücre metinlerini kaynakla birebir aktarıyor.

**PaddleOCR-VL'nin ikinci okuması.** Tesseract (tur+eng, eğiklik düzeltmesiz, psm 11). Her blokta her sayı ve kod parçasının (rakamsız kodlar dahil) geçiş sayısı iki okumada aynı olmalı; farklıysa o bloktaki o parçayı taşıyan bütün hücreler gizlenir. RapidOCR seçilmedi: PaddleOCR-VL ile aynı aileden, hataları ortak olabilir. Geliştirme sayfalarında (set A değil) 214 değer hücresinin 131'i belirsiz çıktı (129'u s.24'teki ölçü tablosu); PaddleOCR-VL'nin yanlış okuduğu 9 eksi kesirin 9'u da gizlendi. **Bilinen zayıflık:** aynı bloktaki iki hata birbirini dengelerse (bir "1/4" → "1/2", bir "1/2" → "1/4") sayılar tutar ve hata geçer.

**Karar kuralı (ölçümden önce yazıldı; sonuçlar görüldükten sonra değişmez).** Sayımlar `evals/ocr_score.py`'nin sonuç türlerinden, iki aday için set A'nın aynı taranmış ve fotoğraflanmış sayfaları üzerinden toplanır:
- **Doğru gösterilen:** "doğru".
- **Yanlış gösterilen:** "yanlış karakter" + "ayraç farkı" + "bağ kopması".
- **Benimsenir:** PaddleOCR-VL + Tesseract'ın yanlış gösterileni mevcut hattınkinden fazla değil **ve** doğru gösterileni daha yüksek.
- **Reddedilir:** Yanlış gösterileni mevcut hattınkinden fazla.
- **Ara durum:** Yanlış gösterileni eşit ya da az, ama "gizlendi (doğruydu)" sayısı daha yüksek. Bu durumda tasarım değişirse yeni tasarım set A ile değil, yeni bir tohumla üretilen set B ile ölçülür.
- **Öncelik:** Benimseme ve ara durum koşulları birlikte sağlanırsa (yanlış gösterilen eşit ya da az, doğru gösterilen ve "gizlendi (doğruydu)" ikisi de daha yüksek) aday **benimsenir**: daha çok doğru değer gösteriliyor.
- **Kapsanmayan durum:** Yanlış gösterilen eşit ya da az, ama ne doğru gösterilen ne de "gizlendi (doğruydu)" daha yüksek (örneğin aday daha çok değeri atlıyor): **reddedilir**, mevcut hatta göre kazanç yok.
- **Rapor kırılımı:** Her iki sayım ayrıca sayfa türüne (kapak, yorum, değerlendirme, BOM, ölçü, fark) ve kesir yazımına göre verilir. Kesir yazımı belgeye göre: syn1 ve syn4 tek karakter (⅜), syn3 düz (3/8), syn5 küçük rakamlı, syn2 küçük rakamlı ama santimetre (kesir az). Kırılım dondurulmuş puanlamanın sonuçlarından hesaplanır; puanlama kodu değişmez.

**Kurallar.** `ocr_score.py` ve `ocr_truth.py` özetleri testte; ölçümden sonra değişmez. Her aday set A'nın taranmış ve fotoğraflanmış sayfalarında bir kez ölçülür; sonuçlara bakıp üretici, puanlama ya da dönüştürücü değiştirilmez. Raporda "doğrulanmış yanlış değer" yanında sayı içermeyen yanlış cümleler de ayrıca yazılır.

**Üçüncü sabitleme (2026-11-19, ürün sahibi onayı).** Yalnız Windows düzeltmesi: `ocr_truth.py` doğru-cevap JSON'unu `\n` satır sonuyla yazar (Windows'ta CRLF yazıyordu, set A yeniden üretilemiyordu; PDF'ler zaten aynıydı), `ocr_score.py` Tesseract çıktısını utf-8 çözer. Dondurulmuş okumalarla (`evals/results/2026-11-16-set-a-benzetim`) `puanla.py` yeniden çalıştırıldı: `rapor.json` eski ve yeni kodla birebir aynı, karar yine "Benimsenir". Puanlama kuralları değişmedi.

### 0009: Set A basılı taranamadı; ölçüm taranmış ve fotoğraflanmış benzetimle yapılır
Tarih: 2026-11-16. Dal: `set-a-benzetim`. Ekip set A'yı basıp tarayamadı; benzetimi kod üretir. Hiçbir okuyucu çalıştırılmadan donduruldu.

**Benzetim (`evals/render/imaging.py`, `degrade_set`, tohum 20261116).**
- Tarama: 30 sayfanın hepsi, 300 dpi gri; ±1,5° eğiklik, 0,4–0,8 piksel bulanıklık, Gauss gürültüsü (σ 6), kontrast 0,85–1,05. Belge başına bir PDF (`synN_tarama.pdf`).
- Telefon fotoğrafı: her sayfa türünden 2 sayfa (12 fotoğraf), ~220 dpi; masa zemini, köşelerde %3'e kadar perspektif (dönme dahil, tek dönüşüm), bir yandan gelen ışık (en karanlık yer %67), 0,6–1,0 piksel bulanıklık, gürültü (σ 8), JPEG kalite 70–85 (`synN_sM_foto.jpg`).
- Var olan düşük çözünürlüklü benzetim (yaklaşık 122 dpi; geliştirme setleri için) değişmedi; set A'nın 7–8,5 puntoluk yazısı için kullanılmadı.
- Aynı tohum aynı dosyaları verir (gürültü tohumdan türetilir, PDF tarihi sabit); 17 dosyanın sha256 özetleri testte. Dosyalar 31 MB olduğu için repoya girmedi; testteki özetlerle yeniden üretilir.

**Sınırlar (ölçüm raporunda yazılacak).** Gerçek kâğıt, gerçek tarayıcı ve gerçek telefon değil: kâğıt dokusu, mürekkep yayılması, katlanma, gölge, odak dışı bölge, kamera bükülmesi ve renkli gürültü yok; bozulmalar düzgün ve tek tip. Sonuçlar gerçek taramaya göre iyimser olabilir. Karar kuralı (0008) değişmeden uygulanır.

### 0010: Okuma ölçümü sonucu: PaddleOCR-VL + Tesseract karar kuralına göre benimsenir (ince farkla)
Tarih: 2026-11-16. Ölçüm: set A benzetimi (0009), 5 taranmış belge (30 sayfa) + 12 telefon fotoğrafı, 3.121 değer. Her aday bir kez çalıştırıldı; puanlama, dönüştürücüler ve karar kuralı (0008) ölçümden önce donmuştu, değişmedi.

| | Mevcut hat | PaddleOCR-VL + Tesseract |
|---|---|---|
| Doğru gösterilen | 1.324 | 1.325 |
| Yanlış gösterilen | 788 (bağ kopması 693, yanlış karakter 95, ayraç 0) | 87 (bağ kopması 37, yanlış karakter 50, ayraç 0) |
| Atlama | 922 | 49 |
| Gizlendi (doğruydu / yanlıştı) | 43 / 44 | 1.335 / 325 |
| Süre (42 sayfa) | 871 sn | 271 sn (PaddleOCR-VL 238 + Tesseract 33) |
| Bulut maliyeti | 0,32 $ | 0 $ |

**Karar kuralının sonucu: Benimsenir.** Yanlış gösterilen fazla değil (87 ≤ 788), doğru gösterilen yüksek (1.325 > 1.324). Fark doğru gösterilende yalnız 1 değer: kazanç yanlış gösterilenin %89 azalması ve atlamanın neredeyse kalkması; bedel değerlerin yaklaşık %43'ünün (1.335) doğru okunduğu hâlde gizlenmesi (Tesseract aynı bloğu farklı sayıyor).

**Kırılım (doğru / yanlış gösterilen).** Tarama: mevcut hat 1.075 / 507, aday 1.035 / 32. Fotoğraf: 249 / 281, aday 290 / 55. Sayfa türü — ölçü 477/258 → 305/51; fark 212/234 → 253/6; BOM 253/179 → 424/14; değerlendirme 282/111 → 185/3; kapak 62/6 → 82/3; yorum 38/0 → 76/10. Kesir yazımı — tek karakter 657/423 → 446/59; düz 329/159 → 237/15; küçük rakamlı 279/161 → 233/10; küçük rakamlı (cm) 59/45 → 409/3.

**Mevcut hat: 788 değer yanlış gösteriliyor.** Bugün uygulamada çalışan hat, bu benzetimde 788 değeri yanlış gösterdi: 507'si taranmış belgelerde (30 sayfa), 281'i telefon fotoğraflarında (12 sayfa). 693'ü bağ kopması (değer yanlış sütun ya da etikete bağlı), 95'i yanlış karakter. Hattın kendi iki okuması bunların yalnız 44'ünü gizledi. Bu, kural 1 açısından hattın bugünkü durumudur; benzetim gerçek taramaya göre iyimser olabileceği için gerçek sayı daha yüksek olabilir.

**Gözlemler.**
- Mevcut hattın bağ kopmaları gerçek: OCR sütun başlıklarını bozuk okuyor ("Tol (-)" → "Tol)", "Tol (+)" → "Tol 6)"), bazı satırlarda bir sütun kayboluyor; değer yanlış adlı sütuna bağlanıyor.
- Adayın 50 yanlış karakterinin 26'sı tek bir ortak hatadan: fotoğraftaki ölçü tablosunda tek karakterli kesirler ("⅞") PaddleOCR-VL'de de Tesseract'ta da "%" okunuyor ("14⅞" → "14%"); iki okuma aynı yanlışta uyuştuğu için gizlenmiyor. Bu, bilinen zayıflıktan (dengelenen iki hata) farklı: iki okuyucunun aynı hatası. Dengelenen hataların sayısı ayrıca ölçülmedi.
- Yalnız okuma ölçüldü; cevap modeli çalıştırılmadı, bu yüzden "sayı içermeyen doğrulanmış yanlış cümle" bu ölçümde yok.

**Sınırlar.** Benzetim, gerçek kâğıt ve kamera değil (0009); sonuçlar iyimser olabilir.

**Ekip kararı (2026-11-16).** Uygulamaya geçilmiyor. "⅞" → "%" ortak hatası için düzeltme yapılmıyor; tasarım değişirse set A ile değil set B ile ölçülür. Set A'nın gerçek taramaları geldiğinde aynı iki aday, hiçbir şey değiştirilmeden bir kez daha ölçülecek.

**Uygulamadaki aday ölçülen adayla aynı değil (2026-11-17, 0011).** Uygulamaya alınan okuyucu, ölçülen adaydan iki bakımdan ayrılır: çözünürlük (ölçümde her sayfa 300 dpi görüntüydü; uygulama taramayı kendi çözünürlüğünde okutur) ve girdi yolu (ölçümde sayfa görüntüsü doğrudan verildi; uygulama PDF sayfasını çizer, OCR katmanlı taramaları da okuyucuya verir, görsel dosyasını doğrudan okutur). Bu tablodaki sayılar uygulamadaki hattın ölçümü değildir. Bir sonraki ölçüm yeni tohumla üretilen set B ile yapılacak. Eski hattı yeniden ölçmek için `c79e4ce` kullanılmalı.

**Set B'de ayrıca ölçülecek (2026-11-17).** Okuyucu yolundaki tablo başlığı kuralı: okuyucu başlık hücresini işaretlemediği için (yüklü 17 föyün 427 tablosunda ve set A kaydının 74 tablosunda yalnız `<td>` var) ilk satırın başlık olup olmadığı tablonun yapısından anlaşılıyor (etiketin altında rakamlı değerler; ilk hücresi rakamlı, altı metin olan sütun karşı kanıt). Kural yüklü föylere bakılarak kuruldu; görülmemiş belgelerde ne yaptığı bilinmiyor ve set B ile ölçülecek. Yüklü föylerde: ölçü tabloları 57/57 başlıklı kaldı, formların 44/49'u okunduğu gibi bırakıldı (5 kapak formu hâlâ kaymış), 64 malzeme tablosunun 10'u başlığını kaybetti.

**Okuyucuya istekler tek tek gidiyor; ölçülen aday bu bakımdan da farklı (2026-11-18).** Aynı fotoğraf (`dikim-foto.jpg`) aynı kodla bir okumada farklı okundu: tablonun başlık satırı bir hücre eksik geldi ve değerler bir sütun kaydı ("S: Bel | M: 38,0"; doğrusu S 38,0, M 40,0). Örnekleme ayarı neden değil: PaddleOCR-VL `mlx-vlm-server` arka ucuna `temperature=0` gönderiyor (paddlex `doc_vlm/predictor.py`), `top_p` göndermiyor. Neden eşzamanlılık: sayfanın blokları sunucuya aynı anda gidiyordu (sunucu kaydında `in_flight=2`, `backend=continuous_batching`) ve sunucu birlikte işlediği isteklerde farklı çıktı üretebiliyor. `vl_rec_max_concurrency=1` yapıldı. Sonrasında aynı fotoğraf iki ayrı sunucu oturumunda dörder kez okutuldu: 8 okumanın ham çıktısı birebir aynı (sha256 `961547de3349…`), sunucu kaydında eşzamanlı istek yok. Tek fotoğrafla gösterildi; kaymış okuma eski ayarla 5 denemede 1 kez görüldü ve yeniden üretilemedi. Set A ölçümü eşzamanlı isteklerle yapılmıştı; set B tek tek isteklerle ölçülecek.

**Set B'de ayrıca ölçülecek: hücre sayısı uyuşmayan tablo (2026-11-18).** Başlık sayılan ilk satırın hücre sayısı bir veri satırınınkinden farklıysa tablo başlıksız, okunduğu gibi yazılıyor. Yüklü 17 föyün saklı ham okumalarında 446 tablonun 6'sını etkiliyor: 3 kapak formu (başlık 6 hücre, satırlar 5/4/2; bunlar zaten kaymış yazılıyordu) ve 6013448'in 3 ölçü karşılaştırma tablosu (iki katlı başlık; alt başlık satırı 4 hücre, 45 değer satırı etiketini kaybediyor). Başlık satırı satırlarla aynı sayıda hücre taşıdığı hâlde kaymışsa (düşen hücrenin yerine boş hücre gelmişse) bu kural yakalamaz; fotoğrafta görülen kaymanın hangi türden olduğu saptanamadı.

**Set B'de ayrıca denenecek: büyük sayfa görselini küçültmek (2026-11-19).** Okuyucu taramayı kendi çözünürlüğünde alıyor. Windows'ta işlemcide bir tech pack sayfası 5–16 dakika sürdü (karar 0015); 16,7 MB'lık 29 sayfalık föyün sayfa görselleri büyük. Görseli belli bir kenar uzunluğuna küçültmenin süreye ve okumaya etkisi set B ile ölçülecek. Dikkat: 120 dpi taramayı 300 dpi'ye büyütmek Tesseract'ın bütün değerleri doğrulayamamasına yol açmıştı (açık notlar, Sayfa okuyucusu); küçültme ikinci okumayı da etkileyebilir. Şimdilik değiştirilmedi.

**Kayıt.** Rapor (`rapor.json`), mevcut hattın okuması (`hat_cikti.json`) ve PaddleOCR-VL + Tesseract ham okumaları (`paddle/`): `evals/results/2026-11-16-set-a-benzetim/` (1 MB). Okuyucuları yeniden çalıştırmadan yeniden puanlama ve gerçek taramalarla yan yana karşılaştırma için repoda tutulur. Ölçümü yapan dört betik (`hat.py`, `paddle_calistir.py`, `tesseract.py`, `puanla.py`) aynı klasörde, ölçüldükleri haliyle durur; gerçek taramalar bunlarla, değiştirilmeden ölçülür. Bu yüzden klasör ruff ve mypy denetiminin dışındadır. `paddle_calistir.py` MLX sunucusunu `http://localhost:8111/` adresinde bekler.

### 0011: PaddleOCR-VL + Tesseract hatta alındı; okuyucu yoksa belge bekler
Tarih: 2026-11-16. Ürün sahibi kararı; yeni bağımlılık (`paddleocr[doc-parser]`, `paddlepaddle`) onaylandı.

**Ne.** Metin katmanı olmayan sayfalar (`PageKind.NONE`) yalnız sayfa okuyucusundan geçer. OCR katmanlı taramalar da böyle sayılır: sayfayı kaplayan bir görüntü var ve metin nesnelerinin en az %90'ı görünmez yazım kipinde ya da o görüntünün altında (başka bir aracın OCR çıktısı, dijital metin değil). Akış: PaddleOCR-VL-1.6 resmi akışı okur, her blok Tesseract (tur+eng, psm 11, deskew yok) ile ikinci kez okunur, sayı ve kodlar sayarak karşılaştırılır (0010'daki gibi). Sayısı tutmayan değer belirsizdir, cevapta gizlenir. Görünür metni olan sayfaların yolu (zayıf metin katmanı, büyük görselli dijital sayfa, gömülü görseller) değişmedi. Görsel dosyası (jpg, png) okuyucuya PDF'e çevrilmiş kopyasıyla değil, kendi pikselleriyle verilir.

**Okuyucu yoksa.** `VA_PAGE_READER` boşsa ya da okuyucuya ulaşılamıyorsa belge indekslenmez, "Okuyucu bekleniyor" (`waiting_reader`) durumunda kalır; "Yeniden işle" ile okunur. Eski OCR yolu yedek değildir. Belgenin metin katmanlı sayfaları da bekler: belge ya tamamen okunur ya hiç.

**Tek ayar.** `VA_PAGE_READER`: `local` ya da `<arka uç>@<adres>`; platforma göre kod yok. Sunucuyu uygulama başlatmaz.

**Kopya kod.** Eşdeğerlik kuralları ve sayarak karşılaştırma `evals/ocr_score.py` ve `evals/ocr_truth.py` içinde sha256 ile donmuş; uygulama ölçüm paketinden içe aktarmaz. Kod `ingest/page_reader.py` içine kopyalandı. `tests/test_page_reader.py` set A kaydının 42 sayfasında iki kopyayı karşılaştırır: her blokta parçalar ve tablo satırları aynı; aynı ikinci okumayla işaretler aynı; kayıttaki işaretlerin gizlediği değerlerin tamamı uygulamanın öğelerinde belirsiz. Kayıtta sayfa görüntüleri ve Tesseract'ın ham metni yok, set A'ya yeniden okuyucu çalıştırılmaz: ölçümdeki işaretler baştan hesaplanarak değil, kayıttan doğrulandı.

**Bilinenler.**
- Metin, karşılaştırılan yazımla saklanır ("14⅞" → "14 7/8"): belirsiz değer cevap denetiminde aynı yazımla aranır.
- Tabloda hücre konumu yok: kaynak panelinde satır yerine tablonun tamamı vurgulanır.
- 0010'daki ortak hata sürüyor: "⅞" iki okuyucuda da "%" okunursa gizlenmez.
- Eski OCR'ın telafi kodu (çizgili tablo, hücre okuma, deskew notları) silinmedi; metin katmanlı taranmış sayfalar onu hâlâ kullanıyor. Ayrı PR.
- `evals/results/2026-11-16-set-a-benzetim/hat.py` uygulamanın hattını çağırır: bu karardan sonra "mevcut hat" adayını değil yeni hattı ölçer. Gerçek taramalarda eski hattı ölçmek için `c79e4ce` kullanılmalı.
- Kural sürümü 8, yalnız taranmış sayfası olan belgeleri eskitir: 7. sürümle işlenmiş ve kaydında `none` ya da `scanned` sayfa olmayan belge "Eski kural" görünmez (`is_outdated`).
- Ölçüm MLX arka ucuyla yapıldı; `local` kipinin okuması ve hızı ölçülmedi.
- Tarama kendi çözünürlüğünde okunur (büyütülmez): büyütülmüş görüntüde Tesseract'ın ikinci okuması bozuluyor (açık notlar, 2026-11-17 denemesi).

### 0012: Taranmış belgelerde yapı kalıyor; gizleme bedeli kabul edildi
Tarih: 2026-11-17. Ürün sahibi kararı.

**Karar.** Taranmış sayfalar için bugünkü yapı kalır: PaddleOCR-VL okur, Tesseract ikinci kez okur, sayı ve kodlar blok düzeyinde sayarak karşılaştırılır (0011). Yeni bir ikinci okuyucu denenmeyecek; karşılaştırma satır düzeyine alınmayacak.

**Neden.**
- Kural 1 korunuyor: iki okumanın uyuşmadığı değer gösterilmez. Yanlış değer göstermektense göstermemek tercih edilir.
- Belgelerin çoğu dijital; gizleme yalnız taranmış sayfaları etkiler.
- Yapı sade kalıyor: yeni okuyucu, yeni bağımlılık ve yeni ölçüm turu gerekmiyor.

**Kabul edilen bedel (2026-11-17 ölçümü, yüklü 17 tech pack, 248 sayfa, 300 dpi).** Yeniden işlemeden sonra parça metnindeki sayı ve kodların belirsiz işaretli payı %0,6'dan %42,8'e, belirsiz değer taşıyan parça oranı %6'dan %61'e çıktı. Okuma düzeyinde 22.381 değerin 11.747'si (%52,5) gizleniyor. Gizlenenlerin 10.383'ü (%88) ikinci okumada karşılığı olmayan değer, 1.364'ü (%12) karşılığı olduğu hâlde bloktaki sayım farkı yüzünden gizlenen değer. Kesirlerin %83'ü gizli: Tesseract föylerdeki kesirleri okuyamıyor ("24 1/2" yerine "24%"). Satır düzeyinde karşılaştırma tahminen yalnız 285 değer kazandırırdı (%52,5 → %51,2). Bu föylerin doğru cevap dosyası yok: gizlenenlerin kaçının doğru okunduğu, gösterilenlerin kaçının yanlış olduğu ölçülmedi.

**Karşılığı (0010, set A benzetimi).** Yanlış gösterilen değer 788'den 87'ye indi; doğru gösterilen 1.324'ten 1.325'e çıktı. Bu sayılar set A'ya aittir; uygulamadaki hat ölçülen adaydan farklıdır (0010 eki).

**Yeniden düşünülür.** Kullanıcılar taranmış föylerde gizlenen değer yüzünden asistanı kullanamıyorsa. İkinci okuyucunun değişmesi ya da karşılaştırma düzeyinin değişmesi ölçülen adayı değiştirir; yeni tohumla üretilen set B ile ölçülmeden yapılmaz.

**Yeniden işleme (2026-11-17).** Kural 8 ile çıktısı değişen 19 belge (18 taranmış PDF, 1 fotoğraf; 252 sayfa) yeniden işlendi: 40 dakika, bulut maliyeti 0 $, hata yok. Parça sayısı 1774'ten 2408'e çıktı.

### 0013: Eski OCR'ın telafi kodu silindi; fark filtresi kaldı
Tarih: 2026-11-17. Ürün sahibi onayı.

**Silinen.** Hücre okuyucu (`cell_reader.py`: OCR'lı tablo hücrelerini görüntü modeliyle yeniden okuyup doğrulayan katman, karar 0005), çizgili tabloları çizgilerinden okuyan ızgara okuma (`ruled_table.py`, karar 0006'nın okuma kısmı), bunların `tools.py` ve `docling_parser.py` içindeki bağlantıları, `VA_CELL_READER_*` ayarları ve eski OCR yolunun metin katmansız sayfa dalları ("yalnız görüntü kaldı" uyarısı dahil). Belge işlerken buluta görüntü gönderen tek yer hücre okuyucuydu: belge işleme artık tamamen yerel.

**Neden.** Bu kod eski OCR'ın taranmış tablolardaki hatalarını telafi ediyordu. Metin katmansız ve OCR katmanlı sayfalar artık sayfa okuyucusundan geçiyor (0011); telafi kodunun çalıştığı sayfa kalmadı.

**Kalan.** Fark filtresi (0006: "Grade Rule: Increment" tablolarının satırları, soru farkı sormuyorsa kaynak olmaz) kaldı: OCR hatasını değil modelin farkı ölçü diye vermesini engelliyor, yeni okuyucunun parçalarında da çalışıyor. Eğiklik ayarı 0007'de zaten kaldırılmıştı. Eski OCR yolu (ocrmypdf, rapidocr) görünür ama zayıf metin katmanlı sayfalar ve metinli sayfalardaki gömülü görseller için duruyor; bu yüzden hiçbir bağımlılık boşa çıkmadı.

**Etki.** Kural sürümü 9. Yalnız eski OCR yolundan geçen (`weak`, `scanned`) sayfası olan belgeler eskir; yüklü belgelerde böyle sayfa yok. O sayfalardaki tablolar ileride gelirse hücre düzeyi doğrulama olmadan, sayfa düzeyi iki okumayla işlenir. Dondurulmuş `hat.py` bugünkü kodla içe aktarılamaz (hücre okuyucuyu çağırıyor); eski hattı ölçmek için `c79e4ce` kullanılır.

### 0014: Sınır seti turu kapandı; kilitli 8 soru artık görülmüş sayılır
Tarih: 2026-11-18. Ürün sahibi kararı.

**Tur.** Yüklü belgeler üzerindeki sınır seti (`evals/sinir_yuklu_belgeler.json`: 32 soru; birim, yanlış sütun, olumsuzlama, niteleyici) ile yürütülen tur. Bu turda giren kurallar: "belgede yok" iddiası doğrulanmış gösterilmez (#71); tekrarlanan cümlede rozet (#72); okuyucu yolunda form tabloları başlıksız, okunduğu gibi (#73); boş hücre "(boş)" (#75); soruda geçen sayısal model numarası belgeyi seçer (#76); kaynaklardan söz eden, değer taşımayan cümle doğrulanmış gösterilmez (#77); hücre sayısı uyuşmayan tablo başlıksız ve okuyucuya istekler tek tek (#78). Kurallar yalnız kilitli olmayan 24 soruyla geliştirildi.

**Kilitli set sonucu (8 soru × 5 koşu, #78 koduyla, kural 13 indeksi).** Yanlış 0; doğrulanmış gösterilen sayısız yanlış cümle 0. Koşu başına doğru / güvenli / yanlış: 7/1/0, 6/2/0, 6/2/0, 6/2/0, 6/2/0. A6, B2, B7, C4, D5, D8 beş koşuda da doğru. A3 bir koşuda doğru, dördünde güvenli (model kaynakta olmayan "cm" birimini ekledi; cümle gizlendi, kaynak satırı gösterildi). C7 beş koşuda da "bulunamadı".

**Ölçümün koşulu.** Bu ölçümde sorgu çevirisi 40 sorunun 40'ında süre sınırını (1,2 sn) aştı; arama özgün Türkçe soruyla yapıldı. C7'nin nedeni bu: beklenen parça özgün soruyla 11. sırada (modele 8 parça gider), İngilizce sorguyla 1. sırada. Aynı gün yapılan #78 ölçümünde de çeviri 134 sorunun 127'sinde düştü; bir gün önceki #77 ölçümünde 120 sorunun 11'inde. Yani bu sonuçlar çevirinin çalışmadığı koşulu ölçüyor; çeviri çalışırken sonuç daha kötü olmaz beklenir ama ölçülmedi.

**Karar.** Tur bu sonuçla kapandı. Kilitli 8 soru (A3, A6, B2, B7, C4, C7, D5, D8) artık görülmüş sayılır: cevaplarına bakıldı, bundan sonra kural geliştirirken kullanılabilirler ama kilitli ölçüm yerine geçmezler. Sonraki tur için yeni kilitli sorular yazılacak.

**Açık kalan.** Birim ekleme (A3, A4: istem kuralı var, model yine ekliyor); sorgu çevirisinin süre sınırı; D2 (fotoğrafta bölüm yok); D4 ve D6 (seçeneksiz netleştirme).

### 0015: Taranmış tech pack'ler normal bilgisayarda okunmaz; hızlı makinede işlenip veri taşınır
Tarih: 2026-11-19. Ürün sahibi kararı.

**Ölçüm (Windows 11, 12 mantıksal işlemci, paddlepaddle işlemci paketi, `VA_PAGE_READER=local`).** PaddleOCR-VL-1.6 + Tesseract ikinci okuması, sayfa başı:

| Belge | Bu bilgisayar | Mac (MLX, 2026-11-17) |
|---|---|---|
| `dikim-foto.jpg` (1 sayfa) | 57,6 sn; model yükleme dahil 165,6 sn | 4,3 sn |
| `dikim-tarama.pdf` (3 sayfa) | ≈ 50 sn (toplam 149,6 sn; uygulamada 38 ve 47 sn) | 5,5 sn |
| 6013448 tech pack, sayfa 1–3 | 16 dk 12 sn, 5 dk 47 sn, 5 dk 7 sn | ölçülmedi |

Fotoğraf ve ölçü föyü taraması Mac'ten 9–13 kat yavaş; okunan değerler Mac'tekiyle aynı (fotoğraf iki okumada birebir aynı). 29 sayfalık tech pack bu hızla 2,5–3 saat sürerdi; işlem 3. sayfadan sonra durduruldu ve belge silindi (dosya repoda değil; ürün sahibinde).

**Karar.** Taranmış tech pack'ler normal bilgisayarda okuyucuyla işlenmez; hızlı bir makinede işlenip veri (`data/`: veritabanı, Qdrant klasörü, belge dosyaları) taşınır. Küçük taramalar (1–3 sayfalık ölçü föyü, fotoğraf) bu bilgisayarda da işlenebilir. Eski OCR yolundan kalan parça bırakılmadı: bu bilgisayardaki yüklü belgelerde 0.

**Bilinmeyen.** Verinin bir makineden ötekine taşınması denenmedi (yollar, Qdrant yerel klasörünün sürüm uyumu). Tech pack sayfalarının neden ölçü föyünden 6–20 kat yavaş olduğu ölçülmedi; görsel boyutu en olası neden (set B'de denenecek, karar 0010/0011 altındaki liste).

**Yeniden düşünülür.** Görsel küçültme süreyi pratik düzeye indirirse ya da okuyucu için ekran kartlı bir sunucu gelirse.

### 0017: Docker paketi kaldırıldı; sunucu gündeme gelince geri alınır
Tarih: 2026-11-19. Ürün sahibi kararı.

**Ne kalktı.** `Dockerfile`, `compose.yaml`, `.dockerignore`, `apps/web/Dockerfile`, `apps/web/.dockerignore`, `apps/web/nginx.conf`, CI'daki `services` işi, README'deki sunucu bölümü, ayrı işçi süreci (`apps/worker/main.py`'nin `main`'i; işleme işlevleri `apps/worker/run.py`'de kaldı) ve `VA_WORKER_IN_PROCESS` ayarı.

**Neden.** Paket hiçbir bilgisayarda denenmemişti ve yerel kipten ayrışmıştı (mimari denetimi, 2026-11-19): compose'da okuyucu ayarı yoktu (taranmış belge sunucuda sonsuza dek beklerdi), imajda `libreoffice-calc` yoktu, docling modellerinin klasörü boş bir birime işaret ediyordu, okuyucu modelinin (3,6 GB) yeri tanımlı değildi. İşçinin kurulması iki yerde yazılıydı.

**Geri alma.** Sunucu gündeme gelince bu commit'in sildiği dosyalar git geçmişinden geri alınır ve yukarıdaki eksikler giderilir. Qdrant sunucusu ayarı (`VA_QDRANT_URL`) duruyor; yerelde gömülü klasör kullanılır.

### 0018: Eski OCR yolu (ocrmypdf, RapidOCR) kalıyor
Tarih: 2026-11-19. Ürün sahibi kararı.

**Ne.** Görünür ama zayıf metin katmanlı sayfalar ve büyük görselli dijital sayfalar (`WEAK`, `SCANNED`) ocrmypdf ile, dijital sayfalardaki gömülü görseller RapidOCR ve Tesseract ile okunmaya devam eder; bu yol silinmez.

**Neden.** Bu (normal) bilgisayarda sayfa okuyucusu sayfa başına 50 sn ile 16 dakika arasında sürüyor (karar 0015); bu sayfaları okuyucuya göndermek pratik değil. Yüklü belgelerde bu türden sayfa şu an yok; eski yoldan kalan parça 0.

**Bilinen zayıflık.** Bu yolun ikinci okuma karşılaştırması okuyucununkinden gevşek (harf-rakam eşdeğerliği, rakamsız kod denetlenmiyor; mimari denetimi B2) ve gömülü görsel tablolarında başlık kayması koruması yok (B3). İkisi yeniden işleme turunun planında.

