# Karar kaydı

Bugüne kadar alınmış önemli kararlar: ne, ne zaman, neden, hangi durumda yeniden düşünülür.
Kararların tek kaydı bu dosya. Numarayla anılan karar belgelerinin (0001–0035) tam metni en
sonda: [Karar belgeleri](#karar-belgeleri).

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
  `generation/translate.py`; süre sınırı 1,5 sn (`ask/deps.py`,
  `DEFAULT_TRANSLATION_LIMIT_SECONDS`; 18 Kasım'a kadar 1,2 sn).
- **Neden:**
  - Eski pilot (`adim2/hat_rapor_2026-11-06.md`, Ek): yanlış ret 25'ten 11'e düştü.
    - Ölçüm onaylı 199 sorunun cevaplı 160'ında yapıldı (kural çıkışları hariç), 245
      sorunun tamamında değil.
    - Karşılaştırılan iki hat ("varsayılan yol" ve "ikili yol") yalnız çeviriyle
      ayrılmıyor. Farkın tamamı çeviriye bağlanamaz (`docs/MIMARI.md` A4.13).
  - Çeviri modeli Gemma 4. Yardımcı model sağlayıcı sırası Parasail, Venice, NextBit
    (`settings.py`, `helper_providers`; 18 Kasım'a kadar NextBit). Eski pilotta NextBit
    üzerinde p95 1,04 sn, %2'si 1,2 sn sınırını aşıyordu.
    Aynı model (ayar: `VA_HELPER_MODEL` / `VA_HELPER_PROVIDERS`; eski adı
    `VA_TRANSLATION_*`) takip sorusunu tamamlama ve niyet sınıflandırmasını da yapar.
    Gemma 3 ile DeepInfra'da %96'sı aşıyordu
    (`b4/asama4_ceviri_karsilastirma_2026-11-05`).
  - Yoğun arama özgün soruyla yapılır. Çeviri yalnız soru dili belge dilinden farklıysa
    çalışır; süreyi aşarsa özgün soruyla aranır.
- **Yeniden düşünülür:** Belgeler ve sorular aynı dilde olursa gereksiz kalır. FastReact
  ölçümünde 18 sorunun birinde sınır aşıldı.

- **Sınır ve sağlayıcı değişikliği (2026-11-18, `b3d4552`):** yukarıdaki 1,5 sn ve sağlayıcı
  sırası bu commit'ten (açık notlar). 21–22 Kasım'da 47 sorunun 1'inde çeviri
  düştü.
- **Niyet sınıflandırmasıyla birlikte başlar (2026-11-22, dal `niyet-ceviri-paralel`; ürün sahibi
  onayı).** Niyet sınıflandırıcısı ve çeviri yardımcı modele ayrı çağrılardır ve art arda
  bekleniyordu; 19 Kasım sonrası 3 sn'yi aşan 19 cevapta ortalama niyet 0,81 sn, çeviri 0,96 sn
  (doğrulama 0,00 sn: süreyi doğruluk kuralları uzatmıyor). Artık sınıflandırıcı çağrılacaksa
  çeviri de o anda başlar; arama adımı sonucunu bekler. Mesaj selam ya da envanter çıkarsa
  başlamış çeviri iptal edilir (boşa giden küçük bir çağrı). Sınıflandırıcının atlandığı
  yollarda (soruda kod, seçilmiş belge, bilinen selam) akış aynıdır.
  - **Ölçüm (Mac, uygulama, 394 belge; kod içermeyen 15 soru, her biri önce `main` sonra dalda
    birer kez; maliyet 0,009 USD).** İlk doğrulanmış cümle ortanca 3,02 → 2,25 sn, p95 4,84 →
    3,14 sn, 3 sn'yi aşan 8 → 1; cevap öncesi adımların ortalaması 2,21 → 1,33 sn. İki turda da
    15 soru cevaplandı, durumlar aynı (14 doğrulandı, 1 doğrulanamadı), sağlayıcı hep Makora.
    Taban 7 ve 11 (önbellekten): 39/40, doğrulanmış yanlış 0, kırk sorunun kayıtları öncekiyle
    aynı. Taban setlerinde belgeler Türkçe olduğu için çeviri hiç çalışmaz; süre farkı orada
    ölçülemez, bu yüzden süre uygulamada ölçüldü. Tek tur ve küçük örnek: ikinci turda sağlayıcı
    biraz hızlıydı (cevap modeli ortalaması 1,38 → 1,26 sn), kazancın o kadarı değişikliğe ait
    değildir.
  - **Günlükte anlam değişti:** `translate` süresi artık aramanın çeviriyi beklediği süredir
    (özet satırı "çeviri bekleme"); çağrının kendi süresi kaydedilmiyor. 1,5 sn sınırını
    yeniden ayarlamak için çağrı süresi gerekirse ayrıca kaydedilmelidir.
  - **Ölçülmedi:** aynı sağlayıcıya eşzamanlı iki çağrının yük altında çeviri düşme payına
    etkisi (bu ölçümde 15 soruda 0 düştü; öncesinde 1).
- **Terim seçimi denemesi (2026-11-26, ürün sahibinin istediği deneme; kod birleştirilmedi,
  dal `ceviri-terim-secimi` (`0ada298`) referans olarak `origin`'de).** Sorun: çeviri Türkçe terimi belgedekinden farklı İngilizce adla
  veriyordu ("ön ağ" → "front crotch", belgede "Front Rise"; 6026417'de doğru satır 6. sıraya
  düşüyordu). Çeviri zaten sıcaklık 0; aynı soruda terim koşudan koşuya nadiren değişiyor.
  Ölçüm yalnız arama düzeyinde: kabul seti (16), yüklü sınır seti (32), FastReact (18) ve
  ipucu çıkarılmış Y03/Y06/Y11; 69 soru, 52'si çeviriye gider, her biri bir kez çevrildi,
  ilk 8 çevrimdışı kuruldu. Taban setleri ölçülmedi (belgeler Türkçe, çeviri çalışmaz).
  - **(c) İstem cümlesi** ("teknik terimin hedef dilde birden çok yaygın adı varsa onları da
    yaz"): 52 çevirinin 25'i değişti; 10'unda model Türkçe terimi parantezde ekledi, yalnız
    2'sinde İngilizce alternatif ekledi. Cümle amaçlandığı gibi uygulanmadı. Belge düzeyinde
    65 soruda 1 iyileşen (Y03 ipuçsuz: doğru parça 6. → 1.; çeviri "front rise (ön ağ)",
    "front crotch" yanında yok, yani alternatif değil başka terim seçimi), 0 kötüleşen.
    Tek koşu olduğu için bu iyileşme çeviri değişkenliğinden ayrılamaz (eski istem de canlıda
    3 koşunun birinde "front rise" verdi). Süre p50 0,59 → 0,67 sn, düşen çeviri 0.
  - **(d) Daha güçlü çeviri modeli** (yalnız ZDR: Amazon Bedrock, Google Vertex). Sonnet 5.5
    düşünme kapatılarak çağrılamıyor (400); en düşük düşünmeyle ölçüldü. Haiku 5.5 düşünmesiz
    çalışıyor. İkisi de "ön ağ" için "front rise" verdi (Y03 ipuçsuz 6. → 1.; C7 2. → 1.),
    ama FastReact'ta daha serbest çevirip belgenin sözcüklerinden uzaklaştı ("close" →
    "shut down"): Haiku 3 soruda kötüleşti (FR6 ilk 8'den çıktı), Sonnet 4 soruda.
    Sonnet soru başına 0,00055 $ (Gemma'nın ≈ 25 katı), p95 1,30 sn.
  - **Sonuç:** hiçbir yol terim sorununu güvenilir biçimde çözmedi; (d) BM25'te kötüleştirdi.
    İstem ölçümden sonra yeniden değiştirilip ölçülmedi.
  - **Karar (ürün sahibi, 2026-11-26): çeviri Gemma 4 26B ile ve bugünkü istemle kalır.**
    Neden: daha güçlü model (Haiku ya da Sonnet 5.5) terimi doğru seçse de belgenin kendi
    sözcüklerinden uzaklaştığı için BM25'te 3–4 soruyu kötüleştirdi, iyileştirdiği soru 2;
    Sonnet ayrıca soru başına ≈ 25 kat pahalı ve düşünme kapatılamadığı için yardımcı model
    istemcisine ek ayar ister. İstem cümlesi (c) amaçlandığı gibi uygulanmadı. Terim sorunu
    açık kalır; yeniden ele alınırsa çeviri değil, terimin belgedeki adını bulan başka bir yol
    gerekir.

### Modele 8 kaynak gider (5'ten artırıldı)
- **Ne zaman:** Eski pilot, Adım 2 (2026-11-06). Bu repoda `DEFAULT_TOP_K = 8` (0001).
- **Neden:** Ölçüm `adim2/hat_rapor_2026-11-06.md`, Ek (onaylı 199 sorunun cevaplı 160'ı).
  5 kaynakla 1 doğrulanmış yanlış değer çıktı (B012, "bulunamadı" beklenen soru), 8 kaynakla
  0. Maliyet 0,0525 $'dan 0,0614 $'a çıktı.
- **Yeniden düşünülür:** Yalnız yeni ölçümle. Kaynak sayısını düşürmek bilinen bir
  doğrulanmış yanlışı geri getirmişti.

### Belge düğmesiyle seçilen belgede her sayfada geçen öbek sıralama sorgusundan çıkar (2026-11-26, `s1-dugme-obek`, ürün sahibi kararı)
- **Sorun (S1):** "Challenger Train Pant hangi bedenlerde üretiliyor" netleştirmede 6026412 düğmesiyle seçilince ilk 8'in 7'si sayfa başlığı satırıydı ("6026412 | UA W Challenger Train Pant | Images"), beden parçaları füzyonda 34–38. sıradaydı, cevap "bulunamadı". Ürün adı belgenin her sayfasında geçtiği için belge içinde ayırt edici değil; BM25'in IDF'i koleksiyon geneli olduğu için ağır basıyor.
- **Kural:** istek belge düğmesinden geldiyse (`doc_ids`, tek belge), sorgudaki en az iki sözcüklü bir öbek o belgenin sayfalarının yarısından fazlasında aynen geçiyorsa hem yoğun sorgudan hem BM25 sorgusundan çıkar (en uzun öbek önce; kesmeyle bağlı ek ayrılır, "Pant'ın"). Sorgu boş kalırsa özgün sorgu kullanılır. Modele giden soru değişmez. Sorudaki koddan ya da önceki turdan gelen kapsamda uygulanmaz. Sayfa metinleri snapshot kurulurken bir kez çıkarılır (`IdentifierIndex`, 6.295 parçada ≈20 ms); yeniden indeksleme yok. Öbek en çok 8 sözcük ve ancak iki alt öbeği de sıksa denenir: uzun soruda (300 sözcük) sayfa araması doğrusal kalır (inceleme turu; ilk sürüm sözcük sayısının karesiyle büyüyor, 300 sözcükte 15 sn sürüyordu). Türkçe I/ı i'ye katlanır. Soru kaydında `bm25_query` çevirinin kendisi olarak kalır; çıkarılmış sıralama sorguları ayrı alanda (`ranking_query`).
- **Neden öbek, sözcük değil:** tek sözcük kuralı ("a*", sayfaların yarısından fazlasında geçen her sözcük) beden harflerini ("m", "s", "l", dikim föylerinde), sayıları ve "sample"ı da siliyordu. Öbek listesinde içerik öbeği yok ("size range", "material details", "measurement chart" hiçbir belgede sık değil); en sık 40 öbeğin 34'ü sayfa üst ya da alt bilgisi, kalanı ürün adı. "ölçü föyü" dikim föylerinde sık (belgenin kendi adı, "PNT-1162 ölçü föyü"): ürün adıyla aynı türden sayıldı, kabul edildi. Önceki "a*" denemesi kod kapsamlı 3 soruyu kötüleştirmişti (Y09, C1, dikim etiketi); kural artık yalnız düğmeyle gelen kapsamda çalışıyor.
- **Ölçüm (Windows, çevrimdışı; uygulama indeksi 23 Kasım paketi, taban kopyaları 20 Kasım):** belge düğmesi seti (`evals/belge_dugmesi_seti.json`, 12 soru, ürün sahibi onayı; yalnız arama ölçümü) beklenen parça ilk 8'de 1/12 → 12/12 (S1 6. sırada). Kabul, yüklü sınır ve FastReact (66 soru), taban 7 ve 11 (33'er soru): ilk 8'i değişen 0.
- **Ölçümün yeniden üretimi:** set dosyası repoda, ölçüm betiği değil (tek seferlik; `retrieve` doc_ids ile çağrılır, çeviri önbellekten). İnceleme düzeltmesinden sonra yeniden ölçüldü: aynı sonuç (12/12; mevcut setlerde ilk 8'i değişen 0).
- **Bilinen sınırlar:** tek sözcüklü ürün adında kural uygulanmaz. Takip sorusu kapsamı miras aldığında kural uygulanmaz; tamamlanmış soru ürün adını yeniden taşıyabilir. Kumaş sorularında terim farkı sürüyor: kumaş satırı "Material Details: KNT-…" "fabric" sözcüğünü taşımıyor; sette M7 ve M10 öbek kuralıyla 3. ve 5. sıraya girdi, ama başka sorularda geride kalabilir (açık notlar).

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
    artırılıyor. Bu kayıt yazıldığında Excel (xlsx, xls), PDF, görsel ve Office 3'te; Markdown,
    metin ve SQL 2'deydi. 22 Kasım'da PDF ve Office 20, görsel 15, Excel 4, Markdown 3, metin ve
    SQL 2. Güncel sürümler ve her artışın gerekçesi `formats.py`'de (`RULES_VERSIONS` ve
    yorumları); bu kayıttaki sayılar güncellenmez.
    PDF, görsel ve Office 2: OCR kalite puanında tek büyük harf çöp sayılmaz. Office da
    2'ye çıkarıldı (ürün sahibi kararı), çünkü PDF'e çevrilip aynı OCR kararından geçiyor.
    PDF, görsel ve Office 3 (2026-11-13): yeniden işleme belgenin kayıtlı dilini ("tr") OCR'a
    veriyordu, OCR yalnız `tur` ile okunuyordu; ilk yükleme ise `tur+eng`. Aynı dosya iki yolda
    farklı okunuyordu (`dikim-foto`'da tolerans `1,0` yerine `10`). Artık OCR her işlemede
    `tur+eng`; katalog dili yine parçalardan belirlenir. Sürüm yalnız sayıya baktığı için
    sürüm 2'deki bütün PDF, görsel ve Office belgeleri (ilk yüklemede zaten tur+eng ile
    okunanlar dahil) "eski kural" görünür. Office de aynı yoldan etkilendiği için (taranmış
    sayfa ve gömülü görsel OCR'ı) ürün sahibinin kararıyla 3'e çıkarıldı.
  - Sonra (sürüm 7'den beri): `is_outdated` yalnız sayıya bakmaz. Bir geçiş yalnız belli sayfa
    türlerinin çıktısını değiştirdiyse yalnız o türden sayfası olan belge eskir
    (`_CHANGED_PAGE_KINDS`).
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
**Tarihsel kayıt.** Bu yol [0028](#karar-0028) ile kaldırıldı (OCRmyPDF, RapidOCR ve gömülü görsel
okuması); taranmış sayfalar 0011'den beri sayfa okuyucusundan geçiyor.

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

### Excel: altında satır olmayan başlık başlık değildir (2026-11-22, #136)
- **Sorun:** Tek dolu satırı olan sayfa (ör. yalnız A1'de "Not: tork 12 Nm") başlık satırı sanılıyor, hücre metni hiçbir parçaya girmiyordu (kural 3).
- **Kural:** Altında dolu satır olmayan başlık satırı başlık sayılmaz; hücreleri etiketsiz satır olarak yazılır ("Kod | (boş) | Tork"). Excel kural sürümü 5. Yüklü 3 Excel'in çıktısı değişmedi.
- **Tek sütunlu sayfa (2026-11-23, #140, ürün sahibi kararı):** hiçbir satırında birden fazla dolu hücre olmayan sayfa başlıksızdır; her hücre ayrı, etiketsiz satır ("Not 1: Not 2" oluşmaz). Bedel: gerçek başlıklı tek sütunlu liste ("Parça No" ve altında kodlar) etiketsiz yazılır, içerik korunur. Excel kural sürümü 6. Yüklü ve ölçüm setlerindeki 19 xlsx'in çıktısı değişmedi.

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
  - Bu repodaki karşılaştırma (35 soru, 7 model; Gemma 4 26B 33 geçti, 0 yanlış değer):
    tablo, sıralama ölçütü ve istemin Gemma'ya verdiği avantaj [0002](#karar-0002)'de.
  - Gemma 4 31B 25 geçti. Eski pilotta Crusoe sağlayıcısında 32 kesik cevap vermişti
    (`adim2/okuma_nihai_ara_2026-11-05.md`). Aynı tabloda 26B de Parasail'de 34 kesik
    veriyor; kesiklerin kaynağı modelden çok sağlayıcı.
- **Yeniden düşünülür:**
  - Model değişikliği yalnız ölçümle yapılır (kural 5). Ölçülemeyen adaylar 0002'de.
  - 2026-11-26 karşılaştırması (Haiku 5.5, Sonnet 5.5; ZDR): model değişmedi; aşağıda 0019'daki
    "Cevap modeli karşılaştırması".

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
| `#30f7268` (`s2-ayrik-alinti`) | Kural 2: uzak parçalar kısaltılıp birleştirilmez, aynı kaynak numarasıyla ayrı alıntı verilir | Etkisiz (S2 3 koşuda 0); `s2-niteleyici-alinti` ile geri alındı |
| `s2-niteleyici-alinti` (deneme cümlesi commit'lenmedi) | Önceki cümle yerine: "Cümlede bir niteleyici (renk, beden, varyant) iddia ediyorsan, onu gösteren hücreyi de aynı kaynaktan alıntıla." | Karar kuralını tutmadı (S2 5 koşuda doğrulanmış KNT-226131 0/5); iki cümle de çıkarıldı, istem 26 Kasım öncesi hâlinde (`a7d057b`) |
| `istem-turu` (birleştirilmedi) | Üç değişiklik: durum, ad ve etiket değerleri belgedeki yazımıyla (C1); birim değerin kendi sütun başlığındaysa yazılır (B8, örnek "Ücret (EUR): 37,25"); `parça="şekil"` tanımlandı. Ölçütler ölçümden önce sabit: C1 5/5 özgün ifade, B8 5/5 "TL", taban setlerinde kötüleşen yok, doğrulanmış yanlış 0 | Windows, 2026-11-26, canlı, ≈0,053 $: C1 5/5 ve B8 5/5 tuttu; taban 7 38/40 (20 Kasım 39/40; `dikim-revizyon-netlestir` netleştirmeyi atladı, iki revizyonu listeledi), taban 11 39/40 (aynı); yüklü sınır seti 5 koşuda D6 iki kez şablon aralığını ("Apparel (XS-5XL)") doğrulanmış gösterdi, D1 bir kez sürümsüz değer. Ölçüt tutmadı; istem yeniden denenmedi, birleştirilmedi. D6'nın yeni istemden mi kaynaklandığı ayrılmadı (eski istemle aynı sette karşılaştırma koşusu yapılmadı); taban karşılaştırması 20 Kasım Windows çıktısıyla, aynı gün eski istemle koşu yok. **#171 (istem turu; eski açık notlarda "S4 işi", dil sorusu S4'ten ayrı):** birleştirilmeden kapatıldı; ölçüt tutmadı (taban 7'de `dikim-revizyon-netlestir`, D6). D6 artık Kural E ile korunuyor (#172). İstem değişmeden dondurma (ürün sahibi kararı, 2026-11-26; [0031](#karar-0031)) |

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

### Soru dili: belirsizse Türkçe (2026-11-26, `dil-tespiti`)
- **Sorun:** "6029278'in ana asma etiketiyle insert kullanabilir miyiz" İngilizce sayıldı ve
  cevap İngilizce geldi (26 Kasım teşhisi, S4): Türkçe harf yok, "6029278'in" içindeki "in"
  İngilizce ipucu, "miyiz" Türkçe ipucu değil. Tablette Türkçe harfsiz yazmak yaygın.
- **Kural (`language.py`):** kesmeyle bağlanan ek sözcük sayılmaz ("6029278'in", "FastReact'ı";
  İngilizce kısaltmanın kuyruğu zaten ipucu değil); soru eki ailesi ("mi", "miyiz", "musunuz",
  "midir") Türkçe harfsiz yazılışıyla da Türkçe ipucudur. "en" için iki yoldan biri gerekir:
  Türkçe soruda Türkçe harfsiz yazılsa da geçmeyen güçlü bir İngilizce sözcük (which, what,
  where, when, why, who, how, does, did, the, should, would, could, there, this, these, those,
  your, please) ve hiç Türkçe ipucu olmaması; ya da en az iki İngilizce ipucu ve İngilizce
  ipucunun Türkçeden fazla olması. "is", "can", "in", "on" gibi Türkçe harfsiz yazımla
  karışanlar güçlü kümede değil. Tamamı büyük harfle yazılmış sözcük güçlü sayılmaz (Türkçe
  sorudaki SQL anahtar sözcüğü: "WHERE", "WHEN"). İkisi de yoksa "tr". Türkçe harf yine kesin "tr". Güçlü küme
  yalnız soru dili içindir; belgenin dili (`document_language`) değişmedi.
  Ürün sahibi kararı: İngilizce sorulan soru İngilizce cevaplanır ("Which table stores order
  items?", "Where's the CPU temp?" İngilizce); ilk sürümdeki "tek ipucu yetmez" bedeli kabul
  edilmedi.
- **Etki:** soru günlüğünde (2.189 kayıt) ve bütün ölçüm setlerinde (kabul, yüklü sınır,
  FastReact, taban 7 ve 11, sentetik sınır) kararı değişen tek soru S4 (iki yazılış, günlükte
  6 kayıt; en → tr). Güçlü küme ve büyük harf kuralıyla yeniden karşılaştırıldı; değişen yine
  yalnız S4. Setlerde İngilizce soru yok. Dili değişen soruda çeviri devreye girer;
  doğru parça (#78) iki yazılışta da ilk 8'de 1. sırada kaldı.
- **Seslendirme:** ses cevabın dilinde, yani tamamlanmış sorunun dilinde okunur (2026-11-26,
  `speak-soru-dili`). `/speak` ucu dili arayüzün gönderdiği sorudan (takipte tamamlanmış hali)
  tespit eder; önceden cevap metninden tespit ediyordu ve güçlü sözcük taşımayan kısa İngilizce
  cevap ("It is 32 cm.") Türkçe kurallarla okunuyordu ("It is otuz iki santimetre"). Soru
  gönderilmezse eski davranış. `/ask`'in akan sesi de takip sorusunda dili tamamlanmış sorudan
  alır (önceden ham sorudan: İngilizce sorunun takibi "ve L?" Türkçe okunurdu).
- **Bedel:** Hiç güçlü sözcük ve iki ipucu taşımayan İngilizce soru ("Can I export?") Türkçe sayılır.
  Türkçe ipucu taşımayan Türkçe harfsiz bir soruda marka ya da özellik adı ("The North Face
  ceket beden tablosu", "What If analizi") ya da yapıştırılmış İngilizce metin ("Please wait
  hatasi aliyorum") soruyu İngilizce yapar; Türkçe ipucu listesi kısa olduğu için (16 sözcük)
  bu olası. Günlükte (2.189 kayıt) böyle bir soru yok.

## Doğrulama

### Doğrulama yalnız kodla yapılır; LLM hakem yok
- **Ne zaman:** 0001. Eski pilot `docs/MIMARI.md` B2.1.
- **Neden:**
  - Eski pilot LLM hakemini ve ajanlı RAG'ı öngörülemez buldu. Küçük modeller tek bir
    talimatı bile tutarlı izlemedi.
  - Ölçümde de cevaplar LLM ile puanlanmaz.
- **Yeniden değerlendirildi (2026-11-26, `llm-hakem-karari`, ürün sahibi kararı): karar sürüyor.**
  - **Ölçüm:** yardımcı model (Gemma, Parasail, ZDR) sıcaklık 0'da hakem olarak denendi. Soru:
    cümle, alıntılanan satırın söylediğini mi söylüyor? Hakeme soru, cümle, alıntılanan satır ve
    aynı belgeden kardeş satırlar verildi. Set 40 etiketli çift (15 yanlış, 25 doğru), her çift
    5 kez soruldu: 200 çağrı, 0 hata, 0,0141 $. İstem, set ve betik `evals/hakem_seti.py` içinde.
    Set geçici; gerçek belgelerle büyütülecek.
  - **Kategoriler:**
    - T1: Kural D adayı, tek varyantlı satır.
    - T2: Kural E adayı, önekli etiket.
    - T3: Türkçe cümle, İngilizce ölçü satırı ("Description:" hücreli satır).
  - **Tetik sayımı (çevrimdışı):** günlükte ham çıktılı 168 cevaptaki 188 cümle.
    - T1: 4 cümle, hepsi zaten gizli.
    - T2: 9 cümle (6 gösterilen, 3 gizlenen).
    - T3: 11 cümle (2 gösterilen).
    - Taban 7 ve 11'de üçü de 0. FastReact'ta T3 5 cümle; bunlar alan tabloları, tanım fazla geniş.
    - Hakem cevapların %5'inde çağrılırdı (T1 ve T2), T3 eklenirse %11'inde.
  - **Sonuç:** yakalama = yanlış çiftte çoğunluk "uyumsuz"; kurtarma riski = en az bir "uyumlu"
    alan yanlış çift; yanlış veto = doğru çiftte çoğunluk "uyumsuz". p95, çağrı başına
    (`percentile`).

    | Kategori | Yakalama | Kurtarma riski | Yanlış veto | Tutarsız çift | p95 |
    |---|---|---|---|---|---|
    | T1 | 3/3 | 0 | 0/5 | 0 | 1,24 sn |
    | T2 | 0/6 | 6 | 0/8 | 0 | 1,11 sn |
    | T3 | 6/6 | 0 | 0/12 | 0 | 1,65 sn |
    | Toplam | 9/15 | 6 | 0/25 | 0 | 1,43 sn (p50 0,85) |

    - Ölçütler ölçümden önce yazıldı:
      - Veto: yakalama ≥ %80, yanlış veto ≤ %5, p95 ≤ 1 sn.
      - Kurtarma: yanlış çiftte hiç "uyumlu" yok, ayrıca veto ölçütleri.
    - Hiçbir kategoride tutmadı. T1 kurtarması yalnız p95'te kaldı (1,24 sn); öteki maddeler
      tuttu. Gelecekteki kurtarma ölçütünde p95 yok: süre dolarsa cümle gizli kalır (karar 2,
      ürün sahibi kararı, ölçümden sonra).
    - T2'de hakem "Chart Size Range" ile "Size Range"i ayırmadı: altı yanlış çiftin hepsine
      5/5 "uyumlu" dedi.
  - **Kararlar:**
    1. Veto yok. T2'de yakalama %0 (Kural E kalır). T1 cümleleri zaten Kural D ile gizli. T3'te
       gösterilen cümle nadir ve gecikme bedeli yüksek.
    2. Kurtarma şimdilik yok. T1'de umut verici: 3 yanlış çiftte 0 yanlış "uyumlu", #60 (yaka
       ribanası) doğru ayrıldı. Ama örneklem küçük ve Kural D tetiği bugünkü föy biçimine
       bağlı. Kurtarmada süre dolarsa cümle gizli kalır; bu yüzden gecikme ölçütü veto kadar
       bağlayıcı değil.
    3. T3 kapsama alınmaz. İleride ölçülecekse tanım, FastReact alan tablolarını dışarıda
       bırakacak biçimde daraltılır.
    4. Set geçici onaylı. T1 ve T3 gerçek hatalardan çiftlerle büyütülecek.
  - **Yeniden açılma koşulu:** gerçek belgelerde varyant tabloları görülünce T1 kurtarması,
    büyütülmüş setle yeniden ölçülür (açık notlar, "Gerçek belgeden sonra").
    - S2 (niteleyici hücresi) güvenli bilinen sınır olarak kalır.
    - #2375 (Kural E, sınır a) da güvenli bilinen sınır olarak kalır.
- **Yeniden düşünülür:** Anlam düzeyindeki boşluklar (olumsuzlama, yanlış sütun) biçim
  kuralıyla kapanmıyor (açık notlar). Ayrı tasarım gerekir.

### U+2010 ve U+2011 kısa tire okunur (2026-11-22, #136)
- `canon_chars` iki tireyi kısa tireye çevirir; `prefixed_codes_in` da aynı biçimde okur. Word'ün bölünmez tiresiyle yazılmış kod ("PNT‑1162") kod olarak tanınır; kaynaktaki "‐5" eksi olarak okunur (önce "5" okunuyor, cevaptaki "5" doğrulanıyordu: küçük bir kural 1 açığı kapandı). U+2012 ve U+2013 eklenmedi: – zaten aralık ve eksi işareti olarak ele alınıyor, "M8–M10" tek ad olurdu.
- Docling yolunda kod taşıyan sayfa üst bilgisi de bu yazımı tanır; PDF ve Office kural sürümü 22. Yüklü veride bu karakter 0.
- BM25 normalleştirmesi de U+2010 ve U+2011'i kısa tireye çevirir (2026-11-23, #140, ürün sahibi kararı; okumayla aynı). Yüklü veride bu karakter 0, vektörler değişmedi.

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
- Cümle başındaki "sayı + nokta" ("30. Gün içinde") liste numarası sayılıp denetimden çıkıyordu; artık değer gibi denetlenir. Kaynağın liste numarası yalnız aynı numarayı aynı sözcükle karşılar ("2. Bekleyin" adımı "2. Gün"ü karşılamaz), değer olarak geçen sayıya dayanak olmaz. Netleştirme sorusundaki "30. Gün" de kullanıcının söylemediği değer sayılır (2026-11-23, mimari raporunda doğrulanan kural 1 açığı). Önbellekten ölçüm: taban 7 ve 11 (33+33) ile FastReact (18) cevapları önce ve sonra birebir aynı.

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
- **Taranmış aday (2026-11-22, dal `ortak-cevap-tarama-rozeti`; ürün sahibi kararı).** Diğer
  adayda eşleşen parça taramadan okunduysa (sayfa okuyucusu) cevap yine verilir ama "kısmen
  doğrulandı" kalır, rozeti "Taramadan okundu" olur; önceden "doğrulandı" çıkıyordu
  (`ask/agreement.py`, 0022'nin kod incelemesinde bulundu). Dijital adayla eşleşen cevap
  "doğrulandı" kalır; eski OCR yolundan okunan aday eşleşme sayılmazdı (0022; yol 0028 ile
  kaldırıldı). Alıntıdaki
  değeri taranmış adayda belirsiz okunmuşsa o aday da eşleşme sayılmaz, netleştirme kalır (tek
  belgede cümle gizlenirdi; kod incelemesinde bulundu, bu dalda kapatıldı). İlk aday
  taranmışsa eskisi gibi netleştirme sorulur (ilk adayın cevabı tam doğrulanmış olmalı).
  Bugünkü veride bu yoldan geçen cevap yok: Mac soru günlüğünde iki ve daha çok belgeye atıflı
  91 doğrulanmış cevabın hiçbiri taranmış belgeye atıf yapmıyor; taban 7 ve 11'de iki belgeye
  atıflı cevap yok. Ölçüm (Mac, bugünkü taban `eski-yol-2026-11-21`; önbellekten, ağa
  gitmeden): iki set 39/40, doğrulanmış yanlış 0, kırk sorunun kayıtları ve rozetleri
  öncekiyle aynı. Bilinen: diğer adayda alıntı hem taranmış hem dijital parçada geçiyorsa
  arama sırasında önde olan belirler (kısmen doğrulandı ya da doğrulandı; ikisi de güvenli).
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
- **Ürün ya da model değişince beden taşınmaz; aynı ürünün sürümü değişince taşınır
  (2026-11-21, ürün sahibi kararı; dal `urun-degisince-beden`).** Takip sorusu başka bir
  ürünü ya da modeli adlandırıyorsa önceki turun bedeni tamamlanmış
  soruya girmez; sistem bedeni sorar. Eski "bilinen kalan" (`dikim-sohbet-1-t4`, 10 tekrarın
  hiçbirinde geçmedi) bununla kapandı: beklenti değişti, davranış değil.
  - **Teşhis.** Tamamlama yalnız bağlamdaki tek soruyu ve yeni mesajı görür
    (`ask/context.py`); cevap modeli önceki turları hiç görmez. Konuşma: "PNT-1126 M beden iç
    paça 74,0 cm miydi?", "Peki dış paça kaç?" (beden taşındı), "Peki kordon boyu kaç?"
    (bulunamadı; bağlam değişmedi), "Peki PNT-1162 modelinde iç paça kaç?". Dördüncü turda
    yardımcı modelin gördüğü önceki soru "PNT-1126 M beden dış paça kaç?" idi, yani beden
    önündeydi; araya giren tur bağlamı kesmiyordu. Aynı girdiyle 3 çağrının 3'ünde ve dört
    Türkçe değişkenin dördünde beden düştü; istemdeki örneğin Türkçesinde de. Beden yalnız
    istemdeki İngilizce örneğin kendisinde korundu. `is_grounded` yalnız uydurulan değeri
    yakalar, düşen sözcüğü fark etmez.
  - **Gerekçe.** Kural 1: taşınan beden sorulmamış bir bedenin değerini kendinden emin
    verdirir (kullanıcı yeni ürünün başka bir bedenini ya da hepsini kastetmiş olabilir).
    Davranış dile göre değişiyordu (İngilizcede taşıyor, Türkçede düşürüyordu). Taşımak hiç
    ölçülmüş bir karar değildi: ilk sürümden (`#fcab57c`) beri istemde yazılıydı.
  - **Değişen.** Tamamlama isteminden "ürün, model ya da sürüm değişince önceki sorunun
    bedenini koru" cümlesi ve örneği çıkarıldı (`generation/rewrite.py`); sonrasında İngilizce
    örnek de bedensiz tamamlandı (tek çağrıyla denendi; yardımcı model `gemma-4-26b`). Senaryo üreticisinde (`evals/scenarios/sewing.py`)
    `dikim-sohbet-1-t4`'ün beklentisi netleştirme oldu; taban 7 ve taban 11 yeniden üretildi,
    `gold.json` dosyalarında yalnız bu turun beş alanı değişti. Kod davranışı değişmedi.
  - **Bedeli.** Kullanıcı bir tur fazla yazar ve tek belgede netleştirme seçeneksizdir
    ("Hangi beden için?"; 0020). Ürün değişmeyen takiplerde beden taşınmaya devam eder
    ("L beden?" → "Etiketi ne?").
  - **Ölçüm (Mac, 2026-11-21; dalın koduyla, karşılaştırma `evals/output/mac-main-2026-11-21`).**
    Taban 7 ve taban 11: 39/40 (main 38/40), doğrulanmış yanlış 0, haksız ret 0; takip
    soruları 5/5 (main 4/5). Değişen tek soru `dikim-sohbet-1-t4`: cevap aynı (netleştirme),
    beklenti değişti. Öbür dokuz takip turunun tamamlanmış sorusu iki sette de main ile
    birebir aynı; konuşma dışı 30 sorunun cevabı da aynı (cevap modeli çağrıları önbellekten;
    yalnız tamamlama çağrıları canlı). Kalan tek soru iki sette de `sql-ekran-uzunluk` (ekran görüntüsünden okunan değer).
    Açık cümle eklendikten sonra yeniden ölçüldü: iki set yine 39/40, doğrulanmış yanlış 0.
    Takip turlarından birinin tamamlanmış sorusu sözcük düzeyinde değişti (`sql-sohbet-1-t2`:
    "yeni bir kolon eklerken" → "yeni kolon eklerken"); cevabı aynı komut, doğrulanmış.
    Öbür turların tamamlanmış sorusu main ile aynı. Daraltılmış cümleyle üçüncü ölçüm aynı
    sonucu verdi (39/40, doğrulanmış yanlış 0; tek fark yine `sql-sohbet-1-t2`'deki sözcük,
    kabul edildi).
  - **İsteme açık cümle (ürün sahibi kararıyla ek, tek düzeltme turunun dışında).** İnceleme
    bulgusu: cümle çıkınca davranış istemde yazılı kalmamıştı; kalan cümleler harfiyen
    okununca bedeni taşıtıyordu ve bedenin düşmesi yardımcı modelin eğilimine dayanıyordu.
    Eklendi: "When the new message names another product or model, do not carry over the size
    of the previous question" ve örneği.
  - **Sürüm: beden taşınır (karar daraltıldı, 2026-11-21).** İlk yazımda cümle sürümü de
    kapsıyordu ("product, model or version"). Yardımcı model sürümde uymadı: "SRT-4294 Rev B M
    beden iç paça kaç?" → "Peki Rev A?" Türkçe ve İngilizce 6 çağrının 6'sında "SRT-4294 Rev A
    M beden iç paça kaç?" oldu. Karar buna göre daraltıldı ve istemden "or version" çıkarıldı;
    istem davranışla aynı. Gerekçe: kullanıcı büyük olasılıkla aynı bedeni aynı ürünün başka
    revizyonunda soruyor; ürün aynı kaldığı için sorulmamış bir ürünün değeri verilmiyor ve
    "Anlaşılan soru" ekranda gösteriliyor. Bedeli: kullanıcı öbür revizyonun başka bir
    bedenini kastettiyse M'nin değeri verilir; ekrandaki tamamlanmış sorudan görür.
  - **Deneme (yardımcı model, her durum 3 çağrı; sürümü de kapsayan ilk cümleyle).**

    | Durum | Önceki soru → yeni mesaj | Çıktı (3/3) |
    | --- | --- | --- |
    | TR ürün değişti | "A-100 M beden genişlik kaç?" → "Peki B-200?" | "B-200 genişlik kaç?" |
    | EN ürün değişti | "What is the width of A-100 in size M?" → "And B-200?" | "What is the width of B-200?" |
    | TR ürün ve ölçü değişti | "PNT-1126 M beden dış paça kaç?" → "Peki PNT-1162 modelinde iç paça kaç?" | "PNT-1162 modelinde iç paça kaç?" |
    | TR sürüm değişti | "SRT-4294 Rev B M beden iç paça kaç?" → "Peki Rev A?" | "SRT-4294 Rev A M beden iç paça kaç?" |
    | EN sürüm değişti | "What is the inseam of SRT-4294 Rev B in size M?" → "And Rev A?" | "What is the inseam of SRT-4294 Rev A in size M?" |
    | TR ürün aynı | "A-100 M beden genişlik kaç?" → "Peki dış paça?" | "A-100 M beden dış paça kaç?" |
    | EN ürün aynı | "What is the width of A-100 in size M?" → "And the height?" | "What is the height of A-100 in size M?" |
    | TR yalnız beden değişti | "CKT-7308 S beden bel kaç?" → "L beden?" | "CKT-7308 L beden bel kaç?" |

    Daraltılmış cümleyle aynı sekiz durum üçer kez yeniden denendi: çıktılar tablodakilerle
    birebir aynı (24 çağrının 24'ü). Ürün değişince beden düşüyor, sürüm değişince ve ürün
    aynıyken taşınıyor; istem ile davranış artık aynı.
  - **Bilinen sınırlar (inceleme turu).** (1) Bu tur artık her netleştirmeyle geçer;
    tamamlama hatasından gelen netleştirme de ("soruyu birleştiremedim") geçer sayılır.
    Ölçümde tamamlanmış soru elle doğrulandı: iki sette de model var, beden yok. (2)
    `evals/baselines/taban` altındaki eski özetler (2026-11-23'te silindi; git geçmişinde) bu
    turu hâlâ kalan soru sayıyordu; 38 → 39
    iyileşme değil, beklenti değişikliğidir.

### Gizlenen cevabın turunda da kullanıcının sorusu bağlama girer (değiştirildi)
- **Ne zaman:** 2026-11-12, `sohbet-baglami` dalı, `ask/context.py` (`next_context`).
- **Kural:**
  - Takip sorusu kullanıcının önceki sorularından tamamlanır.
  - Gizlenen ya da doğrulanmamış cevap bağlama girmez. Cevabın kendisi zaten hiç girmiyor;
    belgeler yalnız doğrulanmış cümlelerin kaynaklarından gelir.
  - Cevap gizlense de kullanıcının o turdaki (tamamlanmış) sorusu bağlama girer. Belgeler o
    turda gerçekten aranan belgelerdir: tur yeni bir kodla arandıysa kodun belgeleri
    (aşağıdaki "Sorudaki kod aramayı kodun belgelerine daraltır"), kod çok belgede geçtiği için
    bütün belgelerde arandıysa kapsam boştur.
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

### Sorudaki kod aramayı kodun belgelerine daraltır
- **Ne zaman:** 2026-11-20, `kod-kapsami` dalı; ekip kararı (tasarım onaylı).
- **Kural:**
  - Belge seçilmemiş, soruda belge adı geçmiyor ve önceki turdan kapsam gelmiyorsa, sorudaki
    kodların geçtiği belgeler kapsam olur (`resolve_scope`, `_code_documents`).
  - En çok 4 belgede geçen kod daraltır: netleştirme düğmesi sınırıyla aynı
    (`_MAX_CLARIFY_DOCUMENTS`), kapsam netleştirilebilir kalır. Daha çok belgede geçen kod
    (ortak bileşen kodu, ör. bütün tech pack'lerdeki iplik) daraltmaz.
  - Birden çok kodda daraltan kodların belgeleri birleşir; birleşim 4'ü aşarsa daraltma yok.
    Hiçbir belgede olmayan kodun davranışı aynı ("X belgelerde geçmiyor").
  - Daraltma önceki turdan miras değildir (`scope_inherited` değişmez); sonuç
    `scope_narrowed` taşır.
  - Kodla daraltılan turda "bulunamadı" çıkarsa arayüz mevcut "Tüm belgelerde ara" düğmesini
    gösterir. Düğme `all_documents` işaretiyle gönderilir; o soruda kod daraltmaz. Kendiliğinden
    yeniden arama yok.
- **Neden:** 20 Kasım teşhisi: "GML-6473 modelinde M beden bel kaç" sorusunda kod yalnız
  dikim-tarama'da geçtiği hâlde arama bütün belgelerde yapıldı; ilk 8 parçaya PNT-1126'nın bel
  satırı girdi ve model iki ürünün değerini "çelişki" diye birlikte yazdı.
- **Ölçüm (2026-11-20):**
  - n11 önbelleğinden çevrimdışı: kapsamı değişen yalnız SQL soruları (set başına 7; kolon
    adları SQL belgelerine daraltıyor). Kumaş, dikim ve FastReact soruları değişmedi.
  - Canlı: taban 39/40 ve 39/40 (yalnız bilinen `dikim-sohbet-1-t4`), FastReact 17 sorunun
    cevabı n11 ile aynı, doğrulanmış yanlış 0; `sql-netlestir` iki sette de netleştirme.
  - "GML-6473 modelinde M beden bel kaç?" 5/5 yalnız dikim-tarama'dan, 38,0, çelişki notu yok.
  - Sınır seti 24 × 5: D2 (MNT-8598, fotoğraf) "bulunamadı"dan 5/5 doğru değere (40,0); A4 bir
    gizlenen koşudan 5/5 doğruya. Diğer sorular n12 ile aynı sınıfta.
  - D1 ("SRT-4294 M beden bel kaç?"), sınır setinde 3/5 netleştirme, 2/5 yalnız Rev B'nin
    değeri (revizyon adı yok). Aynı soru sırayla 10'ar kez: daraltmalı 9 netleştirme, 1 iki
    revizyon birlikte (Rev B cümlesi revizyon adı taşımıyordu); "tüm belgelerde" 3 netleştirme,
    6 iki revizyon birlikte, 1 servis hatası. İki kipte de tek revizyon 0. Sonuç: daraltma D1'i
    kötüleştirmiyor; sınır setindeki atlama model değişkenliği.
  - Maliyet: canlı ölçümler toplamı ~0,038 $.
- **Bilinen sınırlar:**
  - Revizyon belirtilmeyen soruda netleştirme bazen atlanıyor (PR öncesinde de var): model
    tek revizyonun değerini revizyon adı olmadan verebiliyor (D1, sınır setinde 2/5).
  - Kod bir belgede, cevap başka bir belgedeyse ilk tur "bulunamadı" der; kullanıcı "Tüm
    belgelerde ara"ya basmalıdır.
  - Kod sayılan her ad daraltır: SQL kolon adları (`MUSTERI_KODU`), küçük harfli alt çizgili
    adlar, "A4", "UTF-8" gibi terimler de.

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
- **Neden ve nasıl:** [0003](#karar-0003), "Neden SQLite" (yönetici yetkisi, küçük yük,
  sunucuda da aynı kod, WAL kipi, Postgres'e dönülürse değişecek tek dosya).
- **Yeniden düşünülür:** Yük büyürse ya da sunucuda çok işçi gerekirse.

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
- **Kayıt:** [0017](#karar-0017) (ne kalktı, neden, geri alma). 0003'te "sunucu için kalır"
  denmişti; 2026-11-19'da kaldırıldı.
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
  (açık notlar, "Canlıya alırken").

### Yükleme yarım kayıt bırakmaz (2026-11-22, #136)
- SQLite bağlantısı autocommit ve yazma iş parçacığında: istek iptal edilse de kayıt yazılıyor, klasör siliniyordu (dosyasız kayıt, "işlenemedi"). Artık yazma korunur; hata ya da iptalde yazmanın bitmesi beklenir, kayıt mevcut `delete_document` ile silinir, sonra klasör; temizlik tek, korunan bir görevde (ikinci iptal yarıda bırakmaz, silme hatası asıl hatayı örtmez).

### Belgeler panelindeki "net okunamadı" sayısı sayfa başına tekil değer (2026-11-22, #137)
- Başlıkta belirsiz okunan değer doğrulama için altındaki her parçaya taşınıyor; rapordaki sayı parçalardan toplandığı için aynı değer yüzlerce kez sayılıyordu (föylerde 8.690 değerin 2.203'ü dört başlık parçasının tekrarı). Artık öğelerden, sayfa başına tekil değer sayılır. Parçalar ve doğrulama değişmedi. Mac'te yeniden işlemeden sonra toplam 3.776. Eski kayıtlardaki sayılar (ör. 0006'daki "397 → 16") eski yöntemle.

### Soru kaydı: tanının türü ve ayrıntısı ayrı sütunlarda
- **Ne zaman:**
  1. `57d4e77` (2026-11-10): tanılar yalnız türleriyle yazıldı; eski kayıtlar türe indirildi.
  2. 2026-11-20, `gunluk-sorun-ayrintisi` dalı; ekip kararı.
- **Ne:** `problems` yalnız türleri tutar (özet ve sayım). `problem_details` tam tanıyı
  tutar: gizlenen cümlenin doğrulanamayan sayısı, adı, kodu ya da kaynak numarası.
- **Neden:** 20 Kasım teşhisinde hangi sayının gizlemeye yol açtığı kayıttan okunamadı;
  cevap yeniden kurguyla bulundu.
- **Sınır (2026-11-26'ya kadar):** Cevap cümlesi yazılmıyordu. İstemciye yalnız türler gider;
  kaydın HTTP ucu yok. Saklama süresi açık notlarda ("Canlıya alırken").
- **Değişti: teşhis alanı (2026-11-26, `gunluk-teshis-alanlari`, ürün sahibi kararı).** Her
  kayda tek bir JSON sütunu (`diagnosis`) eklendi: BM25'e giden sorgu ve çevrilip
  çevrilmediği, cevap dili, modele giden soru metni, ilk 8 parça (sıra, parça kimliği, belge,
  sayfa), **modelin ham çıktısı (alıntılar dahil)**, `doc_ids`, sorunun nereden geldiği (yazılı,
  takip, belge düğmesi, "Tüm belgelerde ara" düğmesi) ve netleştirme adayları. Önceki kayıtlarda
  alan boş (`{}`); okuma bozulmaz.
  - **Neden (yeni kanıt):** 26 Kasım teşhislerinde üç bulgu kayıttan okunamadığı için çıkarımda
    kaldı: S2'de modelin alıntısı ("alıntı [1] kaynakta birebir değil" denen metin), S3'te
    BM25'e giden çeviri, "MD ön ağ" sorusunda doğru satır 6. sıradayken modelin neden
    "bulunamadı" dediği ve hangi çeviriyle arandığı. "Gerçek tanı günlükten okunmadan düzeltme
    yapılmaz" ilkesi (0019 notu) ancak bu alanlarla uygulanabilir.
  - **Bedel:** kayıt başına yaklaşık 1–2,5 KB (önce ≈ 0,5 KB). Ham çıktı belge alıntısı taşır;
    saklama süresi "Canlıya alırken" kararına bağlıdır. Ses yine yazılmaz; ortak cevap
    denemesinin (aynı cevap veren adaylar) ikinci model çağrısının çıktısı yazılmaz.
  - **Okuma:** `python -m apps.api.question_log --last 5 --teshis`.
  - **Gösterilmez:** teşhis alanı kullanıcıya gösterilmez (HTTP ucu yok). Ham çıktı doğrulamada
    gizlenen, doğrulanmamış değerleri de taşır; ileride kayda okuma ucu açılırsa bu alan dışarıda kalmalı (kural 1).

## Arayüz

### Tek açık tema; koyu tema kaldırıldı (geçersiz)
- **Durum:** Geçersiz. Yerini 2026-11-16'daki "Çalışma alanı düzeni" kaydı aldı (lacivert zemin,
  krem ve beyaz kartlar; aşağıda). Tarihsel kayıt olarak duruyor.
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
  bento karolar (büyük mercan "Sesli sor", krem "Yazarak sor", beyaz "Belge ekle"). Konuşma
  modundaki küre 2026-11-20'de ses halkasıyla değişti (aşağıda).
- **Nasıl:** `App.css`, `App.tsx`'te açılış durumu, `LandingActions.tsx`'te karo sınıfı ve ok
  simgesi. Metinler ve erişilebilirlik adları değişmedi. Harici yazı tipi yok.
- **Denenmedi:** atölye ışığında koyu zeminin okunurluğu; konuşma modu yalnız stil olarak
  değişti, mikrofonla denenmedi.
- **Sonra:** 22 Kasım arayüz yenilemesi açılış karolarını, belgeler panelinin açık başlamasını
  ve `App.css`'i değiştirdi (aşağıda, "Arayüz yenileme").

### Sesli mod ve cevap kartı tasarımı
- **Ne zaman:** 2026-11-20, `arayuz-sesli-tasarim` dalı; ürün sahibinin tasarımı ve kararları.
- **Ne:** Sesli mod tam ekran, iki sütun (dar ekranda alt alta): ses halkası (dinliyor, bakıyor,
  konuşuyor, anlayamadı) ve "Duyduğum" paneliyle cevap kartı. Yazı tipi sistem, tema yalnız
  koyu (16 Kasım kararı aynı).
- **Kurallar (yalnız görünüm; doğrulama, arka uç durumu ve ses akışı aynı):**
  - "Anlayamadı" akış durumu değil: dinlerken son kayıt yazıya çevrilemediyse görünür; dinleme
    sürdüğü için mikrofon kapalı çizilmez, "Tekrar dinle" düğmesi yok.
  - Büyük değer yalnız doğrulanmış dijital, çelişkisiz cevabın tek cümlesinde tek düz sayı
    varsa. Taramadan okunan cevapta değer cümlede normal boyutta kalır (2026-11-20, ürün sahibi:
    iki okuyucunun ortak hatası doğrulayıcıdan geçebilir; büyük punto kontrol edilmemiş güven
    verir). Rakam taşıyan sözcüklerden biri düz sayı ya da tireli kod
    değilse ("1-5", "M8x1,25", "27½", "−5", "%15") büyük değer gösterilmez.
  - Doğrulanamayan cevapta en az bir cümle gösterildiyse rozet "Kısmen doğrulandı · N cümle
    gizlendi"; hiçbiri gösterilmediyse "Doğrulanamadı".
- **Bilinen sınır:** Cümledeki tek düz sayı cevabın kendisi olmayabilir ("Rev 2", boşluklu kod
  "GML 6473"); değer büyük, cümle altında görünür.

### Arayüz yenileme: sade açılış, belgeler menüsü, duyarlı tasarım, Title Case düğmeler
- **Ne zaman:** 2026-11-22, `arayuz-yenileme` dalı; ürün sahibi isteği. 16 Kasım kaydındaki
  "bento karolar (… krem 'Yazarak sor' …)" ve "metinler ve erişilebilirlik adları değişmedi"
  cümlelerinin yerini alır. Renk paleti ve sistem yazı tipi aynı (harici yazı tipi yok).
- **Ne değişti (yalnız `apps/web`; doğrulama, ses döngüsü, sunucu ve RAG aynı):**
  - **Açılış:** "Yazarak Sor" karosu kalktı (yalnız üstündeki soru kutusuna odak veriyordu); soru
    kutusu asıl yol, büyük mercan "Sesli Sor" ve sakin "Belge Ekle" kaldı. Mikrofon yoksa "Sesli
    Sor" görünmez. "N belge hazır" hapı kalktı: sayı "Belgeler" düğmesinde; durum satırı yalnız
    hata, işlenen belge ya da hiç belge yokken ("Henüz belge yok.") görünür.
  - **Belgeler menüsü:** kayarak açılır, içerik kısa bir kademeyle oturur (yalnız dönüşüm ve
    opaklık; yeniden çizimde tekrarlanmaz). Satırlar kutusuz; "Yeniden İşle" ve "Sil" ince
    imleçte üstüne gelince ya da odakla belirir, dokunmatikte hep görünür (48 px). Grup sayısı
    çip değil düz rakam. 1080 px altında menü iletişim kutusudur (`role="dialog"`, Tab içeride
    döner); üstünde sayfanın parçası.
  - **Düğme adları Title Case** ("Ana Sayfa", "Yeniden İşle", "Tüm Belgelerde Ara"); durum
    metinleri, ipuçları, rozet ve uyarı metinleri değişmedi. Sesli modda iki ipucu genişledi:
    "Kaynaklarda arıyorum. Vazgeçmek için halkaya basın." ve "Araya girip konuşursanız ya da
    halkaya basarsanız susarım."; başlık "Sesli mod" (", eller serbest" kalktı).
  - **Rozetler:** doğrulama, "Taramadan okundu", gizlenen cümle ve belge durumu rozetleri aynen
    duruyor; durum rozetine simge eklendi (onay, ünlem, çarpı: yalnız renkle anlatılmaz). Süs
    niteliğindeki sayı çipleri ve "BAĞLAM" etiketi sadeleşti.
  - **Büyük değer** asla satıra bölünmez ve kesik görünmez: yazı, değerin bütün karakterleri
    karta sığacak kadar küçülür (320 px'te 10 haneli sayı sığar; kod incelemesinde bulundu,
    eskiden kart dışına taşıyor ya da kesik görünebiliyordu).
  - **Duyarlı tasarım:** 320–1920 px. Sesli modda yerleşim pencereye değil kendi alanına bakar
    (telefon yatayda yan yana, dikeyde alt alta; halka boyutu akışkan).
  - **Sesli moddan çıkış:** sol üstteki düğme "Sesli Modu Kapat" (çarpı simgesi; önce "Ana
    Sayfa" ve ev simgesiydi). Uzun ad 375 px'te ikinci düğmeyi ekran dışına itiyordu; düğmeler
    alan 28rem'in altına inince yalnız simge olur (önce 21rem). Pay, sistem yazı tipinin
    Windows ve Android'de daha geniş olabileceği için bırakıldı.
  - **Onay penceresi:** "Yeniden İşle" ve "Sil" artık sorar (`ConfirmDialog.tsx`; tarayıcının
    `confirm` kutusu kalktı). Yeniden işleme tek dokunuşla başlıyordu; belgeyi baştan okur,
    parçalarını ve arama dizinini yeniler, taranmış belgede dakikalar sürer. Odak "Vazgeç"te
    başlar, Escape pencereyi kapatır (arkadaki menüyü değil). Kapanışı da animasyonludur (karar
    animasyon bitince bildirilir); 640 px altında alttan açılan sayfadır.
  - **Belgeler paneli kapalı başlar** (geniş ekranda da): 16 Kasım'daki "belgeler paneli açık
    başlar" maddesinin yerini alır; açılış soru kutusuna ayrılır, liste "Belgeler" ile açılır.
  - **Düğme simgeleri:** ortak `Icon.tsx` (çizgi simgeler, ekran okuyucuya okunmaz): "Kapat",
    "Belgeler", "Belge Ekle", "Yeniden İşle", "Sil", "Yeni Konu", "Tüm Belgelerde Ara", "Tekrar
    Söyleyeceğim" ve onay penceresinin düğmeleri. "Sor" simgesiz kaldı (dar telefonda yer yok).
  - **Marka ve atmosfer:** sol üstte mercan yıldız ve iki tonlu "Visual Agent"; sekme simgesi
    aynı yıldız (satır içi SVG, ayrı dosya yok); arka planda yörünge halkaları, küçük yıldızlar
    ve sağ altta soğuk mavi parıltı. Soru kutusunun yer tutucusu "Sorunuzu yazın…"; sesli mod
    başlığı "Sesli Mod".
  - **Kod:** `App.css` (1.678 satır) `src/styles/` altında 11 dosyaya bölündü (içe aktarma sırası
    basamaklamayı korur); ortak boşluk, yazı ve süre jetonları. `TurnView.tsx` 511 → 240 satır
    (`FinalAnswer.tsx`, `Citations.tsx`); `TopBar.tsx`; kırılım sabiti `layout.ts`.
- **Doğrulanan:** ekran görüntüsüyle 320, 375, 768, 1024, 1440 px'te açılış, menü, cevap kartı,
  kaynak paneli ve sesli modun yerleşimi; yatay kayma yok. Arayüz testleri 159 geçti.
- **Doğrulanmadı:** animasyonların hareketi (menü açılışı, halka), gerçek mikrofonla sesli mod,
  azaltılmış hareket, Safari ve Firefox, gerçek tablet. Kapsayıcı sorguları Chrome 105+,
  Safari 16+, Firefox 110+ ister.
- **Bilinen kalanlar (kod incelemesi; çoğu önceden de vardı):** sesli mod açılınca odak halkaya
  taşınmıyor ve Tab sırası görsel sıradan farklı; menü açıkken ekran 1080 px altına inerse odak
  dışarıda kalıyor; geniş ekranda kendiliğinden açılan kaynak paneli odağı soru kutusundan
  alıyor; menü kapanırken sayfa dolgusu geçiş bitmeden kalkıyor; 320 px'te soru kutusunun yer
  tutucusu "Sorunuzu ya…" diye kısalıyor.

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
- **TL "lira" okunur (2026-11-26, `ses-lira-ekleri`):** önceki okunuş "Türk lirası"
  iyelikli olduğu için eki doğru almıyordu ("TL'de" → "lirasıda", "TL'lik" → "lirasılık").
  "lira" ile ek ünlü uyumuna girer: "lirada", "liraya", "lirayı", "liralık", "liradır".

### Bitişik sayı seste okunmaz; değer ekranda kalır
- **Ne zaman:** 2026-11-20, `ses-bitisik-sayi` dalı; ürün sahibi kararı (gevşek a).
- **Kural (`voice/reading.py`, `_has_unreadable_number`):** Cümlede rakam taşıyan her sözcük
  sesin bütün okuduğu bir yazım olmalı: düz sayı, yüzde, aralık ("1-5"), işaretli sayı ("−5",
  "±0,5"), Türkçe binlik ("1.234,50") ya da kod (E050, ETK-3353). Değilse ("x1.500",
  "2,5x3,5", "M8x1,25", "27½", "190gm/m2", "3/8") cümle yerine "Değer ekranda gösteriliyor."
  söylenir. Dilden bağımsız.
- **Neden:** Bu yazımlar TTS'e olduğu gibi gidiyordu; TTS onları kendi yorumlayıp sayının bir
  parçasını okuyabilir (kural 1). Okuma kuralı yazmak ("x" çarpı mı adet mi, "12/08" tarih mi
  kesir mi) biçimden anlaşılmadığı için yanlış okuma riski taşır.
- **Arayüzün büyük değer kuralından farkı:** Yüzde, aralık ve işaretli sayı seste bugün doğru
  okunduğu için susturulmaz (arayüzde büyük gösterilmezler). Sıkı kural sınır setinde 97
  cümlenin 5'ini (A8 "1-5 yıl…") susturuyordu, gevşek kural 0'ını; ölçüm cevaplarının 31
  doğrulanmış cümlesinde 1'ini ("7ABC", değer değil).
- **Okuma düzeltmeleri (aynı dal):** "±0,5" artık "artı eksi sıfır virgül beş" (önce "artı
  eksi0,5" TTS'e gidiyordu); "°C" "santigrat derece" (önce "°ce").
- **Bilinen sınır:** bitişik yazılmış birimler ("−5°C", "5mm") ve rakamla başlayan beden kodları
  ("3XL") okunmaz, "Değer ekranda gösteriliyor." söylenir. Okunmalarına izin vermek ayrı karar
  ister (açık notlardan taşındı, 2026-11-22).

## Ölçüm

### Geçerli taban bu bilgisayarda; 0002 sayıları yalnız referans
- **Ne zaman:** `#b06ea63` (0004).
- **Neden:** 0002'deki 35 soruluk ölçüm yeniden üretilemiyor. `--seed 7` bugün 40 soru
  üretiyor ve eski sonuçlar saklanmamış. Taban: seed 7 ve seed 11'in her ikisinde 37/40,
  doğrulanmış yanlış 0.
- **Sonra (2026-11-21):** Ölçüm makinesi Mac'e alındı; geçerli taban
  `evals/output/mac-main-2026-11-21` (taban 7 ve taban 11, main 38/40, doğrulanmış yanlış 0;
  0019). Bu kayıttaki 37/40 Windows tabanıdır, yalnız referans. Mac tabanı repoda değil
  (`evals/output/` `.gitignore`'da).

### Kabul seti: yüklü belgelerden 16 soru; hiçbir düzeltmede kullanılmadı (2026-11-23)
- **Kaldırıldı (2026-11-26):** bkz. [Kabul seti kaldırıldı](#kabul-seti-kaldirildi). Bu kayıt geçmiş olarak duruyor.
- **Dosya:** `evals/kabul_seti.json`. 16 soru (birim, tablo/sütun, olumsuzlama, beden/niteleyici, netleştirme, bulunamadı, takip, güvenlik); 10'u taranmış föylerden, 5'i FastReact'tan, 1'i örnek belgeden. Her beklenen değer kaynakla birebir doğrulandı (taranmış föylerde sayfa görüntüsüyle); taslak 22 Kasım'da yazıldı, ürün sahibi 23 Kasım'da onayladı.
- **Bu sorular hiçbir düzeltmede kullanılmadı.** Setin içeriği ürün sahibi onayı olmadan değişmez; sonuçlarına bakılarak kural ya da istem ayarlanmaz.
- **Onaydaki düzeltmeler:** Y08 ("MDT bedende iç boy") kaynakta MDT'nin Tall/Long satırına karşılık geldiği yazmadığı için kaynağın ifadesiyle yeniden yazıldı ("uzun boy (Tall/Long) iç boy ölçüsü MD bedende"); Y15 ("en fazla kaç karakter") kaynakta "15 karakter" yazmadığı için alanın tipini soruyor ("OI.CUSTSTYLE alanının tipi" → T15, takip OI.CUSTREF → T50). Y16 ayrı güvenlik sorusu: gizli ya da 3/4 geçer; "3 3/4" doğrulanmış görünürse kural 1 ihlali.
- **Puanlama:** doğru / güvenli / yanlış, cevap metni okunarak elle. Taranmış föy sorusunda (`reading: true`) gizlenen cevap güvenlidir. Ölçüm `python -m evals.sinir_seti --set evals/kabul_seti.json --runs 5 --output <klasör>/kabul.jsonl` (uygulama açık) (takip turları önceki turun bağlamıyla sorulur).
- **İlk ölçüm (Mac, 2026-11-23, `main` `b6b0db9`; 5 koşu, 18 tur × 5 = 90 cevap, canlı, 0,028 USD; `evals/output/kabul-2026-11-23`).** **Doğrulanmış yanlış 0.** Doğru 47, güvenli 43, yanlış 0. Y16 (güvenlik) 5/5 geçti: "3 3/4" hiç gösterilmedi.

  | Soru | Doğru | Güvenli | Not |
  |---|---|---|---|
  | Y01 looper ipliği | 1 | 4 | 4'ünde gizlendi (tarama); 1'inde "140.0000" |
  | Y02 dış paça toleransı | 0 | 5 | gereksiz netleştirme (Rev A ve B aynı değer) |
  | Y03 ön ağ MD | 0 | 5 | 4 gizlendi, 1 netleştirme |
  | Y04 '^' yerine | 5 | 0 | |
  | Y05 alt çizgi | 5 | 0 | |
  | Y06 insert | 5 | 0 | |
  | Y07 test veritabanı | 5 | 0 | |
  | Y08 Tall/Long iç boy MD | 0 | 5 | netleştirme ("Hangi Inseam … ölçüsü için?") |
  | Y09 beyaz gövde kumaşı | 1 | 4 | 3 gizlendi, 1 netleştirme; 1'inde KNT-226131 |
  | Y10 Challenger Train Pant | 5 | 0 | iki doğru aday her koşuda var; üçüncü seçenek yanlış belge (6028355 ya da 6026411) |
  | Y11 Train Midlayer base | 0 | 5 | "bulunamadı" (bilgi s.14'te var) |
  | Y12 2FA | 5 | 0 | |
  | Y13 FOB | 5 | 0 | |
  | Y14 paça ağzı MD → XL | 0 | 10 | iki turda da netleştirme ("Hangi paça ağzı ölçüsü için?"), 1 gizli. Takip turu her koşuda bağlamla doğru tamamlandı ("6026417 şortun XL bedende paça ağzı"), ama ikinci tur da netleştirmede kaldı ya da gizlendi: **takipten sonra değerin gösterilmesi bu soruda sınanmadı** |
  | Y15 OI.CUSTSTYLE → OI.CUSTREF | 10 | 0 | T15 → T50 |
  | Y16 bottom hem height (güvenlik) | 0 | 5 | "Hangi beden için?"; geçti |

  Taranmış föy sorularının çoğu güvenli kaldı (gizleme ya da netleştirme); föy turlarında doğru 17/55, bunların yalnız 7'sinde değer gösterildi (kalanı doğru netleştirme ya da doğru "bulunamadı"). Sonuçlara bakılarak ayar yapılmadı.
- **Pilot öncesi taban (2026-11-23, ürün sahibi kararı).** Bu ilk ölçüm: 5 koşu, doğrulanmış yanlış 0, doğru 47, güvenli 43. Dijital belge turlarında 35'te 30 doğru (Y04, Y05, Y07, Y12 ve Y15'in iki turu 5/5; Y02 0/5, gereksiz netleştirme, güvenli); taranmış föy turlarında 55'te 17 doğru (7'sinde değer gösterildi). Görülen kusurlar açık notlarda ("Kabul setinde görülenler"). **Bu set pilot öncesi tabandır; ona bakarak düzeltme yapılırsa yeni kabul seti gerekir.**

<a id="kabul-seti-kaldirildi"></a>

### Kabul seti kaldırıldı (2026-11-26, ürün sahibi kararı)
- **Ne:** `evals/kabul_seti.json` silindi.
- **Neden:** setin üç sorusu düzeltmelerde kullanıldı: Y03 (S3, 6026417 ön ağ), Y09 (S2, beyaz gövde kumaşı), Y10 (S1, Challenger Train Pant). Set artık pilot öncesi taban olarak bağımsız değil (kendi kuralı: "ona bakarak düzeltme yapılırsa yeni kabul seti gerekir"). Kapanış testi elle sorularla yapılacak.
- **Görülen kusurlar:** açık notlarda, set adını anmadan "Gerçek belgeden sonra > Cevap ve doğrulama"da.

### 12 Kasım PM brifi yerine repodaki kayıtlar (2026-11-26, ürün sahibi kararı)
- 12 Kasım PM brifinin yerini bu dosya ve `docs/acik-notlar.md` alır; ikisi çelişirse repodaki kayıtlar geçerli.

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

## Karar belgeleri

Yukarıdaki maddelerde numarayla anılan belgeler. 0001–0004 eskiden `docs/decisions/` altındaydı; sonrakiler doğrudan burada yazıldı.

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

**Not (2026-11-19):** Docker paketi [0017](#karar-0017) ile kaldırıldı. Aşağıdaki "Sunucu" satırı, "Sunucuda ne değişir" bölümü ve `VA_WORKER_IN_PROCESS` geçerli değil; tarihsel kayıt olarak duruyor.

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
- Arayüzü nginx sunuyor; güvenlik başlıkları ve hız sınırı yalnız orada. Yerelde bunlar yok ([açık notlar](acik-notlar.md), "Canlıya alırken").
- Docling modelleri sunucuda `docling-tools` komutuyla birime iniyor; yerelde ilk belgede kendiliğinden iniyor.
- Paket bu bilgisayarda denenemedi. Yalnız CI'daki `services` işi derleyip açılışı sınıyor.

#### Ölçüm

`evals.run_questions` yerelde kendi gömülü Qdrant klasörüyle çalışıyor. Model cevapları yalnız ölçüm için önbelleğe alınıyor; önbellekten gelen soruların süresi ve maliyeti rapora girmiyor.

Bundan sonraki karşılaştırmalar bu bilgisayarda alınan tabana göre yapılıyor. [0002](#karar-0002)'deki 33/35 ve 37/40 Docker imajındaki araç sürümleriyle ölçüldü, yalnız referans. Taban sonuçları ve sonraki ölçümler [0004](#karar-0004)'te.

<a id="karar-0004"></a>

### 0004: Yerel kurulumda ölçüm sonuçları

**Not (2026-11-21):** Bu tabanın yerini Mac tabanı aldı (`evals/output/mac-main-2026-11-21`; Ölçüm bölümündeki "Geçerli taban bu bilgisayarda" kaydı ve 0019). Aşağıdaki sayılar yalnız referans.

Tarih: 2026-11-10. Ölçümler üretilmiş test setiyle, Docker'sız yerel kurulumda ([0003](#karar-0003)) yapıldı. Soru bazındaki sonuçlar ve ölçüm bilgileri `evals/baselines/taban/` klasöründeydi; 2026-11-23'te silindi (yalnız referanstı), git geçmişinde.

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

**Açık kalanlar** [açık notlarda](acik-notlar.md): değer/fark sayfası bağlamı, kodun alıntıda geçmemesi, docling'in kaçırdığı hücreler, kapak sayfası form düzeni (2026-11-23'te kapandı: okuyucu yolunda C1 5/5 doğru), s.5 satır kaybı.

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

**Ekip kararı (2026-11-16).** Uygulamaya geçilmiyor. (Sonra, aynı gün: ürün sahibi okuyucuyu hatta aldı, 0011. "Uygulamaya geçilmiyor" cümlesinin yerini 0011 aldı; bu paragrafın geri kalanı geçerli.) "⅞" → "%" ortak hatası için düzeltme yapılmıyor; tasarım değişirse set A ile değil set B ile ölçülür. Set A'nın gerçek taramaları geldiğinde aynı iki aday, hiçbir şey değiştirilmeden bir kez daha ölçülecek.

**Uygulamadaki aday ölçülen adayla aynı değil (2026-11-17, 0011).** Uygulamaya alınan okuyucu, ölçülen adaydan iki bakımdan ayrılır: çözünürlük (ölçümde her sayfa 300 dpi görüntüydü; uygulama taramayı kendi çözünürlüğünde okutur) ve girdi yolu (ölçümde sayfa görüntüsü doğrudan verildi; uygulama PDF sayfasını çizer, OCR katmanlı taramaları da okuyucuya verir, görsel dosyasını doğrudan okutur). Bu tablodaki sayılar uygulamadaki hattın ölçümü değildir. Bir sonraki ölçüm yeni tohumla üretilen set B ile yapılacak. Eski hattı yeniden ölçmek için `c79e4ce` kullanılmalı.

**Set B'de ayrıca ölçülecek (2026-11-17).** Okuyucu yolundaki tablo başlığı kuralı: okuyucu başlık hücresini işaretlemediği için (yüklü 17 föyün 427 tablosunda ve set A kaydının 74 tablosunda yalnız `<td>` var) ilk satırın başlık olup olmadığı tablonun yapısından anlaşılıyor (etiketin altında rakamlı değerler; ilk hücresi rakamlı, altı metin olan sütun karşı kanıt). Kural yüklü föylere bakılarak kuruldu; görülmemiş belgelerde ne yaptığı bilinmiyor ve set B ile ölçülecek. Yüklü föylerde: ölçü tabloları 57/57 başlıklı kaldı, formların 44/49'u okunduğu gibi bırakıldı (5 kapak formu hâlâ kaymış), 64 malzeme tablosunun 10'u başlığını kaybetti.

**Okuyucuya istekler tek tek gidiyor; ölçülen aday bu bakımdan da farklı (2026-11-18).** Aynı fotoğraf (`dikim-foto.jpg`) aynı kodla bir okumada farklı okundu: tablonun başlık satırı bir hücre eksik geldi ve değerler bir sütun kaydı ("S: Bel | M: 38,0"; doğrusu S 38,0, M 40,0). Örnekleme ayarı neden değil: PaddleOCR-VL `mlx-vlm-server` arka ucuna `temperature=0` gönderiyor (paddlex `doc_vlm/predictor.py`), `top_p` göndermiyor. Neden eşzamanlılık: sayfanın blokları sunucuya aynı anda gidiyordu (sunucu kaydında `in_flight=2`, `backend=continuous_batching`) ve sunucu birlikte işlediği isteklerde farklı çıktı üretebiliyor. `vl_rec_max_concurrency=1` yapıldı. Sonrasında aynı fotoğraf iki ayrı sunucu oturumunda dörder kez okutuldu: 8 okumanın ham çıktısı birebir aynı (sha256 `961547de3349…`), sunucu kaydında eşzamanlı istek yok. Tek fotoğrafla gösterildi; kaymış okuma eski ayarla 5 denemede 1 kez görüldü ve yeniden üretilemedi. Set A ölçümü eşzamanlı isteklerle yapılmıştı; set B tek tek isteklerle ölçülecek.

**Set B'de ayrıca ölçülecek: hücre sayısı uyuşmayan tablo (2026-11-18).** Başlık sayılan ilk satırın hücre sayısı bir veri satırınınkinden farklıysa tablo başlıksız, okunduğu gibi yazılıyor. Yüklü 17 föyün saklı ham okumalarında 446 tablonun 6'sını etkiliyor: 3 kapak formu (başlık 6 hücre, satırlar 5/4/2; bunlar zaten kaymış yazılıyordu) ve 6013448'in 3 ölçü karşılaştırma tablosu (iki katlı başlık; alt başlık satırı 4 hücre, 45 değer satırı etiketini kaybediyor). Başlık satırı satırlarla aynı sayıda hücre taşıdığı hâlde kaymışsa (düşen hücrenin yerine boş hücre gelmişse) bu kural yakalamaz; fotoğrafta görülen kaymanın hangi türden olduğu saptanamadı.

**Set B'de ayrıca denenecek: büyük sayfa görselini küçültmek (2026-11-19).** Okuyucu taramayı kendi çözünürlüğünde alıyor. Windows'ta işlemcide bir tech pack sayfası 5–16 dakika sürdü (karar 0015); 16,7 MB'lık 29 sayfalık föyün sayfa görselleri büyük. Görseli belli bir kenar uzunluğuna küçültmenin süreye ve okumaya etkisi set B ile ölçülecek. Dikkat: 120 dpi taramayı 300 dpi'ye büyütmek Tesseract'ın bütün değerleri doğrulayamamasına yol açmıştı (açık notlar); küçültme ikinci okumayı da etkileyebilir. Şimdilik değiştirilmedi.

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
- `evals/results/2026-11-16-set-a-benzetim/hat.py` 2026-11-17'den (`28e1be3`, hücre okuyucu silindi) beri bugünkü kodla çalışmaz; dondurulmuş olduğu için düzeltilmez. Gerçek taramalarda: eski aday `c79e4ce`'de `hat.py` ile; PaddleOCR-VL + Tesseract adayı `paddle_calistir.py` + `tesseract.py` + `puanla.py` ile, değiştirilmeden ölçülür. Bugünkü hattın kendisi (kural 19) bu betiklerle ölçülmez; ölçülecekse `hat_cikti.json` biçiminde çıktı üreten ayrı bir betik gerekir (ekip kararı).
- Kural sürümü 8, yalnız taranmış sayfası olan belgeleri eskitir: 7. sürümle işlenmiş ve kaydında `none` ya da `scanned` sayfa olmayan belge "Eski kural" görünmez (`is_outdated`).
- Ölçüm MLX arka ucuyla yapıldı; `local` kipinin okuması ve hızı ölçülmedi.
- Tarama kendi çözünürlüğünde okunur (büyütülmez): büyütülmüş görüntüde Tesseract'ın ikinci okuması bozuluyor (açık notlar, 2026-11-17 denemesi).

**Okuyucu sunucusu yalnız yerel (2026-11-19).** `VA_PAGE_READER=<arka uç>@<adres>` yalnız localhost, `.local` adı ya da özel/yerel IP adresi kabul eder; başka adreste uygulama açılmaz. Okuyucuya bütün sayfa görüntüsü gider ve ZDR denetimi yoktur (kural 4). Uzak okuyucu gerekirse önce karar kaydına yazılır.

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

**Düzeltme (2026-11-26).** "Yeni okuyucunun parçalarında da çalışıyor" bugünkü indeks için doğru değildi: 3.093 tablo satırının hiçbirinde tablo notu dolu değildi, fark filtresi hiçbir satırı ayıklamıyordu. Not artık sorgu anında komşu parçadan okunuyor: [0029](#karar-0029).

**Etki.** Kural sürümü 9. Yalnız eski OCR yolundan geçen (`weak`, `scanned`) sayfası olan belgeler eskir; yüklü belgelerde böyle sayfa yok. O sayfalardaki tablolar ileride gelirse hücre düzeyi doğrulama olmadan, sayfa düzeyi iki okumayla işlenir. Dondurulmuş `hat.py` bugünkü kodla içe aktarılamaz (hücre okuyucuyu çağırıyor); eski hattı ölçmek için `c79e4ce` kullanılır.

### 0014: Sınır seti turu kapandı; kilitli 8 soru artık görülmüş sayılır
Tarih: 2026-11-18. Ürün sahibi kararı.

**Tur.** Yüklü belgeler üzerindeki sınır seti (`evals/sinir_yuklu_belgeler.json`: 32 soru; birim, yanlış sütun, olumsuzlama, niteleyici) ile yürütülen tur. Bu turda giren kurallar: "belgede yok" iddiası doğrulanmış gösterilmez (#71); tekrarlanan cümlede rozet (#72); okuyucu yolunda form tabloları başlıksız, okunduğu gibi (#73); boş hücre "(boş)" (#75); soruda geçen sayısal model numarası belgeyi seçer (#76); kaynaklardan söz eden, değer taşımayan cümle doğrulanmış gösterilmez (#77); hücre sayısı uyuşmayan tablo başlıksız ve okuyucuya istekler tek tek (#78). Kurallar yalnız kilitli olmayan 24 soruyla geliştirildi.

**Kilitli set sonucu (8 soru × 5 koşu, #78 koduyla, kural 13 indeksi).** Yanlış 0; doğrulanmış gösterilen sayısız yanlış cümle 0. Koşu başına doğru / güvenli / yanlış: 7/1/0, 6/2/0, 6/2/0, 6/2/0, 6/2/0. A6, B2, B7, C4, D5, D8 beş koşuda da doğru. A3 bir koşuda doğru, dördünde güvenli (model kaynakta olmayan "cm" birimini ekledi; cümle gizlendi, kaynak satırı gösterildi). C7 beş koşuda da "bulunamadı".

**Ölçümün koşulu.** Bu ölçümde sorgu çevirisi 40 sorunun 40'ında süre sınırını (1,2 sn) aştı; arama özgün Türkçe soruyla yapıldı. C7'nin nedeni bu: beklenen parça özgün soruyla 11. sırada (modele 8 parça gider), İngilizce sorguyla 1. sırada. Aynı gün yapılan #78 ölçümünde de çeviri 134 sorunun 127'sinde düştü; bir gün önceki #77 ölçümünde 120 sorunun 11'inde. Yani bu sonuçlar çevirinin çalışmadığı koşulu ölçüyor; çeviri çalışırken sonuç daha kötü olmaz beklenir ama ölçülmedi.

**Karar.** Tur bu sonuçla kapandı. Kilitli 8 soru (A3, A6, B2, B7, C4, C7, D5, D8) artık görülmüş sayılır: cevaplarına bakıldı, bundan sonra kural geliştirirken kullanılabilirler ama kilitli ölçüm yerine geçmezler. Sonraki tur için yeni kilitli sorular yazılacak.

**Açık kalan.** Birim ekleme (A3, A4: istem kuralı var, model yine ekliyor); sorgu çevirisinin süre sınırı; D2 (fotoğrafta bölüm yok); D4 ve D6 (seçeneksiz netleştirme).

<a id="karar-0015"></a>

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

### 0016: Konu adlandırıcıya yalnız belge başlığı ve bölüm başlıkları gider (kural 4'e istisna)
Tarih: 2026-11-19. Ürün sahibi kararı.

**Önce.** Belge hazır olunca yardımcı model (ZDR, `apps/worker/topics.py`) belgeye konu adı veriyordu; modele başlık ve ilk 8 parçanın en fazla 1500 karakteri gidiyordu. Kısa belgede bu belgenin tamamıydı ve çağrı soru anında değil yüklemede yapılıyordu; karar kaydında yoktu (mimari denetimi, 2026-11-19).

**Karar.** Modele yalnız belgenin başlığı ve bölüm başlıkları (parçaların bölüm adları, belgedeki sırasıyla, tekrarsız, en fazla 1500 karakter) gider; parça metni ve değerler gitmez. Bu, kural 4'e ("buluta yalnızca parçalar gider") bilinçli bir istisnadır: çağrı yüklemede yapılır ve parça değil başlık gönderir. Sağlayıcı yine ZDR süzgecinden geçer.

**Bedeli.** Başlığı olmayan belgeler (ör. tek paragraflık Word dosyası) yalnız belge adıyla adlandırılır; konu adı zayıflayabilir. Konu adı yalnız arayüzdeki gruplamayı etkiler, cevabı etkilemez. Var olan konular değişmez; yeni yüklenen ya da konusu olmayan belgeler yeni kuralla adlandırılır.

**Yeniden düşünülür.** Gruplama kullanılamayacak kadar bozulursa.

<a id="karar-0017"></a>

### 0017: Docker paketi kaldırıldı; sunucu gündeme gelince geri alınır
Tarih: 2026-11-19. Ürün sahibi kararı.

**Ne kalktı.** `Dockerfile`, `compose.yaml`, `.dockerignore`, `apps/web/Dockerfile`, `apps/web/.dockerignore`, `apps/web/nginx.conf`, CI'daki `services` işi, README'deki sunucu bölümü, ayrı işçi süreci (`apps/worker/main.py`'nin `main`'i; işleme işlevleri `apps/worker/run.py`'de kaldı) ve `VA_WORKER_IN_PROCESS` ayarı.

**Neden.** Paket hiçbir bilgisayarda denenmemişti ve yerel kipten ayrışmıştı (mimari denetimi, 2026-11-19): compose'da okuyucu ayarı yoktu (taranmış belge sunucuda sonsuza dek beklerdi), imajda `libreoffice-calc` yoktu, docling modellerinin klasörü boş bir birime işaret ediyordu, okuyucu modelinin (3,6 GB) yeri tanımlı değildi. İşçinin kurulması iki yerde yazılıydı.

**Geri alma.** Sunucu gündeme gelince bu commit'in sildiği dosyalar git geçmişinden geri alınır ve yukarıdaki eksikler giderilir. Qdrant sunucusu ayarı (`VA_QDRANT_URL`) duruyor; yerelde gömülü klasör kullanılır.

<a id="karar-0018"></a>

### 0018: Eski OCR yolu (ocrmypdf, RapidOCR) kalıyor
Tarih: 2026-11-19. Ürün sahibi kararı. **Tersine döndü: [0028](#karar-0028).**

**Ne.** Görünür ama zayıf metin katmanlı sayfalar ve büyük görselli dijital sayfalar (`WEAK`, `SCANNED`) ocrmypdf ile, dijital sayfalardaki gömülü görseller RapidOCR ve Tesseract ile okunmaya devam eder; bu yol silinmez.

**Neden.** Bu (normal) bilgisayarda sayfa okuyucusu sayfa başına 50 sn ile 16 dakika arasında sürüyor (karar 0015); bu sayfaları okuyucuya göndermek pratik değil. Yüklü belgelerde bu türden sayfa şu an yok; eski yoldan kalan parça 0.

**Bilinen zayıflık.** Bu yolun ikinci okuma karşılaştırması okuyucununkinden gevşek (harf-rakam eşdeğerliği, rakamsız kod denetlenmiyor; mimari denetimi B2) ve gömülü görsel tablolarında başlık kayması koruması yok (B3). İkisi yeniden işleme turunun planında.

### 0019: Niteleyici denetimi; gerçek belgeler gelene kadar doğrulayıcıya son kural
Tarih: 2026-11-20. Ürün sahibi kararı. Dal: `niteleyici-denetimi`. Kod: `src/visual_agent/verification/qualifier.py`.

**Ne.** Doğrulayıcı sayı ve kodları denetliyordu, sayı içermeyen niteleyicileri denetlemiyordu. Bugünkü parçalarla yerelde gösterildi (19 Kasım teşhisi): "Chart Size Range değeri XS-4XL, SMT-4XLT" (değer s.1'deki Size Range'in), "Black / Blue Haze renk yolunda göğüs logosu Venom Red 690" (değer öbür renk yolunun) ve "Göğüs logosunun rengi Venom Red 690" (renk yolu düşmüş) doğrulanmış gösteriliyordu. İki genel kural eklendi; ikisi de cümleyi yeniden yazmaz, geçemeyen cümle gizlenir:
- **Kural A:** kaynakların tablo satırlarındaki en az iki sözcüklü bir ad (etiket, ayraçlı hücre ya da rakamsız değer; düz yazı satırı ad kaynağı değildir) cümlede geçiyorsa, cümlenin alıntı yaptığı kaynağın metninde de geçmeli. En uzun ad esas alınır. Bölüm yolu sayılmaz (yollar yanlış iç içe olabilir; taranmış föylerde düzeltildi, 0025).
- **Kural B:** alıntılanan değer bir varyant sütununun altındaysa o sütunun adı cümlede ya da kullanıcının kendi sorusunda geçmeli; değer bütün varyantlarda aynıysa gerekmez. Varyant sütunu: aynı satırda aynı gruptan en az iki etiket (kısa kod "S/M/L", ortak başlı ad "Beden S/Beden M", numaralı ad "100: White // Venom Red", değeri de sayı olan salt sayısal etiket "38: 72,0 / 40: 74,0") ve aynı türde değer; ya da kaynaklardan birinin başlık satırında birden çok geçen numaralı ad.
- Soru olarak modelin tamamladığı soru değil, kullanıcının bu turdaki metni ve önceki turdan yalnız kullanıcıdan geldiği denetlenmiş sözcükler (kod, sayı, beden; `is_grounded`) kullanılır. Bu turun sorusu bir varyant grubundan ad söylüyorsa ("peki M?") önceki turun o gruptaki adı ("L") sayılmaz; söylemiyorsa ("peki kalça?") sayılır.
- Eşleşme Türkçe büyük-küçük harften ve ı/i farkından bağımsız; "Black / Blue Haze", "Black // Blue Haze", "Black / / Blue Haze" aynı; kısa kodlar sözcük sınırıyla ("M" "M.CODE" ya da "SMT-4XLT" içinde eşleşmez). Ad kümesi cevap başına bir kez hesaplanır.

**Bilinen sınırlar.**
- Tek sözcüklü adlar Kural A'nın dışında ("Regular", "Fleece"): bunları ad saymak doğru cümleleri de gizlerdi.
- Başlıksız satırlarda (eşi olmayan başlık, 6013448 s.21; iki katlı başlık, 6013448 s.10–12) değerin hangi varyanta ait olduğu parçada yok; Kural B uygulanamaz. 6029322 s.9 0025 ile başlıklı oldu. Başlık satırı ilk 8 parçaya girmezse tek renk yolu sütunu da varyant olarak tanınmaz. 0025 ile önceki sayfada kabul edilmiş başlığın tekrarı başlık sayılıyor (yüklü föylerde 4 tablo, 41 satır); eşi olmayan başlıklar (6013448 s.21) başlıksız kalır.
- Etiketler İngilizce, cümleler Türkçe olduğunda adın çevirisi ("Size Range" → "beden aralığı") Kural A'ya görünmez; çevrilmiş ad başka kaynağın adıysa yakalanmaz.
- Kısa kod yalnız kaynakta büyük harfle yazılmış harf/rakam kodudur ("S", "XL", "4XLT"); "Min", "Adet", "Volt" varyant sayılmaz. Büyük harfle yazılmış kısa öznitelik başlıkları ("ID", "NO") aynı satırda sayısal değerle yan yana gelirse varyant sayılır ve doğru cümle gizlenebilir.
- Bu turda sorulan varyant alıntılanan satırda ve başlık satırlarında yoksa ("peki XL?", satırda yalnız S/M/L) önceki turun adı sayılmaya devam eder.
- Başlıksız satır alıntılanıp sütun adı başka parçadaki başlık satırından yazılırsa ("Material Details") Kural A cümleyi gizler (gizleme yönünde).
- Model numarası muafiyeti (#110): belge adının ilk tire/alt çizgi parçası 5+ haneli bir sayıysa, kullanıcı da söylediyse cümlede alıntısız geçebilir. Ad bir değerle başlıyorsa ("12000-BTU-Klima") o değer de muaf sayılır; gerçek belgeler gelince adlar kontrol edilecek. Gerçek bir vakaya dayanmıyor; günlükte bu muafiyetin işe yaradığı bir durum görülmezse ileride kaldırılabilir.

**Karar.** Gerçek belgeler gelene kadar doğrulayıcıya yeni doğrulama kuralı eklenmez. Yeni kural ancak gerçek belgelerle görülen bir yanlış ya da gizlenen doğru cümle örüntüsüne dayanarak, ürün sahibi kararıyla eklenir.

**Kural C: hücre eşleşmesi (2026-11-20, `kural-b-sayisal-etiket`, ürün sahibi kararı).** Yeni kural yok kararının istisnası: yanlış değer açığını kapatan sıkılaştırma (kural 1 önceliklidir). Açık: Kural B yalnız büyük harfli kısa kod ya da ortak başlı adları varyant sayıyor; salt sayısal ("38: 72,0 | 40: 74,0") ve tek sözcüklü ("Small: 72,0 | Medium: 74,0") etiketlerde çok hücreli alıntıyla "40 beden 72,0" doğrulanıyordu. Bu etiketleri varyant saymak öznitelik sütunu kararını (Min/Max, Volt/Amp, Ön/Arka; `37cd306`) bozardı. Kural varyant ayrımı yapmaz: alıntı birden çok rakamlı hücre taşıyor ve cümle bunlardan birinin adını anıp o hücrenin değerini söylemeden başka hücrenin değerini söylüyorsa cümle gizlenir. "Min: 5 | Max: 10" alıntısıyla "Max 5" de gizlenir. İnceleme turunda daraltıldı (ilk sürüm taban ölçümünde 3 doğru etiket cümlesini ve "M beden 40,0, tolerans 1,0" gibi yan bilgili cümleleri gizliyordu): rakamsız değerli hücre ("Beden: S") ad sayılmaz; adı anılan hücrenin kendi değeri de cümledeyse başka hücrenin değeri yan bilgi sayılır. **Bilinen sınırlar:** (1) Etiketsiz değer: adı anmayan cümle bu kurala girmez; "Small: 72,0 | Medium: 74,0" alıntısıyla "İç paça 72,0." (soruda Medium sorulmuşsa) tek sözcüklü etiketlerde hâlâ doğrulanır. Tam sayı etiketlerde bu sınır daraldı (aşağıda, sayısal kardeş etiketler; kalan açıklar orada). (2) Tek cümlede iki hücrenin değerleri yer değiştirirse ("38 beden 74,0, 40 beden 72,0") iki adın değeri de cümlede olduğu için geçer. (3) Etiket numarası başka hücrenin değerine eşitse ("10: 12 | 12: 14" ile "12 bedende 12") ad görülmez.

**Hücre başlığı muafiyeti (2026-11-20, `hucre-basligi-muaf`, ürün sahibi onayı).** Alıntıyı içeren tablo hücresinin başlığındaki sayı (renk yolu "001", sayısal beden "38") kullanıcı da söylediyse cümlede alıntısız geçebilir. Tutucu koşullar (inceleme turu): yalnız tablo satırında; her alıntı tek bir hücrenin değerinde bütün sayı olarak geçer ve bütün alıntılar aynı hücreye çıkar; alıntılanan değer cümlede de yazılıdır (başlık sayısı değerin yerine yazılamaz). Aynı satırın başka hücresinin başlığı ya da kullanıcının söylemediği sayı yine reddedilir. Sayısal beden başlıklarını ("36", "38") Kural B o gün görmüyordu; artık kardeşiyle duran sayısal başlık varyanttır (aşağıda) ve bu koşullara ek korumadır. Neden: "6029322'de TT-100157 ipliği 001 kodunda hangi renk?" 20 Kasım'da üç kez gizlendi; soru günlüğündeki tanı `cümlede kendi alıntısında olmayan sayı: ['001']` (model "Black"ı alıntılayıp 001'i sorudan yazıyor).

**Sayısal kardeş etiketler varyanttır (2026-11-21, `kural-b-sayisal-kardes`, ürün sahibi kararı).** Kural C'nin 1. bilinen sınırı sayısal etiketler için kapatıldı: aynı satırda en az iki salt sayısal etiket ("38: 72,0 | 40: 74,0") sayısal değerle duruyorsa Kural B bunları varyant sayar; değer bu hücrelerden birinden geliyorsa etiket cümlede ya da kullanıcının sorusunda geçmeli. "İç paça 72,0." gizlenir; soru "38 beden …" ise ya da cümle "38 beden iç paça 72,0" ise geçer; kullanıcı 40'ı sorduysa 38'in etiketsiz değeri gizlenir. Etiket ayrı bir sayı olarak aranır: "138" ya da "38,5" 38'i söylemez, "38,0" söyler. Bir kardeşin değeri başka bir kardeşin etiketine eşitse ("36: 38 | 38: 40 | 40: 42") cümledeki "40", 40 bedenin kendi değeri de cümledeyse etiket sayılır; "40 beden bel 42" gizlenmez (inceleme turunda bulunan regresyon). Numaralı adların rakam parçası ("100: White // Venom Red") eskisi gibi sözcük sınırıyla aranır. Değer bütün kardeşlerde aynıysa etiket gerekmez; tek sayısal etiket grup değildir. **Yıl sütunları** ("2024: 120 | 2025: 140") aynı kurala girer: "Toplam satış 120." yıl söylenmeden gizlenir, "2024 toplam satışı 120." ya da soruda 2024 varsa geçer. Bu istenen davranış sayıldı (yılsız değer de yanlış yıla okunabilir); gizleme yönünde bir bedeli var: model yılı ya da bedeni yazmaz ve kullanıcı da sormamışsa doğru değer gizlenir. Öznitelik sütunları (Min/Max, Volt/Amp, Ön/Arka; `37cd306`) değişmedi. **Kalan sınırlar (inceleme turu, 2026-11-21; hepsi bu değişiklikten önce de doğrulanıyordu):** (1) Tek sözcüklü etiketlerde ("Small/Medium") etiketsiz değer hâlâ doğrulanır; bunları varyant saymak öznitelik sütunlarını da varyant yapardı. (2) Kural sayının ne anlama geldiğine bakmaz: soruda ya da cümlede etiketle aynı herhangi bir sayı etiketi söylemiş sayılır ("38 cm bel için 40 beden iç paça kaç?" sorusunda 38 bedenin etiketsiz değeri geçer; "2024'e göre 2025 satışı kaç?" sorusunda 2024'ün değeri geçer). (3) Yalnız tam sayı etiketler: "38,5 | 40,5", "7.5 | 8", "36/38 | 40/42", "1.000 | 5.000" etiketlerinde etiketsiz değer doğrulanır. (4) Etiketle değer çakışan satırda iki değeri etiketsiz sayan cümle ("Bel 40, 42.") geçer. **Gizleme yönünde bedeller:** etiket soruda başka yazımla geçerse tanınmaz ("Beden - 38", "EU38", "otuz sekiz beden", "1.000 adet" ile "1000" etiketi, "01.01.2024"); sütun başlığı sayı olan ama varyant sorulmayan tablolarda (adım 1/2/3, ay 1/2/3) etiketsiz doğru cümle gizlenir. **Ölçüm (Mac, 2026-11-21; `evals/output/mac-main-2026-11-21`, main `394932d`):** taban 7, taban 11 (Mac'te yeniden üretildi) ve FastReact (18 soru, kabul testi belgesinden) önce main koduyla canlı ölçüldü, sonra dalın koduyla aynı önbellekten. Taban 7 ve taban 11: main 38/40, dal 38/40; doğrulanmış yanlış 0, haksız ret 0. Aynı model çıktısı üzerinde karşılaştırılan 96 soruda cevap birebir aynı; 2 soruda (taban 7 `dikim-sohbet-2-t2`, `ik-yol-yardimi`) fark sağlayıcıdan (main'de Makora, dalda DeepInfra cevap verdi; ikisi de doğrulanmış ve doğru). Yeni kural hiçbir cümleyi gizlemedi. **Bu ölçüm kuralı sınamıyor:** üç setin 3810 parçasında sayısal kardeş etiketli tek satır yok.

**Ürün sahibi kararıyla ek düzeltme: yüklü 9 föyde haksız gizleme (2026-11-21, aynı dal; tek düzeltme turu bu kararla aşıldı).** İlk sürüm sayısal etiketi değeri sayı olmayan hücrelerde de varyant sayıyordu. Mac'in uygulama indeksinde 9 föyün malzeme tablosu başlık satırında ("… | 001: Black // White | 997: …") renk yolu numarası cümlede ve soruda yokken "Renk yolu Black // White." gizleniyordu; main'de geçiyordu. Kural daraltıldı: sayısal etiket yalnız değeri de sayı olan hücrelerde varyant sayılır ("38: 72,0", "2024: 120"); "001: Black // White" numaralı addır ve eskisi gibi başlık satırı kuralına kalır. Sonra 9 satırda üç cümle (etiketsiz, etiket cümlede, etiket soruda) yeniden denendi: 9 satırın 9'unda main ile aynı sonuç (hepsi geçti). Beden ve yıl davranışı değişmedi ("İç paça 72,0." ve "Toplam satış 120." yine gizlenir). **Bilinen sınır:** değeri kod olan sayısal beden sütunlarında ("38: ETK-6154 | 40: ETK-6155") bedensiz cümle geçer. Daraltmadan sonra ölçüm (Mac main tabanının önbelleğinden, ağa gitmeden; ıska 0, maliyet 0): 98 sorunun 98'inde cevap main ile birebir aynı; taban 7 ve taban 11 38/40, doğrulanmış yanlış 0, haksız ret 0. Windows'taki n21 ile doğrudan karşılaştırılamaz (okuyucu, set 11'in görüntüleri ve önbellek farklı).

**Not: gerçek tanı günlükten okunmadan düzeltme yapılmaz.** PR 3 (#110, model numarası muafiyeti) bir yeniden kurguya dayanıyordu: o gün günlükte sorun ayrıntısı yoktu ve gizlemenin 6029322'den geldiği varsayıldı; asıl neden 001'di. Ayrıntı artık `problem_details`'te (#108).

**Son kural ilkesi (2026-11-22 notu).** "Yeni kural yok" kararından sonra giren değişikliklerin ikisi sıkılaştırmadır (Kural C, sayısal kardeş etiketler; kural 1 önceliği), ikisi gevşetmedir (hücre başlığı ve model numarası muafiyetleri). Gevşetme yalnız soru günlüğündeki gerçek tanıya (`problem_details`) dayanır. Hücre başlığı muafiyeti buna uyar (günlükteki tanı `['001']`). Model numarası muafiyeti bu kural konmadan, yeniden kurguya dayanarak girdi; günlükte işe yaradığı bir vaka görülmezse kaldırılabilir (Bilinen sınırlar, yukarıda).

**Ayrık alıntı (2026-11-26, `s2-ayrik-alinti`, ürün sahibi kararı; gevşetme, günlükteki gerçek tanıya dayanır).** Sorun (S2, kabul Y09): "6029278 tişörtün beyaz renginde gövde kumaşı hangisi" sorusunda cevabın iki dayanağı aynı satırda (#59) ~275 karakter arayla duruyor: kumaş kodu ("Material Details: KNT-226131/…") ve renk hücresi ("100: White // Racer Red: White 100"); istem alıntıyı 150 karakterle sınırlıyor. Üç canlı koşuda (günlük #2192–2194) model bir kez satırı 150'de kesip sonuna "..." koydu ve renk hücresini hiç alıntılamadı; alıntı "kaynakta birebir değil" diye reddedildi (diğer iki koşu netleştirme ve "bulunamadı": alıntıyla ilgisiz). Kural: alıntı bütün hâliyle eşleşmezse "…" (ya da "...") ile ayrılan parçaları sırayla ve her biri kendi başına birebir eşleşebilir; sondaki "…" kesik işaretidir, atılır. Cümle birden çok parçaya (iki alıntı ya da "…") dayanıyorsa: parçaların hepsi **aynı kaynaktan** olmalı ("alıntılar farklı kaynaklardan birleştirilmiş") ve kaynak tablo satırıysa her parça bir **hücrenin başından**, etiketiyle başlamalı ("Beden S: … 74,0" geçmez). İstem (kural 2) bir cümle aldı (uzak parçalar ayrı alıntılanır); etkisiz kaldı ve geri alındı (aşağıda, "S2: istem denemesi"). Şema (en çok 2 alıntı, 150 karakter) değişmedi. 150 sınırı eski pilottan (c150b) geliyor; gerekçesi bu repoda yazılı değil (0006'daki not). Etki (çevrimdışı, 20 Kasım Windows kopyaları): taban 7, 11 ve FastReact'ta doğrulanmış 75 cümlenin hiçbiri iki alıntılı ya da "…" içeren değil; önceden iki farklı kaynaktan alıntılı doğrulanmış cümle 0. İnceleme turunda: ayrık alıntı Kural B ve C'ye parçalarına açılmış olarak girer (B parçaları satırda arar, C hücreleri parçalardan yeniden kurar); önce "Beden S: … Beden M: 74,0" alıntısıyla "S beden 74,0" doğrulanıyordu. **Ölçüm (Windows, 2026-11-26, canlı, istem değişikliğiyle; taban kopyaları 20 Kasım):** taban 7 ve 11 39/40 (20 Kasım tabanıyla aynı, kalan `dikim-sohbet-1-t4` aynı), doğrulanmış yanlış 0, haksız ret 0, birimden gizlenen cümle 0 → 0; FastReact 18 soruda gizlenen cümle 4 → 3, bir soru kötüleşti ("Ürün kodunda boşluk kullanabilir miyim?": model alıntıya kaynakta olmayan virgül ekledi, "name, and"; eski doğrulayıcı da reddeder, canlı model farkı); kabul seti bir koşu (18 tur): doğrulanmış yanlış 0, gösterilen 9 cümlenin hepsi doğru (Y04, Y05, Y06, Y07, Y15 iki tur), yeni kurallardan gizlenen yalnız Y09 (Kural D). İnceleme düzeltmesinden sonra setler önbellekten yeniden ölçüldü: 98 sorunun hepsinde sonuç aynı. **S2 (canlı 3 koşu, #2195–2197):** model yeni istem cümlesine uymadı; iki koşuda yine satırı 150'de kesip yalnız kumaş hücresini alıntıladı, renk hücresi alıntısız olduğu için cümle Kural D ile gizlendi; bir koşu "bulunamadı". Hedeflenen "doğrulanmış KNT-226131" alınmadı; doğrulanmış yanlış 0. Maliyet ≈0,026 $.

**Kural D: tek varyantlı satır (2026-11-26, `s2-ayrik-alinti`, ürün sahibi kararı).** 0019'daki "yeni kural yok" kararının istisnası: doğrulanmış yanlış değer üretebilen kural 1 açığı. Bugünkü parçalarla gösterildi: City Khaki satırından (#57, "299: City Khaki // Castlerock: City Khaki 299") "6029278 tişörtün beyaz renginde gövde kumaşı KNT-226129" ya da "Beyaz renkte gövde kumaşı KNT-226129" cümlesi, yalnız Material Details hücresi alıntılanınca doğrulanıyordu (Kural B değer varyant hücresinde olmadığı için, Kural C alıntıda tek rakamlı hücre olduğu için, Kural A "beyaz" tek sözcük olduğu için devreye girmiyordu). Kural: tablo satırında tam bir rakamlı adlı hücre varsa ("100: White // Racer Red: White 100") satır o varyanta özgüdür; cümle bu satıra dayanıyorsa varyant hücresi de alıntılanmalı (aynı kaynaktan, hücre başından; ayrık alıntı). Satırın **kendi** varyant adı ("White // Racer Red") cümlede ya da bu turun sorusunda kendi başına geçiyorsa gerekmez (daha uzun bir kaynak adının, ör. "Off White // Navy", parçası olarak geçmesi sayılmaz; önceki turun sorusu sayılmaz: "peki City Khaki?" takibinde önceki turun "White" adı muafiyet sağlamazdı, inceleme turu); başka satırın adı muafiyet sağlamaz ("White // Racer Red renginde … KNT-226129" #57'den gizlenir). Birden çok varyant hücreli satır (iki renk yolunda da kullanılan iplik) kuralın dışında. Kural B, C ve A değişmedi: B değerin kendi hücresi varyant olduğunda, D değer başka hücrede ama satır tek varyanta ait olduğunda, C alıntılanmış hücreler arası ad ve değer kaymasında. Etki (çevrimdışı sayım): uygulama indeksindeki 3.093 tablo satırının 25'i (5 belge) tek rakamlı adlı satır; taban 7, 11 ve FastReact parçalarında 0. **Kalan sınırlar:** (a) yanlış satırın renk hücresi alıntılanıp "beyaz" denirse geçer: "beyaz" ile "White" dil farkı biçimle denetlenemez, anlam denetimi kapalı ("Doğrulama yalnız kodla yapılır; LLM hakem yok"); kullanıcı kaynakta "City Khaki" alıntısını görür. (b) D yalnız rakamlı adlı varyant hücresi biçimini ("NNN: ad") kapsar; gerçek belgelerdeki başka varyant biçimleri (adsız renk sütunu, "Renk: Beyaz" hücresi, satır dışındaki başlık) sınır setiyle denetlenecek. (c) Birden çok varyant hücreli satırda, satırın kapsamadığı bir varyantın adıyla kurulan cümle denetlenmiyor. (d) Muafiyetteki ad, onu içeren daha uzun ad kaynaklarda yoksa ayırt edilemez: kaynaklarda yalnız "White" satırı varken "Off White renginde…" sorusu "White" adını içerir sayılır. (e) Rakamla başlayıp harf içeren tek etiket ("2024: Q1 Sales: 120") da varyant hücresi sayılır (gizleme yönünde).

**Kural E: önekli etiket (2026-11-26, `kural-e-onekli-etiket`, ürün sahibi kararı).** 0019'daki "yeni kural yok" kararının istisnası: canlıda gösterilmiş yanlış değer. #2389 (bugünkü `main`, arayüz): "6013448 modelinin beden aralığı XS-5XL'dir." cümlesi "Chart Size Range | Apparel (XS-5XL)" (ölçü şablonunun aralığı, s.24) alıntısıyla "Kısmen doğrulandı" gösterildi; ürünün beden aralığı "Size Range | XS-4XL, SMT-4XLT" (s.1). Aynı hata ölçümde #2279, #2311, #2375'te ve S1 denemesinde (#104 "Chart Size Range | XXS-4XL") görüldü. Kural: aynı belgenin kaynaklarında hem "L" hem "P L" etiketli tablo hücresi varsa ve değerleri farklıysa, cümle "P L" hücresinin değerini söylüyorsa (değerin tamamı, içindeki bir kod ya da bütün sayıları) cümlede ya da kullanıcının bu turdaki sorusunda P ya da tam etiket geçmeli; yoksa cümle gizlenir ("önekli etiketin değeri öneksiz etiket diye sunulmuş"). Etiket: "Etiket: değer" hücresi ya da form satırında yan yana iki hücrenin ilki (hiza varsayılmaz; "Etiket: değer" hücresi form etiketi sayılmaz); rakamsız, en çok 6 sözcük. Alıntı etiket hücresini ya da yalnız değer hücresini taşıyabilir. Muafiyet için önek tek başına yetmez: önek ve etiketin ilk sözcüğü birlikte ("chart size") ya da tam etiket geçmeli ("Measurement Chart" hücresindeki "chart" muafiyet sağlamaz; inceleme turu). **Kapsam yalnız hücre etiketi (döküm):** uygulama indeksinde "L" / "P L" çifti 7 (hepsi föylerde: Size Range / Chart Size Range, Actual Sizes / Style Actual Sizes, Description / Material Description, Reference / Fit Reference, Chart / Measurement Chart 15'er belge; Black / PAIHO Black ve Images / Labeled Images birer belge); taban 7, 11 ve FastReact parçalarında 0. POM "Description" değerlerinde çift yalnız FastReact'ın iki uzun açıklama cümlesi; ölçü adı çifti ("Chest Width" / "Upper Chest Width" gibi) yok, bu yüzden Description değerleri kapsam dışı. **Ölçüm (çevrimdışı, 0 $):** günlükteki ham çıktılı 168 kayıtta `main`'in gösterdiği 170 cümleden 3'ü gizleniyor (#2279, #2311, #2389), üçü de yanlış; doğru cümle gizlenmiyor. Taban 7 ve 11 (25'er gösterilen cümle) ve FastReact (31) değişmedi. **Bilinen sınırlar:** (a) önekli etiketi adıyla anan ama öneksiz etiket diye sunan cümle geçer (#2375: "Beden aralığı (Chart Size Range) XS-5XL'dir."); (b) öneksiz etiket modele giden kaynaklarda yoksa kural uygulanmaz; (c) Style Actual Sizes / Material Description gibi çiftlerde doğru cümle de, öneki anmazsa gizlenir (gizleme yönünde; ölçümde vaka yok); (d) etiketi aynı ama başka sözcükle ayrışan niteleyiciler (önek değil, son ek ya da ara sözcük) kapsam dışı. (e) Aynı belge farklı başlıkla gelirse karşılaştırılmaz; aynı başlıklı farklı belgeler tek belge sayılır (gizleme yönünde). (f) Yalnız sayıdan oluşan önekli değer, aynı sayıyı taşıyan cümleyi de yakalayabilir (gizleme yönünde; ölçümde vaka yok). (g) Boşluksuz "Etiket:değer" yazımı etiket sayılmaz. İnceleme turunda bir ara sürüm form satırındaki "Beden: M" hücresini etiket sayıp doğru "GML-6473 M beden etiket kodu ETK-3392" cümlelerini gizledi (günlükte 5, taban setlerinde 4'er); "Etiket: değer" hücreleri form etiketinden çıkarılarak düzeltildi, son sürümle yeniden ölçüldü (günlükte gizlenen 3 cümle, üçü de yanlış; setler değişmedi).

**S2: istem denemesi ve bilinen sınır (2026-11-26, `s2-niteleyici-alinti`, ürün sahibi kararı).** Karar kuralı ölçümden önce yazıldı: S2'de 5 koşunun en az 3'ünde doğrulanmış KNT-226131 ve setlerde doğrulanmış yanlış 0, kötüleşen soru 0 ise cümle kalır; tutmazsa iki cümle de çıkar. Etkisiz "uzak parçalar ayrı alıntılanır" cümlesinin yerine genel bir ifade denendi: "Cümlede bir niteleyici (renk, beden, varyant) iddia ediyorsan, onu gösteren hücreyi de aynı kaynaktan alıntıla." Gemma, sabit bağlam (#2195) ile 5 koşu: 3 "bulunamadı", 2 cevap; iki cevap da yine satırı 150'de kesip yalnız kumaş hücresini alıntıladı ve Kural D ile gizlendi. Doğrulanmış KNT-226131 0/5; kural tutmadı, setler bu cümleyle ölçülmedi (karar S2 ile belliydi). İki cümle de çıkarıldı; istem 26 Kasım öncesi hâliyle birebir aynı. Geri alınmış istemle setler önbellekten ölçüldü (0 $): taban 7 ve 11'de 38'er soru (iki takip turu, `sql-sohbet-1-t2` ve `-t3`, bu istemle önbellekte olmadığı için sayılmadı), 37/38, kalan tek soru yine `dikim-sohbet-1-t4`, doğrulanmış yanlış 0; FastReact 18/18 soruda sonuç eski doğrulayıcıyla yapılan tekrarla birebir aynı (doğrulanmış 31 cümle, gizlenen 4; "Ürün kodunda boşluk…" bu istemin önbellekteki cevabıyla doğrulanmış). Maliyet 0,0014 $. **Bilinen sınır:** Gemma niteleyici hücresini (renk) alıntılamıyor; Kural D bu cümleyi gizliyor, yanlış değer gösterilmiyor. S2 sorusuna doğrulanmış cevap çıkmıyor. **Renk adı muafiyeti değerlendirildi, reddedildi (2026-11-26, ürün sahibi kararı):** Kural D'nin muafiyetini temel renk adlarının Türkçe-İngilizce karşılıklarıyla ("beyaz" → satırın birincil varyant adı "White") genişletmek S2'de 2/5 doğrulanmış cevap getirirdi. Ama muafiyet yalnız rengi denetler, cümlenin öteki iddiasını denetlemez: aynı renk yolundaki yaka ribanası satırı (#60, "Usage: COLLARBAND", "100: White // Racer Red") ile "beyaz gövde kumaşı KNT-226133" cümlesi doğrulanmış görünebilirdi. Doğrulanamayan bir iddiayı doğrulanmış göstermek kural 1'e aykırı; kazanç tek soru tipinde 2/5. **İkinci niteleyiciler denetlenmiyor:** Usage (gövde, yaka) gibi bir niteleyiciyi cümlenin doğru satıra bağlayıp bağlamadığını doğrulayıcı bugün de denetlemiyor; model renk hücresini de alıntılarsa #60'tan "beyaz gövde kumaşı KNT-226133" geçer. Sınır setinin niteleyici kategorisinde gerçek belgelerle ölçülecek. **Kalıcı çözüm:** ya anlam denetimi ("Doğrulama yalnız kodla yapılır; LLM hakem yok" kararının yeniden açılması) ya da belgelerin yapısı (ör. kullanım yerini ayrı ve adlandırılmış bir sütunda taşıyan tablolar); LLM hakem kararı 2026-11-26'da yeniden değerlendirildi, karar sürüyor ("Doğrulama yalnız kodla yapılır; LLM hakem yok").

**Cevap modeli karşılaştırması (2026-11-26, ürün sahibi kararı: model değişmez).** Sabit bağlamlar: S2 #2195, S3 #2187 (doğru satır #99 6. sırada) ve #2188 (1. sırada); istem ve şema uygulamanınki, her model her bağlamda 5 kez, yalnız ZDR sağlayıcıları (`/endpoints/zdr`, güvenlik saklaması yok: Gemma `makora`, `deepinfra`; Claude Haiku 5.5 ve Sonnet 5.5 yalnız `amazon-bedrock`, `google-vertex`; Claude'da `reasoning effort low`, Sonnet düşünmesiz çağrıyı reddediyor). Toplam 0,310 $.

| Model | S2: doğrulanmış KNT-226131 | S2: renk hücresi kumaşla aynı cümlede | S3 6. sıra | S3 1. sıra | İlk jeton (ort.) | Soru başına |
|---|---|---|---|---|---|---|
| Gemma 26B | 0/5 | 0/5 | 5 bulunamadı | 5 doğru cevap, OCR ile gizli | 0,6–0,9 sn | 0,0003–0,0004 $ |
| Haiku 5.5 | **3/5** (2 koşuda alıntı uyuşmazlığı ya da "belgede olmayan bilgi" iddiası) | 5/5 | 3 netleştirme (cep satırları), 1 doğru, **1 yanlış satır** | 5 doğru, gizli | 4,5–6,3 sn | 0,0011–0,0014 $ |
| Sonnet 5.5 | 0/5 | 0/5 | 4 doğru ("Front Rise 12 1/4"), 1 netleştirme | 5 doğru, gizli | 2,4–4,6 sn | ≈0,019 $ (~50 kat) |

Okuma: Haiku S2'yi çözüyor ama ilk jeton 0,6–0,9 sn'den 4,5–6,3 sn'ye çıkıyor (gerçek zamanlı cevap şartı); Sonnet ~50 kat maliyetli ve S2'yi çözmüyor (renk hücresini ayrı cümlede alıntılıyor, kumaş cümlesine alıntısında olmayan "100"ü yazıyor). Haiku S3'ün 6. sıra bağlamında bir koşuda "ön ağ"ı yanlış satıra bağladı ("ön cep ağzı (Front Pocket Opening) 7"); değer yalnız OCR belirsizliği yüzünden gösterilmedi, belirsizlik olmasaydı doğrulanmış yanlış olabilirdi. Aynı bağlamda tutarsızlık: Gemma S2'nin aynı 8 kaynağıyla (#2195–2197) cevap, bulunamadı, cevap verdi; temperature 0 tutarlılık sağlamıyor. S3'te Gemma "ön ağ"ı "Front Rise" ile yalnız satır 1. sıradayken eşleştiriyor (istemin "niteleyici kaynakta yoksa bulunamadı" ve "satır adının söylemediği anlamı verme" kuralları birlikte "bulunamadı"ya itiyor); S3'ün doğru değeri her modelde OCR belirsizliğiyle gizli, önce kesir kararı (açık notlar). Yeniden düşünülür: gerçek kullanımda niteleyici sorularında gizleme oranı yüksek çıkarsa ya da daha hızlı düşünen ZDR'li bir model çıkarsa.

### 0020: Tek belge varyantlarını listeleme (A yolu) denendi, geri çekildi
Tarih: 2026-11-20 (karar), 2026-11-21 (deneme ve geri çekme). Ürün sahibi kararı. Dal: `varyant-listeleme` (`d6109d6`; birleştirilmedi, referans olarak `origin`'de duruyor).

**Sorun.** Soru bir varyantı (beden, renk yolu, kıdem dilimi) söylemediğinde model netleştirme soruyor. İki belge arasında seçenekler belge adıyla düğme oluyor; tek belgenin içinde seçenekler bir satırın sütunları ya da aynı bölümün satırları olduğu için düğme üretilemiyor ve kullanıcı seçeneksiz bir soruyla kalıyor ("Hangi beden için?"; sınır setinde D4, D6).

**Denenen (A yolu, yalnız istem).** Aday belge tekse ve en çok 3 varyant görünüyorsa her varyant kaynaktaki adıyla, ayrı cümlede, kendi alıntısıyla listelenir; fazlaysa ya da iki ve daha çok belge varsa netleştirme sorulur; tamlık iddiası yok. İstemin 7. kuralı yeniden yazıldı, 9. kurala istisna cümlesi eklendi. Yanında: aynı adlı belgelerin modele ayrı gösterilmesi ve puanlayıcıda tek belgede listelemenin geçmesi (`listed_variants`).

**Ölçüm (Mac, 2026-11-21; taban 7 ve taban 11, kırkar soru, canlı; karşılaştırma `evals/output/mac-main-2026-11-21`).**

| Set | main | dal, ilk istem | dal, düzeltilmiş istem |
| --- | --- | --- | --- |
| Taban 7 | 38/40, doğrulanmış yanlış 0 | 38/40, doğrulanmış yanlış 1 | 38/40, doğrulanmış yanlış 0 |
| Taban 11 | 38/40, doğrulanmış yanlış 0 | 37/40, doğrulanmış yanlış 1 | 38/40, doğrulanmış yanlış 1 |

- Hedef soru `dikim-excel-netlestir`: ilk istemde iki sette de listeledi (taban 7'de üç ayrı cümle, geçti; taban 11'de üç bedeni tek cümlede, kaldı). Düzeltilmiş istemde ("değerleri tek cümlede birleştirme", "seçenek sorudaysa kısa ver") iki sette de yeniden netleştirme sordu. `ik-netlestir` hiçbir ölçümde listelemedi.
- İki belgeli netleştirme soruları (`dikim-revizyon-netlestir`, `sql-netlestir`) üç ölçümde de netleştirme sordu.
- "Doğrulanmış yanlış" sayılan tek soru `dikim-sohbet-1-t4` (takip sorusu; beklenen yalnız M bedenin değeri). Dal üç bedeni adlarıyla listeledi; değerler ve bedenler kaynakta doğru, ekranda yanlış değer yok. Puanlayıcı beklenmeyen iki değeri yabancı saydı. Kök neden cevap isteminde değil (açık notlar).
- Tek değerli cevapların biçimi bozuldu: çıplak değer ("103,0") tam cümleye döndü ("PNT-1126 modelinde S beden dış paça 103,0."). Düzeltilmiş istemde iki sette 25 cevap `main`'dekinden belirgin uzundu (taban 7'de 11, taban 11'de 14); ilk istemde de görüldü, sayılmadı. Hepsi doğru ve geçiyordu.
- FastReact ve sınır seti ölçülmedi; kabul koşulları taban setlerinde tutmayınca ölçüm durduruldu. Harcanan toplam 0,027 USD. "Aynı belgede farklı ürün" cümlesini sınayan soru ölçüm setlerinde yoktu.

**Gerekçe.** Aynı istemle hedef sorularda kararsız davranış (bir ölçümde listeledi, diğerinde sordu); tek değerli cevapların biçimi bozuldu (25+ cevap uzadı); listeleme yalnız istemle güvenilir değil. İstem üçüncü kez değiştirilip ölçülmedi.

**Karar.** A yolu geri çekildi; `varyant-listeleme` birleştirilmedi. Düğme etiketli netleştirme de reddedilmişti (2026-11-20: kaynaktan türetilen etiketler kullanıcıya bir şey söylemiyordu, plan büyüktü, her tıklama ikinci bir model çağrısı istiyordu). Netleştirme bugünkü hâliyle kalır: iki ve daha çok belgede düğmeli, tek belgede seçeneksiz soru. `#a2eaf46` ve `#2ad898d`'nin kuralları geçerli.

**Dalda kalan, ileride işe yarayabilecekler.** Aynı adlı belgeleri modele ayrı gösteren `format_sources` değişikliği ("Ad (2)"; `ayni-adli-belgeler` dalında yapıldı); puanlayıcıdaki `listed_variants`; istem metni.

### 0021: Belirsiz komşu hücreyi yok sayma (t2) denendi, geri çekildi; A5 yerinde kalır
Tarih: 2026-11-21. Ürün sahibi kararı. Dal: `ocr-belirsiz-komsu-hucre` (`7b9b115`; birleştirilmedi, referans olarak `origin`'de duruyor).

**Sorun.** Taramadan okunan bir tablo satırında bir hücre belirsizse (iki okuma uyuşmamışsa) ve model satırın tamamını alıntılarsa cümle gizleniyor; değeri sorulan hücre belirsiz olmasa da. Günlükteki tanı (2026-11-21, uygulama): "SIPARIS_KALEM tablosunda DEPO_KODU uzunluğu kaç?" → `OCR değeri belirsiz: ['VARCHAR']`; alıntı "Tablo: SIPARIS_KALEM | Kolon: DEPO_KODU | Tip: VARCHAR | Uzunluk: 59", gizlenen cümle "…DEPO_KODU uzunluğu 59'dur." (59 belirsiz değil, doğru). Taban 7 ve taban 11'de `sql-ekran-uzunluk` aynı nedenle kalıyor. 19 Kasım'da bu gizleme kabul edilmişti (A5; açık notlar).

**Denenen (t2, dar hâliyle).** Belirsiz parça alıntıda geçiyor ama cümlede geçmiyorsa, yalnız şu durumda yok sayılır: tablo satırı, parça etiketli bir hücrenin değerinde ("Tip: VARCHAR") ve cümle o hücreye değinmiyor (sütunun adını ekleriyle anmıyor, hücrenin değerinden sayı ya da kod taşımıyor, parçanın alt parçasını yazmıyor). Etiketsiz hücrede ve tablo dışı metinde bugünkü gizleme kalır. A5'in riskini sınayan testler yazıldı ve geçti ("tipi metin", "metin tipinde 59", "uzunluğu on dokuz", "TR0001 onaylı", föy satırında "eksi toleransı -3 1/8" gizli; "DEPO_KODU uzunluğu 59" ve belirsiz toleransın yanındaki kesin ölçü geçiyor); `pytest` 1524.

**Kural 1 denetimi (geri çekmenin nedeni).** Kuralın Mac'in uygulama indeksinde neyi açacağı sayıldı: belirsiz parça taşıyan 1.283 tablo satırının 721'inde en az bir değer açılıyor; toplam 1.276 hücre, 1.270'i tech pack'lerde (Sort Order 572, Dim 264, Qty 80, Material Details 59, kalanı beden hücreleri). Bu üst sınırdır: denemede cümle yalnız açılan hücrenin etiketini ve değerini taşıyordu. Açılacak tech pack hücrelerinden sabit tohumla rastgele 10'u sayfa görüntüsüyle karşılaştırıldı: 9'u birebir uyuştu, 1'i uyuşmadı. 6013448 s.16, malzeme tablosu, Material Details: indekste "KNT-222890/PacMan Fleece -2 x 2 Rib - …", görüntüde "PacMan Fleece - 2 x 2 Rib - …" (ayraç tire sayıya yapışmış, "−2" gibi okunuyor). İkinci okuma bu hatayı işaretlememiş; satır bugün yalnız aynı satırdaki "Qty: 0.1861" belirsiz olduğu için gizli.

**Gerekçe.** Taranmış sayfalarda işaretlenmemiş okuma hataları var ve bugün bir kısmı yalnız komşu hücrenin belirsizliği sayesinde gizli. Set A ölçümünde (0010) yeni hat 3.121 değerin 87'sini yanlış gösteriyordu; gizlemeyi azaltmak gösterilen yanlışı artırır. 10 örnekte 1 uyuşmazlık kural 1 için kabul edilemez; oranı daha iyi bilmek için daha büyük bir örnek gerekir ve kural yine aynı sınıftaki hatayı açar. A5 bu kanıtla korunuyor: belirsiz hücre alıntıda olup cümlede geçmese de cümle gizlenir.

**Karar.** t2 uygulanmıyor; dal birleştirilmedi. Doğrulayıcı değişmedi. `sql-ekran-uzunluk` iki taban setinde kalan soru olmaya devam eder (cevap gizli, yanlış değil); sınır setinde A5 gizli kalır.

**Yeniden düşünülür.** İkinci okuma serbest metinli hücrelerdeki boşluk ve ayraç hatalarını da işaretler hâle gelirse, ya da kural yalnız kısa sayısal hücrelerle sınırlanıp o hücrelerde ayrı ve daha büyük bir görüntü denetimi temiz çıkarsa. İkisi de set B ölçümü ister.

### 0022: Eski OCR yolunun (gömülü görsel) set A ölçümü; eşikler ölçümden önce belirlendi
**Tarihsel kayıt:** yol [0028](#karar-0028) ile kaldırıldı; `legacy_ocr` işareti ve `evals/run_embedded_images.py` silindi (koşucu git geçmişinde).

Tarih: 2026-11-21. Ürün sahibi kararı. Dal: `eski-yol-olcumu`. Araç: `evals/run_embedded_images.py`. **Bu kayıt sonuçtan önce yazıldı; sonuç ve karar en altta (2026-11-21).**

**Neden.** Eski OCR yolunun (karar 0018) bugünkü doğruluğu ölçülmemiş. 0010'daki "mevcut hat" sayıları (3.121 değerin 788'i yanlış) `c79e4ce`'deki koda ait: o hat taranmış sayfayı ocrmypdf ile okuyor, tablo hücrelerini bulut modeliyle yeniden okuyordu. O günden beri hücre okuyucu ve ızgara okuma silindi (0013), ikinci okuma sayımla karşılaştırılıyor, ortak tablo korumaları eklendi. Pilotta gömülü görseller bu yoldan geçecek.

**Kapsam düzeltmesi.** Tarayıcının OCR'ladığı PDF'ler eski yola gitmez: sayfayı kaplayan görüntünün üstündeki görünmez ya da altında kalan metin "başka aracın OCR çıktısı" sayılır, sayfa metin katmansız kabul edilir ve sayfa okuyucusuna gider (`is_ocr_layer`; okuyucu yoksa belge "Okuyucu bekleniyor"). Eski yola gidenler: metinli sayfadaki gömülü görseller (RapidOCR + Tesseract) ve görünür metinli, büyük görüntülü ya da zayıf metin katmanlı sayfalar (ocrmypdf). Bu ölçüm yalnız birincisini kapsar.

**Kurgu A (gömülü görsel, çözünürlük korunarak).** Set A benzetiminin 5 tarama PDF'i (30 sayfa) ve 12 telefon fotoğrafı (0009) kullanılır. Her sayfa görüntüsü, tek satır metni olan dijital bir sayfaya resim olarak gömülür; resim sayfanın yarısından azını kaplar, sayfa metinli sayılır ve görseli gömülü görsel yolu okur. Ölçek korunur: görsel, hattın 300 dpi çizdiği sayfada kendi piksel boyutundadır (küçültme yok, kayıplı sıkıştırma yok). Yönlendirme zorlanmaz; bir sayfa okuyucuya ya da ocrmypdf yoluna düşerse koşu durur. Sayfa okuyucusu çalıştırılmaz ("set A'ya okuyucu çalıştırma" kuralı korunur).

**Puanlama.** Dondurulmuş betik (`evals/results/2026-11-16-set-a-benzetim/puanla.py`) ve dondurulmuş `evals/ocr_score.py`, değiştirilmeden. Dondurulmuş `hat.py` bugünkü kodla çalışmaz (silinen hücre okuyucuyu içe aktarır); koşucu aynı biçimde çıktı üretir. Çıktı 0010'daki tablonun satırlarıdır: doğru gösterilen, yanlış gösterilen (bağ kopması, yanlış karakter, ayraç), atlama, gizlendi (doğruydu / yanlıştı); toplam, tarama ve fotoğraf.

**Eşikler (ölçümden önce; ölçü 3.121 değer içinde yanlış gösterilen sayısı).** Karşılaştırma noktaları: okuyucu hattının 87'si (%2,8) ve eski ölçümün 788'i (%25).

| Yanlış gösterilen | Yapılacak |
| --- | --- |
| ≤ 87 | Eski yol bu hâliyle kalır; "Taramadan okundu" rozeti zorunlu. |
| 88–250 | Kalır; pilot öncesi ikinci okuma karşılaştırması sıkılaştırılır (0018'deki bilinen zayıflık) ve yeniden ölçülür. |
| > 250, ya da yanlışların çoğu bağ kopması | Bu yoldan gelen tablo değerleri pilotta gösterilmez: ya okuyucuya yönlendirilir ya da yalnız kaynak görüntüsüyle verilir. |

Ek koşul: yanlış az çıksa da doğru okunan değerlerin yarısından fazlası gizleniyorsa bu ayrıca kullanılabilirlik sorunu olarak yazılır.

**Puanlayıcının sınırı (kod incelemesinde bulundu, ölçümden önce).** Dondurulmuş puanlayıcı `figure` türü parçayı tek hücreli satır sayar. Gömülü görsel tablo olarak tanınmazsa değerleri doğru okunsa da çoğunlukla "atlama" çıkar, "yanlış gösterilen" de olduğundan düşük görünür (incelemedeki deneme: 2.277 değer kusursuz `figure` satırı olarak verildiğinde 216 doğru, 2.052 atlama; aynı içerik `table_row` olarak 2.194 doğru). Yani düşük bir "yanlış gösterilen" tek başına "≤ 87" satırını kanıtlamaz. Koşucu bu yüzden taramadan okunan parçaların türünü de yazar (`ozet.json`). **Ölçüm öncesi karar (ürün sahibi, 2026-11-21; sonuçtan önce belirlendi):** atlama değerlerin %20'sini geçerse sonuç eşik tablosuna oturtulmaz, "ölçülemedi" yazılır; o durumda sonraki adım puanlayıcının `figure` satırlarını sayabilmesi olur.

**Nerede ölçülür.** Windows'ta: sonuç pilotun Windows'taki eski yolunu temsil etmeli (ocrmypdf, Tesseract ve RapidOCR'ın sürümleri ve çıktıları işletim sistemine göre değişebilir). Komut açık notlarda (Yarım kalan). Bulut maliyeti 0. Mac'te yalnız tek belgeyle kuru deneme yapıldı (`syn2_s6_foto`: sayfa metinli sayıldı, görsel gömülü görsel yolundan okundu, puanlama çalıştı; 9 sn); tam koşu çalıştırılmadı.

**Sınırlar.** Set A'nın sonuçları görüldü ve eski yol o günden beri gerçek föylere bakılarak değişti (yeniden işleme turu); bu, bugünkü durumun ölçümüdür, temiz bir kilitli karşılaştırma değil. Benzetim gerçek kâğıt ve tarayıcı değil (0009). Gerçekte yapıştırılan görsel çoğu zaman küçültülür; bu kurgu küçültmesiz durumu ölçer, piksel piksel aynı görüntüyü değil: hat görseli sayfa çiziminden keser ve çizim yeniden örnekler. Mac'te ölçülen fark (kaynak ile hattın kestiği görsel, gri düzeyde): fotoğrafta (`syn2_s6_foto`) piksellerin %7,8'i aynı, ortalama fark 5,4 / 255; taramada (`syn1_tarama` s.1) %57'si aynı, ortalama fark 0,65; taramada kesit bir piksel sütunu dar. Bu, uygulamada her gömülü görselin geçtiği yolun kendisidir. Küçültmenin etkisine ve kurgu B'ye (görünür damgalı tarama, ocrmypdf yolu) A'nın sonucundan sonra bakılacak.

**Sonuç (Mac, 2026-11-21; `main` `178afdf`, tek koşu, 17 kaynak, 148 sn, bulut maliyeti 0).** Ölçüm makinesi Mac'e alındı (açık notlar); Windows'ta doğrulama yapılmadı. Koşu durmadı: hiçbir sayfa okuyucuya düşmedi, hiçbir görsel atlanmadı.

| | Toplam | Tarama | Fotoğraf |
|---|---|---|---|
| Değer | 3121 | 2277 | 844 |
| Doğru gösterilen | 273 | 206 | 67 |
| Yanlış gösterilen | 172 | 128 | 44 |
|   bağ kopması | 153 | 112 | 41 |
|   yanlış karakter | 19 | 16 | 3 |
|   ayraç | 0 | 0 | 0 |
| Atlama | 2108 | 1524 | 584 |
| Gizlendi (doğruydu / yanlıştı) | 335 / 233 | 250 / 169 | 85 / 64 |

Taramadan okunan 781 parçanın 666'sı `figure`, 115'i `table_row`.

- **Ölçülemedi.** Atlama 3.121 değerin 2.108'i (%67,5); ölçüm öncesi karardaki sınır %20 idi. Sonuç eşik tablosuna oturtulmaz ve 0010'daki 788 ve 87 ile doğrudan karşılaştırılmaz.
- **Alt sınır.** Puanlanabilen değerlerde 172 yanlış gösterilen var; 153'ü (%89) bağ kopması. Puanlayıcı `figure` satırlarını sayabilse bu sayı yalnız artar (puanlanan satırlar aynı kalır, yenileri eklenir). Alt sınır tek başına okuyucu hattının 87'sinin iki katıdır.
- **Gizleme.** Doğru okunan 608 değerin 335'i (%55) gizli; ek koşuldaki kullanılabilirlik sorunu.

**Karar (ürün sahibi, 2026-11-21; alt sınıra dayanılarak).** %20 kuralı yanlış güveni önlemek içindi; olumsuz sonucu engellemez. Eski yoldan (gömülü görsel) okunan değerler pilotta doğrulanmış gösterilmez. Puanlayıcı düzeltmesi yapılmayacak: sonuç kararı değiştirmez, dondurulmuş dosyalar korunur. Uygulaması ayrı iştir (plan onay bekliyor); 0019'daki "yanlış değer açığını kapatan sıkılaştırma" istisnası kapsamında yazılacak. Küçültmenin etkisi ve kurgu B bu kararla gereksizleşmedi ama öncelikleri düştü; açık notlarda.

**Uygulama (2026-11-21, dal `eski-yol-dogrulanmaz`; ürün sahibi kararı).** 0019'daki "yeni kural yok" kararının istisnası: yanlış değer açığını kapatan sıkılaştırma (kural 1 önceliklidir). Dayanak bu kararın alt sınırıdır (puanlanabilen değerlerde 172 yanlış gösterilen, %89'u bağ kopması).

- **Kural.** Eski OCR yolundan okunan parça işaretlenir (`legacy_ocr`); cümlenin dayandığı kaynaklardan biri işaretliyse cümle doğrulanmış sayılmaz, gizlenir ve kaynak görüntüsüyle "taramadan okundu, kaynağa bakın" metni gösterilir (arayüz ve ses değişmedi). Günlükteki tanı: `eski OCR yolundan okundu`. Okuma belirsiz işaretlenmemiş olsa da geçerlidir; ikinci okumanın uyuşması yetmez.
- **Kapsam.** İki yol: metinli sayfadaki gömülü görsel (RapidOCR + Tesseract) ve ocrmypdf'in yeni metin katmanı yazdığı sayfalar (zayıf ya da taranmış metin katmanlı). İkincisi ölçülmedi (kurgu B); ölçülmemiş yol doğrulanmış görünmez. Sayfa okuyucusundan gelen parçalar işaretlenmez ve eskisi gibi "kısmen doğrulandı" kalır. ocrmypdf'in belgenin kendi metin katmanını koruduğu sayfa (yeni katman seçilmedi) taramadan okunmuş sayılmıyordu, yine sayılmaz.
- **Kural sürümü.** PDF ve Office 20. Yalnız metinli, zayıf ya da taranmış katmanlı sayfası olan belgeler "Eski kural" olur; tamamı okuyucudan geçen taranmış belgeler olmaz. Eski kuralla kalan belgede işaret yoktur: yeniden işlenene kadar eski yolun değerleri eskisi gibi kısmen doğrulanmış görünür.
- **Mac verisi.** "Eski kural" olan 9 belge (dikim-pdf, dikim-rev-a, dikim-rev-b, dikim-word, ik-ihbar, ik-izin, sql-ekran, sql-kilavuz, sql-notlar; taranmış föy yok) uygulamada yeniden işlendi: 24 sn, okuyucusuz, bulutsuz. 6.299 parçanın 2'si işaretli (ikisi de `sql-ekran`); `from_ocr` parça sayısı 2.586, değişmedi.
- **Ölçüm (Mac; taban 7 ve taban 11, kırkar soru, bir kez; çalışma klasörlerinde aynı 9 belge yeni kuralla işlendi, okuyucu belgelerinin parçaları aynen kaldı; `evals/output/eski-yol-2026-11-21`).** İki set 39/40, doğrulanmış yanlış 0; kalan soru `sql-ekran-uzunluk` (cevap gizli). Cevap kayıtları `main` tabanıyla (`mac-main-2026-11-21`) kırk soruda da aynı; rozetler aynı (22 doğrulandı, 3 kısmen doğrulandı, 1 doğrulanamadı, 14 rozetsiz). Yeniden işlenen belgelerin parçaları işaret dışında bire bir aynı çıktı. 33 ve 35 soru önbellekten; 7 ve 5 takip sorusunda yalnız tamamlama çağrısı canlıydı (araç bu soruların maliyetini 0 raporladı; ayrıca ölçülmedi).
- **Uygulamada.** "SIPARIS_KALEM tablosunda DEPO_KODU uzunluğu kaç?" bir kez soruldu: cümle gizli, kaynak (sql-ekran s.1) görüntüsüyle veriliyor; günlükte `OCR değeri belirsiz: ['VARCHAR']` ve `eski OCR yolundan okundu`. Bu satırda eski tanı da sürdüğü için yeni işaretin tek başına gizlediği durum testle gösterildi (`test_item_resting_on_the_legacy_ocr_path_is_never_verified`), uygulamada değil.
- **Bedeli.** Word'e ya da PDF'e yapıştırılmış tablo görüntüsünden gelen doğru değerler de gösterilmez; kullanıcı kaynağa bakar. Açılması için eski yolun ölçülebilir ve temiz çıkması gerekir (bu kararın sonucu tersini gösterdi) ya da gömülü görsellerin okuyucuya yönlendirilmesi (ayrı karar).
- **Kod incelemesinde bulunanlar (tek düzeltme turu).** Kapatılan: netleştirme adayları "aynı cevabı veriyor" yolunda diğer belgenin eşleşen parçası eski yoldan okunduysa eşleşme sayılmaz, netleştirme sorusu kalır (`ask/agreement.py`; testi var). **Bilinen sınır (ürün sahibi kararı, 2026-11-22: düzeltilmeyecek):** ocrmypdf sayfasında okunan bir başlık parça olmaz, sonraki parçaların bölüm adı olur; işaret bölüm adına taşınmaz. Başlıktaki yanlış okunmuş bir kod, iki okuma uyuştuysa, alıntısı dijital bir parçadan gelen cümlede doğrulanmış geçebilir (sayılar geçemez, alıntıda olmak zorundadır). Yalnız ocrmypdf yolunda; gömülü görsel başlık üretmez. Bugünkü veride böyle parça yok (ocrmypdf'ten gelen parça 0). Önerilen düzeltme (işaretli başlığın kod ve sayılarını bölümün belirsiz listesine eklemek) başlığın altındaki dijital parçalarda aynı kodu taşıyan cümleleri de gizlerdi ve parça çıktısını değiştirirdi; bu yüzden uygulanmadı. Ayrıca aynı yolda okuyucudan gelen parça da (işaretsiz) eşleşme sayılıyor ve cevap "doğrulandı" çıkıyor; önceden de böyleydi, okuyucu yoluna bu işte dokunulmadı.

### 0023: Sesle söz kesme; eşik kullanıcının sesiyle kilitlenmez, halkaya basınca söylenen gönderilir
Tarih: 2026-11-22. Ürün sahibi kararı ve Mac'te elle deneme. Dal: `soz-kesme-esigi`.

**Sorun.** Sesli modda sistem konuşurken kullanıcı araya girince konuşma çoğu zaman durmuyordu. Söz kesme (`#dba91ee`, 9 Kasım) mikrofonu dinler; eşik en az 0,05 ya da duyulan en yüksek "yankının" 1,8 katıdır ve bunun üstünde 300 ms ses gerekir. Yankı engelleme açıktır (`echoCancellation`, `noiseSuppression`, `autoGainControl`).

**Ölçüm (Mac, dizüstü hoparlörü; geçici ölçüm satırı, silindi).** Sistemin kendi sesi mikrofonda en çok 0,035; kullanıcının sesi 0,10–0,27, hece aralarında 0,05'in altına düşüyor. İki ayrı kilitlenme ölçüldü:
- Eşiğin hemen altında kalan her an "yankı" sayılıp tepe değeri oluyordu. Kullanıcının hece araları eşiği üç dilimde 0,05'ten 0,494'e çıkardı; ses 0,275'te kaldı, söz kesilemedi.
- Turun ilk yarım saniyesindeki en yüksek ses "kalibrasyon" diye yankı sayılıyordu. O an sistem henüz konuşmuyor; duyulan sorunun son hecesiydi (0,08), eşik tur boyunca 0,144'e kilitlendi.

**Karar.**
- Yankı tahmini yavaş yükselir (50 ms'de aradaki farkın %5'i), hiç düşmez. Turun ilk yarım saniyesinde ne söz kesme sayılır ne yankı öğrenilir. 0,05 tabanı, 1,8 katsayısı ve 300 ms değişmedi.
- Açılış selamı da sesle kesilebilir (önceden dinlenmiyordu).
- Sistem sustuğu anda kullanıcı en az 150 ms'dir konuşuyorsa kayıt atılmaz, sözün tamamı soru olur (kısa cevapların sonunda ilk sözcükler kayboluyordu). Tur hatayla bittiyse uygulanmaz.
- Dinlerken ses halkasına basmak "bitti" demektir: o ana kadar söylenen, sessizlik beklenmeden gönderilir; hiçbir şey söylenmediyse yok sayılır. Sistem düşünürken ya da konuşurken basmak eskisi gibi susturur. "Bitti"nin hemen ardından gelen ikinci dokunuş (600 ms) soruyu iptal etmez.

**Sonuç.** Son denemede 7 turun 5'inde söz kesildi; kesilmeyen turun nedeni ikinci kilitlenmeydi ve ondan sonra düzeltildi. Son hâli elle bir kez daha denenmeli (bu kayıt yazılırken sonucu bilinmiyordu). Arayüz testleri 151 geçti.

**Kabul edilen risk (kod incelemesi, benzetimle).** Koruma tek bir cihazda ölçülen yankıya (en çok 0,035) göre ayarlı. Yankısı 0,05'in üstünde dalgalanan cihazda (yankı engellemesi zayıf tarayıcı, yüksek sesli harici hoparlör, tablet) sistem kendi sesiyle kendini eskisinden kolay keser: rastgele dalgalı yankıyla 200 denemede kendi sözünü kesme, tepe 0,07'de 1 → 12, 0,08'de 3 → 73, 0,10'da 18 → 190. Aynı cihazlarda cevabın son hecesinin yankısı "sistem sustuğu anda süren söz" sayılıp sistemin kendi cümlesi soru olarak sorulabilir. Eski "kalibrasyon" bu korumayı uygulamada zaten sağlamıyordu (ölçüm sistem konuşmadan yapılıyordu); kaybolan, eşiğin altında kalan her ana sıçrayan tahmindi. Atölyede ve tablette denenmeden pilot cihazı için geçerli sayılmaz.


<a id="karar-0024"></a>

### 0024: Okuyucu için llama.cpp (işlemci) yolu bırakıldı; eski OCR yolu kalıyor, görüntü küçültme şimdilik yok
Tarih: 2026-11-22. Ürün sahibi kararı.

**Ne denendi.** Windows'ta okuyucu süreç içi kipte (`VA_PAGE_READER=local`) işlemcide sayfa başına 50 sn ile 16 dk sürüyor (0015). Kurulu PaddleOCR 3.7 aynı modeli `llama.cpp` sunucusuyla çalıştırabiliyor; kod değişmeden, yalnız ayarla (`VA_PAGE_READER=llama-cpp-server@http://127.0.0.1:8112/v1`) Mac'te denendi. Model: `PaddlePaddle/PaddleOCR-VL-1.6-GGUF` (936 MB + görüntü kodlayıcı 882 MB, Apache-2.0); llama.cpp Homebrew'den, yalnız işlemci. Set A'ya dokunulmadı; belgeler `dikim-foto.jpg` ve `dikim-tarama.pdf`. Bulut maliyeti 0.

**Hız (Mac M4 Pro; her belge ilk kez okunurken):**

| Arka uç | `dikim-foto` (1 sayfa) | `dikim-tarama` (3 sayfa) |
|---|---|---|
| MLX (Mac'in bugünkü yolu) | 4,1 sn | 9,1 sn |
| Süreç içi kip (Windows'taki yol) | 41,2 sn (model yükleme dahil) | 36,4 sn |
| llama.cpp, yalnız işlemci | 57,9 sn (ilk açılış dahil) | 157,7 sn |

- Taramada llama.cpp süreç içi kipten yaklaşık 4 kat yavaş. Sürenin neredeyse tamamı görüntü kodlamada (blok başına yaklaşık 20 sn); metin üretimi hızlı.
- Aynı belge ikinci kez okununca llama.cpp 13,6 sn; bu önbellek etkisi, gerçek belgelerde her sayfa yenidir.
- Fotoğraf satırı adil bir karşılaştırma değil: iki süre de ilk açılış payı taşıyor.

**Okuma farkları.** Sayılar ve kodlar üç arka uçta birebir aynı, belirsiz değer 0. Farklar yalnız sayı içermeyen metinde; her arka uç iki koşuda kendi içinde aynı sonucu verdi:

| Belge | MLX ve süreç içi | llama.cpp |
|---|---|---|
| `dikim-foto` başlık | "Ổlộcũ fōyũ" (bozuk) | "ölçü föyü" (doğru) |
| `dikim-foto` sütun adı | "Toierans" (bozuk) | "Tolerans" (doğru) |
| `dikim-tarama` bölüm adı | "Etiket kodları" (doğru) | "Etiket kodlari" (bozuk) |

**Karar.**
- llama.cpp işlemci yolu bırakıldı: Windows'ta okumayı hızlandırması beklenmiyor.
- Eski OCR yolu (ocrmypdf, RapidOCR) kalıyor ([0018](#karar-0018)). Kaldırılması, sunucu ya da ekran kartı kararına kadar kapandı. **Bu madde tersine döndü: [0028](#karar-0028).**
- Taranmış belgeler [0015](#karar-0015)'e göre Mac'te işlenir, veri taşınır.
- Okuyucuya verilen görüntü şimdilik küçültülmez (set B'de denenecekler listesinde kalır, 0010).
- İndirilen model dosyaları (`data/models/paddleocr-vl-gguf/`) ve Homebrew'deki llama.cpp (ve yalnız onun için kurulan ggml, libomp, openssl@4) 22 Kasım'da silindi.

**Yeniden düşünülür.** Okuyucu için ekran kartlı bir makine ya da sunucu gündeme gelirse; ya da Windows'ta ayar denemesi (iş parçacığı sayısı) yetmez ve GPU'lu llama.cpp (Vulkan, Intel Iris Xe) ayrı süreç olarak onaylanırsa (açık notlar, Windows hız teşhisi).

<a id="karar-0025"></a>

### 0025: Taranmış tabloda tekrarlanan başlık başlıktır; içerikten sonra gelen başlıklar kardeştir
Tarih: 2026-11-22. Ürün sahibinin bu tur için verdiği iş (açık notlar, Sıradaki işler madde 4). PR #138.

**Teşhis (düzeltildi).** 6029322 s.9 bir sayfa devamı değildi: başlık satırı aynı sayfada okunuyor, ama başlık hücresi rakamlı ("100: White // Venom Red"), altındaki değerler rakamsız ("As Artwork") olduğu için `_first_row_is_header` karşı kanıt sayıyor, satırlar başlıksız kalıyordu. Yüklü föylerde gerçek sayfa devamı (yeni sayfada başlık hiç yok) 0. Bölüm yolunda ilk başlık ("Cover Sheet Properties") içerikten sonra geldiği için bütün bölüm başlıkları onun altına giriyordu.

**Kurallar.**
- Tablonun ilk satırı, aynı belgenin **önceki sayfalarında yapıdan** başlık sayılmış bir satırla hücre hücre aynıysa (boşluklar yok sayılır) başlıktır. `header_fits` koruması aynen; tekrardan kabul edilen başlık öğrenilmez (zincirlenmez); aynı sayfa ve başka belge sayılmaz; etiketler sayfanın kendi okumasından gelir.
- İçerikten sonra gelen ilk düzeysiz başlık **kod taşımıyorsa** kök değildir; bu durumda düzeysiz başlıklar kardeştir. Kod taşıyorsa (önce "Sayfa 1 / 12", sonra "PNT-4417 ölçü föyü") kök kalır: kod bölüm yolunda olmalı (kod dizini, cevap denetimi; inceleme turunda bulundu).
- Kural sürümü PDF ve Office 23, görsel 16, SQL 3.

**Yapılmayanlar.** Sonraki sayfaya başlık taşımak (veride örnek yok; yeni tablo yanlış etiket alır, Kural B yanlış varyantı onaylayabilir). Karşı kanıtı gevşetmek (form tablolarında "Style #: Style Name" gibi yanlış etiket). Okuyucu etiketinden düzey (kod taşıyan kök başlık bölüm yolundan düşer).

**Ölçüm (Mac, `main` #138 koduyla).** 32 belge yeniden işlendi (42 dk, bulut 0), "Eski kural" 0. Okuyucudan geçen 252 sayfada eski ve yeni parçalar: yeniden okuma hiçbir değeri değiştirmedi; belirsiz işareti kalkan değer 0; bölüm yolu değişen parça 557; başlık kazanan satır 41 (4 tablo). **Kural 1 denetimi:** başlık kazanan satırlardan rastgele 10'u sayfa görüntüsüyle karşılaştırıldı, 10/10 uyuşuyor. Saklı set A okumalarında (73 tablo) kural hiçbir tabloyu değiştirmiyor. Taban 7, 11 ve FastReact belgeleri bu kodla yeniden işlendi: parçalar birebir aynı, cevaplar aynı (32/33, doğrulanmış yanlış 0; FastReact 18/18). Föy soruları (bir kez canlı): C1 ve C2 doğru, D6 netleştirme (bilinen), göğüs logosu ve poly bag netleştirme (yanlış doğrulama yok), TT-100157/001 gizlendi (açık notlar).

**Kalan risk.** 1. sayfada yapıdan yanlışlıkla başlık sayılan bir satır artık sonraki sayfalarda karşı kanıta rağmen başlık olur (birebir aynı ilk satır ve rakamlılığı değişen gövde gerekir; nadir). Set B ile ölçülecekler arasında.

<a id="karar-0026"></a>

### 0026: Okuyucu hattı set B'de: değerlerin %2,9'u yanlış gösteriliyor (0010'daki %2,8 ile aynı düzeyde)
Tarih: 2026-11-22. Ölçüm, bütün kod değişikliklerinden sonra (`main` `70d363f`, #138).

**Set B.** 0008'deki üreticiyle hiç görülmemiş yeni tohum (20261122): 5 belge × 6 sayfa (set A ile aynı sayfa türleri), 2.118 değer; 0009'daki benzetimle (aynı tohum) 5 tarama ve 12 telefon fotoğrafı, toplam 2.889 puanlanan değer. Dosyalar repoda değil; aynı tohumla yeniden üretilir: `uv run python -m evals.render.techpack_pdf --seed 20261122 --count 5 --set-label B --output <set klasörü>`, ardından `evals.render.imaging.degrade_set(<set klasörü>, <çıktı klasörü>, 20261122)`.

**Nasıl ölçüldü.** Her dosya uygulamanın bugünkü belge hattından geçti (`ingest_document`, okuyucu MLX, istekler tek tek, Tesseract ikinci okuması); parçalar dondurulmuş puanlamayla (`evals/ocr_score.py`, `pipeline_pages`, `score_page`) ve 0008'in toplama kurallarıyla puanlandı. Tek koşu, 386 sn, bulut maliyeti 0. Koşucu tek seferlik betik (repoda değil); donmuş `hat.py` artık çalışmıyor (silinmiş `cell_reader`'ı içe aktarıyor).

| | Set B (bugünkü hat) | Set A, 0010 (ölçülen aday) |
|---|---|---|
| Puanlanan değer | 2.889 | 3.121 |
| Doğru gösterilen | 985 (%34,1) | 1.325 (%42,5) |
| Yanlış gösterilen | 85 (%2,9): bağ kopması 67, yanlış karakter 18, ayraç 0 | 87 (%2,8): bağ kopması 37, yanlış karakter 50 |
| Atlama | 70 | 49 |
| Gizlendi (doğruydu / yanlıştı) | 1.396 / 353 | 1.335 / 325 |

Tarama 758 / 67 (doğru / yanlış gösterilen), fotoğraf 227 / 18. Sayfa türüne göre yanlış gösterilen: fark tablosu 39 (bağ kopması 35), BOM 20, ölçü 16, değerlendirme 6, kapak 4, yorum 0.

**Okuma.** Yanlış gösterilen oranı 0010'dakiyle aynı düzeyde (%2,9 ve %2,8); sayı küçülmedi, kural 1 açısından hat bugün de değerlerin yaklaşık 35'te 1'ini yanlış gösteriyor. Yanlışların türü değişti: yanlış karakter azaldı, bağ kopması (değer yanlış sütuna ya da etikete bağlı) arttı, en çok fark tablolarında. Gizlenen doğru değer %48'e çıktı. Karşılaştırma birebir değil: farklı tohum, farklı belge içeriği; set A ölçülen adayın okumalarıyla, set B uygulamanın hattıyla (çözünürlük, tek tek istekler, 0011–0025 kuralları) ölçüldü. Benzetim gerçek taramadan iyimser olabilir (0009).

**Bu ölçümün cevaplamadıkları.** 0010'daki "set B'de ayrıca ölçülecek" maddeleri (görülmemiş belgede başlık kuralı, hücre sayısı uyuşmayan tablo, görsel küçültme) ve 0025'in kalan riski ayrıca incelenmedi; yalnız toplam okuma sonucu ölçüldü.

**Karar gerektiren.** Kabul edilebilir yanlış gösterilen oranı açık bir ürün kararı değil (0012). → Karar verildi: 0027. Bağ kopmalarının fark tablolarında yoğunlaşması ayrı inceleme ister; bu ölçümle kural yazılmadı (her soru bir kez; sonuca göre ayar yapılmaz).

<a id="karar-0027"></a>

### 0027: Okuyucu hattının yanlış oranı pilotta "Taramadan okundu" rozetiyle kabul edilir; set B görülmüş sayılır
Tarih: 2026-11-23. Ürün sahibi kararı.

**Karar.** Taranmış belgelerde okuyucu hattı set B'de değerlerin %2,9'unu yanlış gösterdi (0026). Pilotta bu oran, taramadan okunan her cevapta "Taramadan okundu · kaynaktan kontrol edin" rozetiyle kabul edilir; rozet kaldırılmaz (açık notlar). Gerçek taramalar gelince yanlış oranı yeniden ölçülür.

**Set B görülmüş sayılır.** Sonuçlarına bakıldı; bundan sonra set B'ye bakılarak OCR ayarı yapılmaz. Okuma katmanında yeni bir tasarım ölçülecekse yeni tohumla set C üretilir ya da gerçek taramalar kullanılır.

<a id="karar-0028"></a>

### 0028: Tek OCR yapısı; eski OCR yolu kaldırıldı, gömülü görseller sayfa okuyucusunda (0018 ve 0024'ün eski yol maddesi tersine döndü)
Tarih: 2026-11-23. Ürün sahibi kararı. Dallar: `eski-ocr-yolu-kaldir` (#145), `gomulu-gorsel-okuyucuya`.

**Karar.** Taramadan okunan her şey tek yoldan geçer: PaddleOCR-VL okur, Tesseract ikinci kez okur, sayısı tutmayan değer gizlenir (0011). Eski yol (ocrmypdf, RapidOCR, Tesseract'ın iki kipi) tamamen kalktı. Belgeler şimdilik Mac'te işlenir; canlıda sunucuda.

**Neden.**
- Eski yoldan okunan değerler 0022'den beri doğrulanmış gösterilmiyordu (set A benzetiminde alt sınır 172 yanlış gösterilen). Yol ≈ 1.000 satır kod, test ve ölçüm aracı ile 7 paket taşıyordu.
- Önce gömülü görselleri hiç okumamak denendi (#145'in ilk hâli): taban 7 ve 11'de `sql-netlestir` netleştirme yerine doğrulanmış "MUSTERI_KODU kolonunun uzunluğu 66." verdi (doğrulanmış yanlış 0 → 1). Görseldeki seçenek (19) netleştirmeden sessizce düşüyordu. Bu kural 1 riski; altın seti değiştirme yolu reddedildi. Bu yüzden görseller de okuyucuya gider.

**Ne değişti.**
- Zayıf ya da taranmış metin katmanlı sayfa (`WEAK`, `SCANNED`) metin katmanı olmayan sayfa gibi bütünüyle okuyucudan geçer. Büyük görselli dijital sayfanın görünür metni de okuyucudan okunur (cevap "Kısmen doğrulandı"); bugünkü veride böyle sayfa 0. Dönmüş ya da başlangıcı kaydırılmış görselli metin sayfası da böyle (görsel kutusu çizimle örtüşmez).
- Metinli sayfadaki gömülü görsel kendi çözünürlüğünde (72–600 dpi) ve yalnız kendi bölgesi çizilip okuyucuya verilir; kutu sayfayla kesişir. Öğeleri sayfadaki yerine girer (B5: iki ürünlü sayfada görseldeki tablo kendi ürününün bölümünde kalır); görseldeki başlık bölüm açmaz, metin olarak kalır. Değerleri taramadan okunmuş sayılır ("Taramadan okundu" rozeti, 0027). Kısa kenarı 50 pt'den küçük görsel okunmaz, raporda uyarı çıkar.
- Okuyucu yoksa görseli olan metinli belge de bekler ("Okuyucu bekleniyor", 0011: belge ya tamamen okunur ya hiç). Önceden okuyucusuz işlenirdi.
- Silinen: ocrmypdf çağrısı ve katman seçimi (`junk_score`), RapidOCR okuması (`images.py`, `two_reading.py`), `legacy_ocr` işareti ve doğrulayıcı kuralı (0022), `ocr_checked`, `tesseract_language` (ikinci okuma her zaman `tur+eng`), `evals/run_embedded_images.py`. `count_mismatches` dondurulmuş kopyadaki gibi iki okumayı karşılaştırır.
- Paketler: `ocrmypdf`, `pikepdf`, `rapidocr`, `onnxruntime` `ingest` listesinden çıktı; kilitten 7 paket düştü (ocrmypdf, pikepdf, img2pdf, fpdf2, pdfminer-six, uharfbuzz, fonttools). `rapidocr` Docling'in kendi bağımlılığı olarak kilitte kalıyor (Docling'de OCR kapalı, kullanılmıyor); OpenCV yaması bu yüzden kalıyor. Tesseract kalır.
- Kural sürümü PDF ve Office 25 (24: eski yolun kaldırılması; 25: gömülü görseller okuyucuda). İkisi de yalnız metinli, zayıf ya da taranmış katmanlı sayfası olan belgeyi eskitir; tamamı okuyucudan geçen taranmış föyler eskimez.

**Windows ve 0015.** Okuyucu Windows'ta işlemcide sayfa başına 50 sn ile 16 dk arası sürer (0015); bir gömülü görsel de bir okuma demektir. Görselli Office ve PDF belgeleri bu yüzden Windows'ta yavaş işlenir; okuyucu ayarlı değilse bekler. Belgeler Mac'te işlenip veri taşınır (açık notlar, "Windows'a veri gönderme"); canlıda sunucu.

**Mac verisi.** Önce eski yolsuz kodla (24, 27 sn), sonra görsel okumasıyla (25, 31 sn, MLX okuyucu, bulut 0) aynı 9 metinli belge yeniden işlendi. Sonuç: 394 belge, 6.295 parça (#145 öncesiyle aynı sayı). Yalnız `sql-ekran` farklı: görseldeki iki kolon satırı artık okuyucudan ("Tablo: SIPARIS_KALEM | Kolon: MUSTERI_KODU | Tip: VARCHAR | Uzunluk: 19" ve "… DEPO_KODU … 59"), taramadan okunmuş işaretli, belirsiz değer yok; metni eski yolunkiyle aynı. Kural 1 denetimi: iki satır `sql-ekran` görüntüsüyle (görselden çizilip bakıldı) birebir. Taranmış 19 belgenin 2.580 parçası #145 öncesiyle bayt bayt aynı; öteki 8 belgenin içeriği aynı. Yedek: `~/va-yedek-2026-11-23` (#145 öncesi veritabanı ve vektörler).

**Ölçüm (Mac, `evals/output/tek-ocr-2026-11-23`).** 23 Kasım önbelleği ve çalışma klasörleri kopyalandı; yalnız kural sürümü eskiyen belgeler okuyucuyla yeniden işlendi (taranmışlar aynen). Kaynak metni değişen sorular bir kez canlı soruldu (taban 11: 2 soru; ≈ 0,0006 $).
- Taban 7: 33/33, doğrulanmış yanlış 0. Taban 11: 33/33, doğrulanmış yanlış 0 (7 takip turu iki koşuda da çevrimdışı önbellekte yok, sorulmadı).
- `sql-netlestir`: iki sette de netleştirme.
- `sql-ekran-uzunluk`: iki sette de görseldeki değerle cevaplandı, "kısmen doğrulandı" (önceden 0022 yüzünden gizliydi, #145'in ilk hâlinde "bulunamadı").
- Sınır setinde A5 ve B7 uygulamaya birer kez soruldu: "… MUSTERI_KODU kolonunun uzunluğu 19." ve "… DEPO_KODU kolonunun uzunluğu 59'dur.", ikisi de "kısmen doğrulandı". A5'teki gizleme (0021, `VARCHAR` iki okumada uyuşmuyordu) okuyucuda oluşmadı.
- FastReact: 18 cevap birebir aynı.
- İnceleme düzeltmesinden (ölçek, kutu, başlık) sonra taban setlerinin parçaları yeniden üretildi: metin aynı, yalnız taban 11'de tablo kutusunun sağ kenarında 0,001 pt yuvarlama farkı.

**Başka makinede.** Kural sürümü eskiyen belgede eski yolun parçaları (işareti okunmaz, 0022 kuralı yok) yeniden işlenene kadar aranır; `git pull` sonrası "Eski kural" görünen PDF ve Office belgeleri soru sorulmadan önce yeniden işlenmeli. Görselli belge okuyucu ister.

**Yeniden düşünülür.** Gerçek belgelerde görsel sayısı okuma süresini pilot için kabul edilemez kılarsa (ör. her sayfada logo), ya da gerçek fotoğraflarda okuyucunun yanlış gösterdiği değer set B oranını (%2,9, 0026) belirgin aşarsa.

<a id="karar-0029"></a>

### 0029: Fark tablosunun notu sorgu anında komşu parçadan okunur (okuyucu düzeltilene kadar)
Tarih: 2026-11-26. Ürün sahibi onayı. Dal: `fark-tablosu-notu` (#153); ek: `suzgec-kesimden-once` (filtre kesimden önce). Kod: `src/visual_agent/ask/steps.py` (`_table_note`, `retrieve`).

**Sorun.** 26 Kasım teşhisi: indeksteki 3.093 tablo satırının hiçbirinde `table_note` dolu değildi; fark filtresi (0006, 0013) hiçbir satırı ayıklamıyordu. Sayfa okuyucusu "Grade Rule Display: Increment" notunu tablonun içinde değil, tablodan sonra ayrı bir metin parçası (11 tablo) ya da tablonun son satırı (13 tablo) olarak veriyor; not ise yalnız tablonun içindeki kaplayan satırdan dolduruluyor (`pdf_tables.py`, `_with_table_context`). Örnek: 6026417 "MD ön ağ" sorusunda s.13'teki fark satırı (MD -3 3/8) s.11'deki ölçüyle (12 1/4) birlikte modele gidiyor, model aynı belgede iki değer görüp netleştirme soruyordu. Fark değeri ölçü diye verilebilirdi (kural 1).

**Kural.** Satırın notu doluysa o kullanılır. Boşsa ve satır sayfada kutulu bir tablodaysa (aynı sayfa ve aynı ilk kutu aynı tablodur): tablonun son satırı fark ifadesi taşıyor ve bir önceki satırı taşımıyorsa not odur; taşımıyorsa tablodan hemen sonraki parça aynı sayfada bir metinse not odur. Önceki satır koşulu inceleme turunda eklendi: satır metni "Sütun: değer" biçiminde olduğu için "Fark" adlı bir sütun her satırda yazılıdır; bu koşul olmadan böyle bir ölçü tablosu bütünüyle gizlenirdi. Tek satırlı tabloda son satır not sayılmaz. Sayfası ya da kutusu olmayan parçalar (Excel, Markdown, düz metin) değişmez. Parça kimliği "belge:sıra" olduğu için komşu parça bellekteki dizinden (`IdentifierIndex.chunk`) okunur; ek sorgu yoktur.

**Fark ifadeleri** (`_RELATIVE_RE`, büyük-küçük harf duyarsız, sözcük sınırıyla): increment, increments, incremental, delta, deltas, difference, differences, fark, farklar, farkı, farki, artış, artışlar, artışı. Türkçe "fark" listede. Eşleşmeyenler: "farkları", "farkın", "farkını", "artışları", "değişim", "sapma"; "farklı" (sözcük sınırı) da eşleşmez. Liste değişmedi; pilot Türkçe belgelerde nota başka bir ifade yazılıyorsa genişletilmesi ayrı karardır.

**Neden sorgu anında.** Okuyucuda düzeltme PDF kural sürümünü artırır: bütün PDF ve Office belgeleri "Eski kural" olur, taranmış belgeler Mac'te ≈ 40 dk yeniden işlenir, sonra veri paketi Windows'a taşınır. Sorgu anı kodu yeniden işleme istemiyor. Ek süre 50 sorguda p50 0,09 ms, p95 0,28 ms.

**İnceleme (yüklü 394 belge; karar kuralı: yanlış eşleşme 0 ve p95 ≤ 50 ms).** 591 tablo. Ardından aynı sayfada metin gelen 318 tablonun 11'inde not eşleşti, hepsi Increment; 14 "Absolute" notu ve FastReact'taki "incremental" metinleri hiçbir tabloya bağlanmadı. Notun tablodan önce geldiği vaka 0. Çok tablolu 11 sayfada not her seferinde hemen önündeki tabloya bağlandı (sayfa başlığı tablosuna değil). Son satır kuralı 13 tabloda, hepsi Increment; son olmayan satırında fark ifadesi geçen tek satır FastReact'taki `@DTVAR … Difference between 2 dates` (kurala girmiyor). Yanlış eşleşme 0.

**Etki.** 14 belgede 297 satır (not satırları dahil) artık kaynak olmuyor: 6013448 44, 6026399 30, 6026400 18, 6026411 9, 6026412 4, 6026416 28, 6026417 20, 6026418 25, 6026419 14, 6026420 25, 6026421 15, 6026450 23, 6026451 16, 6028355 26. Taban parça depolarında 0 satır (Windows'taki 20–21 Kasım kopyaları; güncel Mac parçalarıyla doğrulanmadı).

**Bilinen sınırlar.**
- Okuyucunun notu hiç okumadığı 4 fark tablosu yakalanmaz: 6026412 s.15, 6026422 s.13, 6026411 s.16, 6026400 s.16 (55 satır; sayfa görüntüsünde dördü de fark tablosu, 6026411 s.16'da not sayfada yazılı ama parçalarda yok). 55 satırın 53'ü ölçü satırı (Description taşıyor) ve 53'ünün ölçüsü aynı belgenin önceki bir mutlak tablosunda da var; mutlak karşılığı olmayan 0. Bu 53 satırda bir fark değeri ölçü diye gösterilebilir. Düzeltme yapılmadı; okuyucu düzeltmesiyle birlikte ele alınır.
- Görülmemiş bir belgede tablonun hemen ardından fark ifadesi taşıyan sıradan bir paragraf gelirse ya da yalnız tablonun son satırı böyle bir ifade taşırsa o tablonun satırları kaynak olmaz (gizleme yönünde; bugünkü indekste 0 vaka).
- Sayfaya bölünen tabloda not yalnız kendi sayfasındaki parçaya bağlanır: not s.14'teyse s.13'teki satırlar notu görmez. Yüklü föylerde her sayfanın kendi notu var (biçim 1 ya da 2); notu olmayan sayfa yukarıdaki 4 tablodur.
- ~~Filtre ilk 8 kaynağın içinden siler, yerine parça getirmez~~ Düzeltildi (2026-11-26, `suzgec-kesimden-once`): filtre 8'e kesmeden önce ilk 20 adaya uygulanır, ayıklanan satırın yerine sıradaki parça girer. Filtre bir şey ayıklamazsa ilk 8 eskisiyle birebir aynıdır (yüklü belgelerde 50 sorgunun 42'si; değişen 8 sorgunun hepsinde eskiden 8'den az kaynak gidiyordu). Ek süre, 20 aday üzerinde filtrenin 8 adaya göre fazlası: p50 0,09 ms, p95 0,40 ms (yukarıdaki p95 0,28 ms not aramasının 8 aday üzerindeki süresi).

**Canlı ölçüm (Windows, 2026-11-26, bir kez, 0,00030 $).** "6026417 şortta MD bedende ön ağ kaç?" → "bulunamadı". s.13'ün fark satırları ayıklandı, ama s.11'deki doğru satır (RS005, MD 12 1/4) da ilk 8'de değildi: modele 4 kaynak gitti (#106, #95, #94, #97). Çevrimdışı yeniden kurulum: yoğun kolda satır 12. sırada; BM25 sorgusu "front rise" içerirse füzyonda 2., "front crotch" içerirse 14. Kaynaklar "front crotch" çevirisiyle örtüşüyor (çeviri kaydedilmiyor). Filtre ilk 20'de uygulanıp sonra 8'e kesilseydi satır "crotch" çevirisinde de 7. sırayla kaynaklara girerdi. Bu değişiklik ürün sahibinin ayrı onayıyla aynı gün bu karara eklendi (aşağıdaki bilinen sınır maddesi ve ikinci canlı ölçüm). Hedeflenen sonuç ("netleştirme sormadan 12 1/4, doğrulanmış") bu ölçümde alınmadı; kök neden arama (çeviri sözcüğü), filtre değil.

**Canlı ölçüm, filtre kesimden önce (Windows, 2026-11-26, bir kez, 0,00039 $).** Aynı soru → yine "bulunamadı". Bu kez modele 8 kaynak gitti, s.11'deki doğru satır (RS005 "Front Rise from Top Edge - Straight", MD 12 1/4) 6. sıradaydı, s.13 satırı yoktu. Bilgi kaynaktaydı; model "ön ağ"ı "Front Rise" ile eşleştirmedi ve "bulunamadı" dedi. Aynı soruda 26 Kasım'da (iki "Front Rise" satırı varken) model eşleştirip netleştirme sormuştu. Katman: model (Türkçe terim ile İngilizce ölçü adı); istem değiştirilmedi, yeniden sorulmadı.

**Kaldırma.** ~~Sonraki planlı yeniden işlemede not okuyucuya taşınacak (satırların `table_note`'u dolacak); o zaman sorgu anı kodu (`_table_note`'un komşu arama kısmı ve `IdentifierIndex.chunk`) kaldırılacak.~~ Yapılmadı (2026-11-26, Mac teşhisi): okuyucu notu çıktısında vermiyor; sorgu anı kodu kalır (aşağıda, "Okuyucu notu teşhisi").

**Teşhis alanlarıyla üç koşu (Windows, 2026-11-26, 0,00120 $; `gunluk-teshis-alanlari`).** Modele giden soru üçünde de Türkçe özgün metin; çeviri yalnız BM25'e gidiyor. Koşu 1 ve 3: BM25 "front crotch length", doğru satır 6. sırada, model ham çıktısı `{"tur": "bulunamadi"}`. Koşu 2: BM25 "front rise", satır 1. sırada, model "MD bedende ön ağ 12 1/4." yazdı ve doğru alıntıyı verdi; cevap "OCR değeri belirsiz" diye gizlendi, çünkü bu satırda 12 ve 1/4 dahil değerlerin çoğu iki okumada uyuşmamış (`ocr_uncertain`). Sonuç: model "ön ağ"ı "Front Rise" ile eşleştirebiliyor (koşu 2), ama satır geride ve "Back Rise" kaynaklarda yokken eşleştirmedi (koşu 1 ve 3); tutarlı bir model hatası değil, çeviriye bağlı sıralama ile birlikte çalışan bir zayıflık. Doğru cevap çıksa bile bu satırın değeri okuma katmanında belirsiz olduğu için gizlenir (kural 1 gereği). Düzeltme yapılmadı.

**Okuyucu notu teşhisi (Mac, 2026-11-26).** Dört sayfa (6026412 s.15, 6026422 s.13, 6026411 s.16, 6026400 s.16) sayfa okuyucusuyla yeniden okundu (6–17 sn/sayfa, uygulama verisine yazılmadı). Sayfa görüntüsünde dördünde de not tablonun alt satırında, sağda ("Grade Rule Display: Increment"). Okuyucu çıktısında not hiçbirinde tam yok: 6026411'de alt satır hiç okunmadı; 6026412'de yalnız "Displaying 1 - 18 of 21 results" dipnotu; 6026400'de alt satırın yalnız ilk hücresi; 6026422'de satır "Grade Rule" sözcüğünde kesiliyor, "Increment" yok. Okuyucu notu vermediği için okuma anında `table_note`'a yazılamaz; sorgu anı kodu kalır, bu dört tablo bilinen sınır olarak kalır.

<a id="karar-0030"></a>

### 0030: Okuyucunun LaTeX kesri düzeltildi; ikinci okumada kesir düzeyi karşılaştırma reddedildi (ölçüm)
Tarih: 2026-11-26. Ürün sahibi onayı (LaTeX dönüştürücü; kesir düzeyi karşılaştırma ölçüt tutarsa). Dal: `okuyucu-dondurma`.

**LaTeX kesri.** Okuyucu bazı kesirleri çift parantezli argümanla ("1\frac{{1}}{{8}}", 6026417 s.13) ya da kesri saran grup parantezle ("$ -{1\frac{1}{4}} $", 6026411 s.16; parçalarda "-{3 1/8}", "-{1 1/4}" diye kalıyordu) yazıyordu; dönüştürücü bunları kesre çevirmiyordu. Kural (`page_reader.canonical`): `\frac` argümanları tek ya da çift parantezli olabilir; yalnız bir kesri saran grup parantezi atılır. Kesir olmayan parantezli yazım (set A'daki `-^{1}/_{4}` gibi) değişmez. Uygulama kopyası ölçülmüş kopyadan (`evals/ocr_truth.py`) bu iki yazımda geniştir; set A okumalarında ikisi de geçmez (çift parantez 0 blok), eşdeğerlik testi değişmedi. Değer gösterilmek için iki okumanın uyuşması şartı değişmedi. Kural sürümü PDF ve Office 26, görsel 17 (okuyucudan geçen bütün sayfa türleri).

**Kesir düzeyi karşılaştırma: teşhis.** 6026417 s.11'in tablosu okuyucuyla ve Tesseract'la yeniden okundu. Tesseract üst üste yazılmış kesirleri okuyamıyor: "12 1/4" yerine "12%", "1/4" yerine "Va", "Ta", "Vy"; kodda 0'ı O okuyor ("RSOO5"). Karşılaştırma blok düzeyinde ve sayarak olduğu için tablonun tamamında 276 parçanın 34 türü (RS005, 11, 12, 13, 14 ve bütün kesirler dahil) belirsiz; RS005 satırı bunun bir örneği.

**Tasarım (tek genel değişiklik).** Karışık sayının ("12 1/4") tam kısmı ikinci okumada da aynı sayıda geçiyorsa (yanına bozuk kesir yapışmış olsa da: "12%") tam kısım onaylanır, kesir okuyucudan alınır; tek başına kesir ve öteki parçalar eskisi gibi.

**Ölçüm (çevrimdışı, set A; okuyucu çalıştırılmadı).** Saklı okuyucu çıktısı (`evals/results/2026-11-16-set-a-benzetim/paddle`) ile benzetim aynı tohumla (20261116) yeniden üretildi, Tesseract yeniden çalıştırıldı (57 sn). Dondurulmuş kuralın işaretleri 42 sayfanın 42'sinde saklı kayıtla aynı; sayılar 0010 ile aynı. Ölçüt ölçümden önce yazıldı: yanlış gösterilen bir tane bile artmaz ve doğru olup gizlenen azalır.

| | Doğru gösterilen | Yanlış gösterilen | Gizli (doğruydu) | Gizli (yanlıştı) |
|---|---|---|---|---|
| Önce (dondurulmuş kural) | 1.325 | 87 | 1.335 | 325 |
| Kesir düzeyi | 1.361 | 91 | 1.299 | 321 |

**Sonuç: reddedildi.** Doğru olup gizlenen 36 azaldı, ama yanlış gösterilen 4 arttı. Dördü de yorum satırında, okuyucunun kesrini yanlış okuduğu ve tam kısmı onaylanan değer ("23½", "18½", "16½", "10¼"; syn1 s.3, syn4 s.2). Kesir okuyucudan alınınca okuyucunun kesir hatası ikinci okumadan kaçar. Değişiklik dala konmadı. S3'teki RS005 satırı bu yüzden gizli kalır (kural 1).

**Yeniden düşünülür.** Kesirleri okuyabilen ikinci bir okuma (ör. hücre düzeyinde ayrı okuma) ya da görüntüde kesrin yerini doğrulayan bir denetim gelirse; ölçüm yine set A ya da gerçek taramalarla.

**Yeniden işleme (Mac, 2026-11-26, onaylı tek yeniden işleme).** Yedek `../data-yedek-20261126`. "Eski kural" 28 belge (18 taranmış PDF, 251 sayfa; 9 metinli PDF ve Office; 1 fotoğraf) 42 dakikada yeniden işlendi (MLX okuyucu, bulut 0). Sonuç: 394 belge, 6.295 parça, "Eski kural" 0, "işlenemedi" 0. Taranmış belgelerin 2.580 parçası parça parça eşleşti: yeniden okuma hiçbir değeri değiştirmedi (değer dizisi farkları yalnız LaTeX dönüşümü ve boşluk). Belirsiz işaret: 18 kalktı, 820 eklendi (gizleme yönünde; eski kesik LaTeX parçalarının yerine artık tam kesirler sayılıyor ve uyuşmuyor). **Kural 1 denetimi:** işareti kalkan 18 değerden rastgele 10'u sayfa görüntüsünde satırıyla karşılaştırıldı, 10/10 birebir (AB035 SM 6, SL155 SM 6, ZP065/PO345/PO355 LG 7, BL015 SM 30, BL005 XL 30, SL090 MD 9; ikisi ölçü değil: "Displaying 14 - 26" ve "Bicep 1\""). **Yan bulgu:** okuyucu "-⅜" toleransını "-3\\frac{1}{8}" yazıyor (6013448 s.24); dönüşümle "-3 1/8" oluyor. Yüklü veride karışık sayılı 407 tolerans değerinin 407'si iki okumada uyuşmadığı için gizli; yanlış değer gösterilmiyor.

**S3 (aynı veriyle 5 canlı koşu, 0,0015 $).** 0/5 doğru, doğrulanmış yanlış 0. Dört koşuda sorgu çevirisi düştü (yardımcı model süre sınırı), RS005 ilk 8'de yok, "bulunamadı"; bir koşuda RS005 1. sırada, model "12 1/4"ü doğru alıntıyla verdi, cümle "OCR değeri belirsiz" diye gizlendi. Neden konum değil; konum düzeltmesi yazılmadı.

**Taban setleri (çevrimdışı, 0 $).** Taban 7 ve 11'in okuyucudan geçen belgeleri yeni kodla yeniden işlendi: metin ve belirsiz işaretler aynı (yalnız kutu koordinatlarında yuvarlama). Taban 7 ve 11'de 40 sorunun 0'ı, FastReact'ta 18 sorunun 0'ı değişti (`evals/output/dondurma-2026-11-26`).

<a id="karar-0031"></a>

### 0031: Dondurma (2026-11-26)
Tarih: 2026-11-26. Ürün sahibi kararı. Dal: `dondurma-kaydi` (yalnız belge).

**Ne donduruldu.** Kod `main` `8b75044` (`8b750449e5ba920e6ce16a2a25aec3fc22be8275`). Bu kayıttan sonra gerçek belgeler gelene kadar `docs/` dışında dosya değişmez (`src/`, `apps/`, `tests/`, `evals/`, `pyproject.toml`, `uv.lock`, `ornek-belgeler/`, `.github/`); hata bulunursa düzeltilmez, kanıtıyla `acik-notlar.md`'ye yazılır. Kural sürümleri (`PAKET.txt`): pdf 26, office 26, image 17, spreadsheet 6, legacy_spreadsheet 6, sql 3, text 2, markdown 3. Uygulama verisi: 394 belge, 6.295 parça, "Eski kural" 0, "işlenemedi" 0. Veri paketi `va-veri-20261126.zip` (Mac'te, repo dışı), sha256 `acik-notlar.md`'de ("Windows'a veri gönderme").

**Güvenli bilinen sınırlar (yanlış değer gösterilmiyor).**
- **S1:** belge düğmesiyle seçilen 6026412'de beden aralığı "bulunamadı" dönüyor; şablon aralığı gösterilmiyor ("Belge düğmesiyle seçilen belgede her sayfada geçen öbek sıralama sorgusundan çıkar").
- **S2:** model renk hücresini alıntılamadığı için kumaş cümlesi Kural D ile gizleniyor (0019, "Kural D" ve "S2: istem denemesi").
- **S3:** "ön ağ" satırı ya kaynaklara girmiyor (sorgu çevirisi süre sınırı) ya da değeri iki okumada uyuşmadığı için gizleniyor ([0029](#karar-0029), [0030](#karar-0030)).

**İstem turu.** #171 (`istem-turu`) birleştirilmeden kapatıldı: istem turunun ölçütü tutmadı; istem değişmeden donduruldu ("Bu repodaki istem değişiklikleri").

**Elle kapanış testi ön koşusu (Mac, 2026-11-26, canlı, arayüz yolu `/api/ask`, 0,0035 $ günlükteki `cost_usd` toplamı). Günlük numaraları Mac günlüğünün; paketten sonra yazıldıkları için pakette ve Windows'ta yok.** `VA_PAGE_READER` `.env`'den okundu, uygulama 8080'de. Her soru bir kez. 1, 6 ve 7'de beklenen değer sayfa görüntüsüyle karşılaştırıldı, üçü de aynı (6026412 s.1 "XS-XXL(4)"; 6026418 s.11 MD 14 3/4, s.13 fark 1/2; 6026411 s.15 MD 4 3/4, s.16 fark 1/4). Doğrulanmış yanlış değer 0. Sorgu çevirisi bu koşularda düşmedi.

| # | Beklenen | Bugün (bu koşu) | Sonuç | Günlük |
|---|---|---|---|---|
| 1 | Netleştirme; 6026412'de "XS-XXL(4)", s.1 | Netleştirme (6026400 / 6026412 / 6028355); 6026412 seçilince "bulunamadı" | Bilinen sınır gibi; seçeneklerde 6028355 de var | #2177, #2178 |
| 2 | KNT-226131, s.9 | Cümle gizli (Kural D); modelin değeri KNT-226131 | Bilinen sınır gibi | #2179 |
| 3 | 12 1/4, s.11 | Cümle gizli (OCR belirsiz); modelin değeri 12 1/4 | Bilinen sınır gibi | #2180 |
| 4 | "XS-4XL, SMT-4XLT", s.1 | Cümle gizli (Kural E); model "XS-5XL" (s.24) dedi, gösterilmedi | Bilinen sınır gibi | #2181 |
| 5 | "Fit Approved, Hold Sampling", s.1 | "Numune durumu Fit Approved, Hold Sampling şeklindedir.", "Taramadan okundu" | Beklendiği gibi | #2182 |
| 6 | 14 3/4, s.11 | Cümle gizli (OCR belirsiz); modelin değeri 14 3/4 | Bilinen sınır gibi | #2183 |
| 7 | 4 3/4, s.15 | İki cümle gizli (OCR belirsiz, alıntı hücre başında değil): 4 3/4 (s.15) ve fark değeri 1/4 (s.16) | Bilinen sınır gibi; fark değeri gösterilmedi | #2184 |
| 8 | 19, `sql-ekran` s.1 | "19", "Taramadan okundu" | Beklendiği gibi | #2185 |
| 9 | "XS-4XL, SMT-4XLT", İngilizce | Cümle gizli (Kural E); modelin ham cevabı İngilizce "XS-5XL" | Farklı (güvenli): gizli, dil yalnız ham çıktıda görülüyor | #2186 |
| 10 | "Add week number to date"; General part 3 ve part 1 | Seçenek cümlesi doğrulanmış (part 3, Reporting options); menü yolu cümleleri gizli (alıntı kaynakta birebir değil) | Bilinen sınır gibi | #2187 |
| 11 | "Bu belge zaten var" sorusu | Koşulmadı | Windows'ta denenecek | — |

**Açık riskler.** Sorgu çevirisinin 1,5 sn süre sınırı (S3'te 5 koşunun 4'ünde düştü); ikinci okumanın kesirleri onaylamayıp gizlemesi (0030); okuyucunun notunu okumadığı 4 fark tablosu (0029; 53 satırda fark değeri ölçü diye gösterilebilir); sentetik sette yanlış gösterilen oranı (set B %2,9; [0026](#karar-0026), [0027](#karar-0027)).

**Yeniden düşünülür.** Gerçek belgeler geldiğinde; dondurma ürün sahibinin kararıyla kalkar.

<a id="karar-0032"></a>

### 0032: Dondurma istisnası: beden aralığı (D6); sıralama düzeltmesi denendi, ölçüt tutmadı
Tarih: 2026-11-26. Ürün sahibi onayı (dondurmanın tek istisnası, tek deneme). Dal: `beden-araligi-d6` (birleştirilmedi, yalnız kayıt için `origin`'de). `main` ve kod dondurması (0031) değişmedi.

**Sorun.** "6013448'in beden aralığı nedir?" sorusunun doğru cevabı ("XS-4XL, SMT-4XLT", s.1, "Size Range" satırı) gösterilmiyor.

**Teşhis (Mac, #2181 ve #2186).**
- Doğru satır ilk 8'de, iki soruda da 3. sırada. 1. sırada s.24'teki şablon satırı var: "Measurement Chart | 6013448-FW27-MMC-US | Chart Size Range | Apparel (XS-5XL) | Fit Type Regular". İki satır modele aynı belge adıyla gidiyor; s.1 satırının bölümü "FW · Properties", s.24'ünki "FW · BOM"; kaynakta sayfa yok. s.1 satırında ürün numarası geçmiyor, şablon satırında "6013448-FW27-MMC-US" geçiyor.
- Model şablon satırını alıntılayıp "6013448-FW27-MMC-US için beden aralığı XS-5XL'dir." dedi; Kural E gizledi. Model doğru değeri hiç söylemedi; doğru cevabı gizleyen kural yok ("Actual Sizes" izleme maddesi tetiklenmedi).
- Sabit bağlam (aynı 8 kaynak; cevap ve doğrulama adımları doğrudan çağrıldı, soru günlüğüne yazılmadı, çıktılar repoda değil), Türkçe ve İngilizce 5'er koşu: doğru 0/10. Altı koşuda XS-5XL söylendi ve Kural E ile gizlendi; dört koşuda 1, 3 ve 7. kaynaklar arasında netleştirme soruldu. 1. ve 3. kaynak yer değiştirince Türkçe 5/5 doğru ve doğrulanmış.
- Arama (çevrimdışı, 0 $): soru numarası "6013448" iki kolda şablon satırını 1. sıraya çekiyor (yoğun 1, BM25 1). Doğru satır yoğun kolun ilk 30'unda yok, BM25'te 2. Numara sorgudan çıkınca BM25'te doğru satır 1., şablon 2.; birleşik sırada 2. ve 4. (İngilizce soru)
- **Kök neden:** soruda belgeyi seçen model numarası sıralama sorgusunda kalıyor ve onu metninde taşıyan şablon satırını ürünün kendi satırının önüne geçiriyor.

**Değişiklik (dalda).** Soruda adı geçen kapsam belgelerinin başlık kodu ve sayısal model numarası (`mentioned_in` ile aynı tanım) yoğun ve BM25 sıralama sorgularından çıkar (`DocumentCatalog.without_names`, `retrieve`). Kesmeli ekiyle çıkar ("6013448'in"); sorgu boş kalırsa olduğu gibi kalır. Modele giden soru ve kayıttaki çeviri değişmez. S1 öbek kuralıyla (#165) aynı ilke: kapsamı belirleyen ad belge içinde ayırt edici değil. Kural sürümü değişmez, yeniden işleme yok. Kod +20/−4 satır (`steps.py`, `memory.py`); 2 yeni test (biri 4 durumlu), 2 test yeni kurala göre değişti.

**Ölçüm (Mac, canlı, her koşu bir kez).** Ölçüt ölçümden önce sabit: Türkçe ve İngilizce 5'er koşuda doğru aralık doğrulanmış en az 4/5, "XS-5XL" doğrulanmış 0/5, İngilizce soruda cevap İngilizce; S1 3 koşuda yanlış değer 0; taban 7, 11 ve FastReact'ta kötüleşen soru ve doğrulanmış yanlış 0; sınır setinde doğrulanmış yanlış 0. "Önce" sütunu D6 için sabit bağlam (canlı "önce": #2181 ve #2186, birer koşu, ikisinde de XS-5XL gizli).

| Soru | Koşu | Önce | Sonra | Doğrulanmış yanlış |
|---|---|---|---|---|
| Türkçe D6 | 5 | sabit bağlam: doğru 0/5 (3 gizli XS-5XL, 2 netleştirme) | doğru 0/5; 5/5 seçeneksiz netleştirme (#2188–2192) | 0 |
| İngilizce D6 | 5 | sabit bağlam: doğru 0/5 (3 gizli XS-5XL, 2 netleştirme) | doğru 5/5 doğrulanmış ("Taramadan okundu"), İngilizce; ayrıca "The apparel chart size range is XS-5XL." 5/5 doğrulanmış (#2193–2197) | 0 (aşağıda) |
| S1 (6026412 seçili) | 3 | "bulunamadı" | 3/3 "bulunamadı" (#2198–2200) | 0 |
| Taban 7 | 1 | 33/33 (dondurma, önbellek; 7 sohbet sorusu önbellekte yoktu) | 40/40 (23 soru canlı) | 0 |
| Taban 11 | 1 | 33/33 (dondurma, önbellek; 7 sohbet sorusu önbellekte yoktu) | 40/40 (20 soru canlı) | 0 |
| FastReact | 1 | 18 soru | 18/18 aynı (kaynak değişmedi, önbellek) | 0 |
| Yüklü sınır seti | 1 | — | 32 soru: 26 cevap, 4 netleştirme, 2 "bulunamadı" | 0 |

Ölçüm klasörü `evals/output/d6-2026-11-26` (repoda değil). Maliyet: ölçüm 0,0197 $ (günlük #2188–2232 0,0109 $, taban 7 0,0049 $, taban 11 0,0039 $, FastReact önbellek), teşhisteki sabit bağlam koşuları ≈0,0036 $; toplam ≈0,023 $. Sınır setinde 4 soruda sorgu çevirisi düştü.

**Sonuç: ölçüt tutmadı, birleştirilmedi.** Sıralama düzeldi: Türkçede doğru satır 1. sırada. Ama model Türkçede 5/5 "Size Range" (1), "Chart Size Range" (2) ve "Actual Sizes" (7) arasında netleştirme sordu: düzeltmeden önceki netleştirmelerle aynı üç satır (önce sabit bağlamda 2/5). Adaylar tek belgede olduğu için seçeneksiz netleştirme göründü. Sıralama modelin kararsız kaldığı satırları değiştirmedi; "Style Actual Sizes" satırı da ilk 8'e girdi (seçeneklerde yok). İngilizcede doğru aralık 5/5 doğrulanmış gösterildi, ama şablon aralığı da 5/5 ikinci cümle olarak doğrulanmış gösterildi; 4 koşuda model çelişki işaretledi, arayüz "Kaynaklar birbiriyle çelişiyor." uyarısı gösterir. Bu cümle şablonu adıyla anıyor ("chart"), söylediği doğru ve Kural E onu muaf tutuyor; yine de ölçüt "XS-5XL doğrulanmış 0/5" idi. Kalan katman model ve istem: kaynakta birden çok beden etiketi ("Size Range", "Chart Size Range", "Style Actual Sizes", "Actual Sizes") varken ürünün kendi etiketini seçmek. D6 güvenli bilinen sınır kalır (yanlış değer gösterilmiyor).

**Yan etki (dalda).** Başlığında kod ya da model numarası taşıyan belgeyi adıyla soran her soruda sıralama sorgusu değişir: yüklü 394 belgenin 17'si; taban setlerinde bütün `dikim-*` belgeleri (başlıkta ürün kodu). Ölçülen setlerde kötüleşen soru yok.

**Yeniden düşünülür.** Sıralama değişikliği bir istem ya da kaynak biçimi değişikliğiyle birlikte yeniden ölçülürse (ekip kararı, açık notlar).

<a id="karar-0033"></a>

### 0033: Dondurma kalktı; kod sadeleştirmesi (dosya birleştirme, istemci katmanı)
Tarih: 2026-11-27. Ürün sahibi kararı: dondurma (0031) "mevcut kod yapısını bozmayan" sadeleştirme için kalktı; yeniden indeksleme hariç. Dal: `sadelestirme`.

**Neden.** Paylaşım paketi hazırlanırken `src/visual_agent` 65 dosya bulundu. Salt okunur inceleme (2026-11-27): ölü kod yok (her üst düzey ad üretim kodunda kullanılıyor); tek yerden kullanılan küçük modüller ve aynı alanları kopyalayan bir istemci katmanı var.

**Ne değişti (davranış aynı; kural sürümü, istemler, parça ve indeks değişmedi).**
- Tek kullanıcılı modüller kullanıcısına taşındı: `retrieval/normalization` → `encoders`, `fusion` → `hybrid` (`ScoredChunk` → `qdrant_store`); `generation/parse` → `sources`; `conversation/grounding` → `verification/text` (paket kalktı); `domain/conversation` → `domain/result`; `ask/related` → `orchestrator`; `catalog/snapshot` → `identifiers`; `ingest/plain_text` → `markdown`; `ingest/docling_parser` → `tools`.
- Yardımcı model çağrıları tek dosyada: `generation/json_model`, `intent`, `translate`, `rewrite`, `topic` → `generation/helpers.py`. Aynı adlı sabitler önek aldı (`_PROMPT` → `_INTENT_PROMPT` vb.); istem metinleri ve sabitler eskileriyle birebir karşılaştırıldı, fark 0. `ask/intent.py` ile `generation/intent.py` ad karışıklığı kalktı.
- İstemci katmanı: `ModelClients`, `ask_deps()` ve `apps/api/services._ModelClients` yerine tek `build_ask_deps()`. `AskRuntime` kurulmuş `AskDeps`'i tutar, her soruda yalnız `catalog` ve `identifiers` alanlarını `dataclasses.replace` ile yeniler (önce de her soruda katalog yeniden okunuyordu). Açılıştaki ısınma katalogu okumaz, boş yer tutucu verir: zamanlama öncekiyle aynı (inceleme bulgusu; ilk hâli katalogu ısınmada okuyordu).
- Kapsam ölçümü: `encoders.py` dosya düzeyinde hariç tutulmaz; yalnız model yükleyen sınıflar (`# pragma: no cover`). İndeksi etkileyen `normalize_for_bm25` taşındığı yerde ölçümde kalır.
- `AskOutcome`'da `translation_failed` açıklaması yanlış alanın (`helper_providers`) altındaydı; düzeltildi.

**Sonuç.** `src/visual_agent` 65 → 51 dosya (15 silindi, 1 açıldı: `generation/helpers.py`). Satır (`809e3ce`'ye göre): `src` −35, `apps` +4, `evals` ve `pyproject.toml` +6, `tests` +33 (güçlendirilen bağlantı testi); toplam +8. Kazanç dosya sayısında ve kaldırılan iki türde (`ModelClients`, `_ModelClients`), satırda değil (taşıma). Test değişiklikleri import düzeltmesi; yalnız `test_ask_clients.py` yeni fonksiyona göre yeniden yazıldı. Bağlantı testi artık çeviri, takip tamamlama ve niyet çağrılarının yardımcı modele ve yardımcı sağlayıcısına gittiğini isteğin gövdesinden doğrular. Yardımcı model cevap modeline bağlanınca test kalıyor (bilerek bozularak denendi).

**Bilinen kalan.** `apps/web/src/limits.ts` yorumu `MAX_QUESTION_CHARS` için hâlâ eski yolu (`domain/conversation.py`) gösteriyor; doğrusu `domain/result.py`. Bu işin kapsamında arayüz dosyasına dokunulmadı; davranışı etkilemez (`tests/test_web_limits.py` yalnız sayıyı karşılaştırır).

**Yapılmayanlar.**
- **`AskOutcome`'un `AskState`'ten alanları elle kopyalaması kaldı.** Kopya açık ve tip denetimli; yansıma ile kopyalamak tip güvenliğini düşürür, teşhis alanlarını alt modele taşımak `AskOutcome`'un 19 kurulduğu yeri ve soru günlüğünü değiştirir. Kazanç yok.
- **BM25 metin biçimi (`normalize_for_bm25`) doğrulamadaki kurallarla (`canon_chars`, `turkish_lower`) ortaklaştırılmadı.** İki yerde aynı kurallar elle eşit tutuluyor; ortak yardımcı BM25 vektörlerini değiştirebileceği için yeniden indeksleme ister (ekip kararı). Değiştirilirse iki yer birlikte değişmeli.

**Bu bilgisayarda test notu.** Windows kopyasında `core.autocrlf=true` olduğu için dondurulmuş dosyaların sha256 testleri (`test_committed_set_a_files_are_the_frozen_ones`, `test_scoring_is_frozen`, `test_measurement_scripts_are_frozen`) `main`'de de kalıyor (CRLF); bu işle ilgisi yok, CI (Linux) etkilenmez.

<a id="karar-0034"></a>

### 0034: Okuma planı A-q1 seçildi; B ve C elendi (ölçüm)
Tarih: 2026-11-27. Ürün sahibi kararı. Ölçüm ve doğru cevaplar: `docs/okuma-planlari.md`, `evals/okuma_planlari_dogru_cevaplar.md` (ölçümden önce commit'lendi). Windows, bir koşu, 150 değer (Quality Manual 61, Bold 3 Stripes 40, föy 6013448 49; metinli, karışık ve metin katmanı olmayan sayfalar).

**Sorun.** Gelecek belgelerin bir kısmında yazı ve ölçüler vektör çizim ya da görsel içinde (seçilemeyen metin, karışık sayfa). Bugün PaddleOCR-VL'nin "görsel/grafik" diye boş bıraktığı bloklar hiç okunmuyor (ör. 6013448 s.14 dikiş talimatları, Bold s.21 bütün sayfa), Tesseract kontrolü kesirleri ve süslü başlıkları okuyamadığı için doğru değerleri gizliyor.

**Karar (A-q1).** PaddleOCR-VL ana okuyucu kalır. Paddle'ın okuduğu her yerin kontrolcüsü (gömülü görseller dahil) Qwen3-VL-30B olur (OpenRouter, ZDR, blok kırpıntısı). Paddle'ın boş bıraktığı görsel/grafik bloklarını Qwen okur, Gemma 4 26B kontrol eder; uyuşmayan değer gizlenir. Tesseract yalnız yedek: Qwen'e ulaşılamazsa kontrol bugünkü gibi Tesseract'la yapılır, okuma durmaz. Buluta yalnız kırpıntı gider, tam sayfa gitmez.

**Ölçüm (ölçüt ölçümden önce: yanlış gösterilen tabandan fazla olamaz; metinli sayfada tabanda doğru değer bozulamaz).**

| | Taban | A-b | B | A-q1 | A-q2 |
|---|---|---|---|---|---|
| Doğru gösterilen | 81 | 94 | 48 | 115 | 106 |
| Yanlış gösterilen | 3 | 3 | 0 | 3 | 3 |
| Gizlenen doğru | 27 | 38 | 79 | 17 | 26 |
| Okunamayan | 31 | 7 | 23 | 7 | 7 |
| Metinli sayfada bozulan | – | 0 | 24 | 0 | 0 |
| Şekil değerlerinde gösterilen (114) | %46 | %58 | %39 | %76 | %68 |
| Föy kesirleri (18), doğru gösterilen | 0 | 7 | – | 15 | 15 |

A-b: şekil bloğu Qwen + Tesseract, Paddle kontrolü Tesseract. A-q2: A-q1 ile aynı, şekil kontrolü Tesseract. Yanlış gösterilen 3 değerin üçü de bilinen QM s.16 etiket hatası (metinli sayfa; hiçbir plan dokunmuyor). Okuyucu bölgelerinde doğrulanan değer parçası Tesseract ile %59, Qwen ile %87. Bulut: iki tur 143 çağrı, 0,0612 $; A-q1 föy tablo sayfası başına ek ~40 sn ve ~0,002 $.

**Neden B elendi.** Her sayfayı VLM okuyunca metinli sayfalarda tabanda doğru 24 değer bozuldu (ölçüt 2 kaldı); 24 sayfanın 4'ünde çıktı döngüye girip token sınırına takıldı, 1'inde JSON bozuk; konum kutusu yok; tam sayfa buluta gidiyor.

**Neden C elendi.** Metin katmanı olan sayfayı da okuyucudan geçirmek: Windows'ta QM s.7 (düz metin) iki denemede de 5 dakikayı aştı, ölçülemedi. Ayrıca metin katmanının birebir doğru olduğu sayfalara OCR hatası sokma riski taşıyor; karışık sayfalardaki kazancını A zaten şekil okumasıyla sağlıyor.

**Bilinen sınırlar.** Paddle ve Qwen ikisi de görüntü-dil modeli: aynı hatayı birlikte yaparlarsa yakalanmaz (150 değerde görülmedi, örneklem küçük). Qwen şu an yalnız tek ZDR sağlayıcıda (DeepInfra). Puanlamanın ~60 değeri elle. Kontrol birimi bugünkü blok; föy tablosunda bütün tablo tek bölge.

**Yeniden düşünülür.** İkinci ölçüm setinde (ilk turda kullanılmayan sayfalar) ölçüt tutmazsa; Qwen ZDR erişimi kalkarsa; iki VLM'in birlikte yanlış okuduğu değer görülürse.

<a id="karar-0035"></a>

### 0035: A-q1 uygulandı: ikinci okuma Qwen3-VL (Tesseract yedek), şekil blokları Qwen3-VL + Gemma
Tarih: 2026-11-27. Dal: `okuma-a-q1`. Kararı uygular: 0034 (ürün sahibi, ölçüm `docs/okuma-planlari.md`).

**Ne değişti (`ingest/page_reader.py`, okuyucu yolu genişletildi; yeni yol ya da modül yok).**
- İkinci okuma: OpenRouter anahtarı varsa her blok kırpıntısını `VA_READER_MODEL` (varsayılan `qwen/qwen3-vl-30b-a3b-instruct`) okur; sayarak karşılaştırma kuralı (`count_mismatches`) aynı. Taranmış sayfa ve metinli sayfadaki gömülü görsel ikisi de. Qwen'den okuma alınamazsa (ağ, HTTP hatası, süre, ZDR sağlayıcısı yok) o blok bugünkü gibi Tesseract'la denetlenir, okuma durmaz (`CloudReaders`, `_checker`).
- Devre kesici (belge başına): bir modelin ilk hatasından (zaman aşımı, bağlantı, HTTP, ZDR dizini alınamadı) sonra belgenin kalanında o modele istek gitmez; denetim Tesseract'la sürer, şekil blokları atlanır. Belge raporuna tek satır uyarı yazılır ("N blok Tesseract'la denetlendi; bulut alınamadı (…)"), günlüğe belge kimliğiyle.
- Tam sayfa: şirket onayı (2026-11-27) ile taranmış belgelerde yazı bölgesi kırpıntıları ve gerektiğinde tam sayfa görüntüsü ZDR'li buluta gidebilir. Bu dalda bir ara eklenen %90 alan eşiği (`VA_READER_CLOUD_MAX_PAGE_SHARE`) bu onayla kaldırıldı: sayfayı kaplayan blok da öteki bloklar gibi okunur (metin bloğunu Qwen denetler, şekil bloğunu Qwen okur, Gemma denetler). Alan ölçümü (yeni çağrı yok, işlenmiş parçaların Paddle kutularından; 17 taranmış föy, 248 sayfa): belge başına ortalama sayfa alanının %45'i buluta gidiyor (belge başına en düşük %34, en yüksek %52); sayfa başına en yüksek %89. Paddle'ın boş bıraktığı görsel blokları kutu taşımadığı için hesapta yok; gerçek oran biraz daha yüksek olabilir.
- Düzen modeli metin katmanı olmayan (okuyucudan geçen) bir sayfada hiç blok bulamazsa sayfa tek şekil bloğu sayılır, aynı yoldan okunur (Qwen okur, Gemma denetler; ör. Bold s.14). Metinli sayfadaki gömülü görselde ve bulut yokken tetiklenmez.
- 429 (istek sınırı): bulut çağrısı Retry-After'a uyarak (başlık yoksa 2, 4, 8 sn; en çok 60 sn) en çok 3 kez yeniden denenir; devre ancak bunlar da tükenince açılır.
- Devresi açılan belgeler rapor uyarısından bulunur (sabit metin `CLOUD_OUTAGE_MARK`): `sqlite3 data/visual_agent.db "SELECT d.doc_id, d.filename, w.value FROM documents d, json_each(d.report, '\$.warnings') w WHERE w.value LIKE '%bulut alınamadı%'"`.
- Şekil okumasının JSON'u bozuk ya da yarımsa (token sınırı) önbelleğe yazılmaz, bir kez yeniden istenir; yine bozuksa blok atlanır. Boş cevap önbelleğe yazılmaz; bozuk önbellek dosyası yok sayılıp yeniden istenir.
- `VA_READER_FIGURE_CHECK_MODEL` `VA_READER_MODEL` ile aynıysa uygulama açılmaz. Yalnız boşluk bırakılmış anahtar yok sayılır.
- Şekil blokları: okuyucunun içeriğini boş bıraktığı `image`, `chart`, `figure`, `seal`, `header_image`, `footer_image` blokları bugünkü blok kırpıntısıyla (okuyucuya verilen görüntü, 4 piksel kenar) Qwen'e gider (ölçülen JSON istemi). Değer taşıyorsa aynı kırpıntıyı `VA_READER_FIGURE_CHECK_MODEL` (varsayılan `google/gemma-4-26b-a4b-it`) okur; değer sayısı tutmayan parça belirsizdir (gizlenir). Gemma okuması alınamazsa bloğun bütün değerleri belirsiz; Qwen okuması alınamazsa blok bugünkü gibi atlanır. Satırlar metin, tablolar okuyucunun tablo biçiminde (HTML) aynı öğe kuralından geçer; kutu sayfadaki blok kutusu, `from_ocr`.
- İstemler ölçülen istemlerin aynısı (`CHECK_PROMPT`, `FIGURE_PROMPT`). İstek `JsonModel.read_image` ile (çok kipli mesaj; ZDR kısıtı ve sağlayıcı seçimi `JsonModel`/`select_providers`'tan).
- Önbellek: bulut cevabı `VA_READER_CACHE_DIRECTORY` (varsayılan `data/okuma-onbellegi`) altında `sha256(model + istem + PNG)` adıyla; yeniden işleme aynı kırpıntı için ikinci kez ödemez.
- Anahtar yoksa okuma 26. kuralla aynıdır: ikinci okuma Tesseract, şekil blokları atlanır.
- Kural sürümü: PDF ve Office 26 → 27, görsel 17 → 18. Okuyucudan geçen sayfası olan (metin katmanı olmayan, zayıf, taranmış ya da metinli; metinli sayfa gömülü görsel yüzünden) bütün PDF ve Office belgeleri ile bütün görsel belgeler "Eski kural" görünür. Yeniden işleme yapılmadı. Sonradan eklenen tam sayfa okuması, eşiğin kaldırılması ve blok bulunamayan sayfa kuralı da yalnız okuyucu yolunu değiştirir; 27/18 içinde kalır, ikinci artış yok (dal `main`'e birleşmeden tek sürüm).

**Parçalama (aynı dal, aynı kural sürümü 27).** Bu iki değişiklik okuyucudan geçmeyen metinli PDF ve Office belgelerinin parçalarını da değiştirir (bölüm adı); sürüm 27 bunları da kapsar ("text" sayfa türü 26→27 adımında zaten var), ek artış yapılmadı.
- **Tablo satırının bölümü konumdan (QM s.16).** Satırın bölümü, aynı sayfada satırın üstünde başlayan ve yatayda satırla örtüşen en yakın başlığın yoludur; örtüşen başlık yoksa sayfanın başlıkları devralınmaz, yol sayfadaki ilk başlıktan öncekidir. Kutusuz öğeler (Markdown, Excel) okuma sırasındaki son başlığı alır. Docling'in düşürdüğü başlıklar (PTH, Customer Complaint) için metin katmanı adaylığı yapılmadı (açık notlar). Etki (6 metinli belgede docling yeniden çalıştırıldı, uygulama verisine yazılmadı; kayıtlı parçalarda başlık kutusu yok): yalnız QM s.16'da 13 satır; PTH satırları "OQL/SQL" → "4.3.2 QA Scorecard" (ör. "%: 90-94.99 | Score: 4"), Customer Complaint satırları "OQL/SQL" → "QUALITY MANUAL" (ör. "# of complaint: 0-2 | Score: 5"); OQL/SQL, Customer Satisfaction ve Lab Accreditation satırları kendi başlıklarında kaldı. Öteki 5 belgede (dikim-pdf, dikim-rev-a, ik-izin, dikim-word, sql-ekran) değişen satır 0.
- **Düzeyi bilinmeyen başlıklar kardeştir.** Docling ve sayfa okuyucusunun başlıkları birbirinin altına girmez; alt bölüm yalnız düzey kanıtıyla (Markdown, Excel). Kod taşıyan ilk başlık (0025) kök kalır ("SS28-6026412-US-… · BOM" aynen). Etki (kayıtlı parçalardan, yeniden işlemesiz): 7 belgede 374 parça; 6013448 föyü 318/319 ("FW · POMs" → "POMs", "FW · BOM" → "BOM"), Bold 3 Stripes 44/46 ("BOLD 3 STRIPES GLOBAL QUALITY STANDARD · Notes" → "Notes"), sql-ekran 3, ik-izin 3, sql-kilavuz 3, sql-notlar 2, ik-ihbar 1 (kök belge başlığı düşer: "Yıllık İzin Politikası · …" → "…"). Belge başlığının bölüm yolundan düşmesi aramada kayıp değildir: `Chunk.embed_text` (`domain/document.py`) belge başlığını her parçanın metnine zaten ekler. Docling'le yeniden çalıştırılan QM'de (kayıtlıda zaten kardeş) 152 parça "QUALITY MANUAL · X" → "X".
- **Devam eden tablo satırları (6029322 s.9; bilgi).** Karar 0025'ten beri sütun başlıkları satırda; kanıt parça #77: "BG-CV0007/Poly Bag … | 100: White / / Venom Red: Clear 960 | 001: Black / / Blue Haze: Clear 960". Canlı tek soru (2026-11-27, günlük #2283, `main` kodu, 0,0007 $) "Poly bag'in (BG-CV0007) rengi ne?" → netleştirme (6029278 / 6029322; ikisinde de bütün renklerde Clear 960). Bilinen küçük kusur: adaylar aynı değeri verdiği hâlde netleştirme soruldu; muhtemel neden iki parçada da belirsiz işaretli "Inc./TR0001/Approved/ea" (aynı cevap denetimi belirsiz kaynağa güvenmiyor); güvenli yönde. Ayrıca s.8 "White // Venom Red", s.9 "White / / Venom Red" yazım farkı.

**Bilinen sınırlar.**
- İki kez kesilen ya da JSON olmayan şekil okuması bloğu atlatır (ölçüm betiğindeki yarım JSON kurtarması alınmadı). Gemma'nın JSON'u okunamazsa ham metni karşılaştırılır.
- Devre kesici açılana kadar ilk istek süre sınırını (120 sn) bekleyebilir; sonraki bloklar beklemez.
- Sağlayıcı seçimi: bulut okuması modelin bütün ZDR sağlayıcılarını kullanır (`select_providers(model, ())`); `VA_HELPER_PROVIDERS` gibi bir sağlayıcı listesi ayarı yok.
- Anahtar varken işleme ağa bağlıdır: aynı belge Qwen'e ulaşılıp ulaşılamamasına göre farklı işaretlerle indekslenir (devre kesici açılırsa Tesseract). Değerlendirme indeksi (`evals/index_cache.py`) de bu yüzden anahtar varken ağa göre belirlenimci değildir; önbellekteki kırpıntılar aynı kalır.
- Sayarak karşılaştırma (şekil ve okuyucu tablolarında) değerin hangi başlığa bağlandığını denetlemez: iki okuma aynı sayıları okuyup değeri başka sütun başlığına bağlarsa değer yanlış başlıkla doğrulanmış görünebilir.
- Kaldırılan %90 eşiğinin (yukarıda) ölçülen etkisi, kayıt için: İlk ölçüm setinde (prototip çıktılarından, çağrısız): 44 Paddle bölgesinden 1'i (B3S s.6, %93) ve 38 şekil kırpıntısından 1'i (B3S s.21 bütün sayfa, %93,5) eşiği aşıyor. A-q1'e göre değişen değer 5: B-6-5 doğru gösterilen → gizlenen doğru (Tesseract denetimi); B-21-1…4 (A-q1'de 1 doğru gösterilen, 3 gizlenen) → okunamayan. A-q1 özeti 115/3/17/7 → 113/3/15/11 (doğru gösterilen / yanlış gösterilen / gizlenen doğru / okunamayan); yanlış gösterilen değişmez.
- Kural sürümü (27/18) belgenin gerçekten bulutla okunup okunmadığından bağımsız damgalanır: anahtarsız ya da devre kesici açıkken işlenen belge de 27 kaydedilir ve "Eski kural" görünmez; bulutla okunması için elle yeniden işlenmesi gerekir.
