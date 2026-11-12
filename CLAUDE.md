# CLAUDE.md — visual-agent-v2

Bu repo senin sorumluluğunda. Kodun düzeni, sadeliği ve doğruluğu senin mühendislik kararlarının sonucu; ona göre davran. Ama sorumluluk, aşağıdaki sınırların içinde geçerli: bazı kararlar ekipten onay ister (bkz. "Karar yetkisi").

Raporlarını ve açıklamalarını Türkçe yaz.

## Ürün

Fabrikadaki iç belgeler (kılavuzlar, sürüm notları, teknik föyler, Excel/Word dosyaları) üzerinde soru-cevap asistanı.

- Kullanıcılar sabit değil: hattaki işçi de olabilir, bir iç aracı soran SQL uzmanı da.
- Soru belge belirtmeden sorulabilir; sistem doğru belgeyi kendi bulur. Belirsizse (ör. iki benzer ürün modeli) hangisini kastettiğini sorar.
- Cevap gerçek zamanlı olmalı; cevabın kaynak sayfası/bölümü görünür olmalı.
- İleride: sesli soru-cevap, gerektiğinde görsel gösterme, departman bazlı yetki.

## Değişmez kurallar

1. **Yanlış değer asla verilmez.** Ölçü, ayar değeri, vida değeri gibi sayılar kaynakta doğrulanmadan kullanıcıya gösterilmez. Emin olunamıyorsa cevap vermemek, yanlış vermekten iyidir.
2. **Alana bağımsız ve otomatik.** Şu anki test belgeleri üretimde kullanılmayacak. Gerçek belgeler elle düzeltilemez. Her kural, hiç görülmemiş belgelerde de kendiliğinden çalışmalı. Belgeye, soruya ya da belirli bir modele özel yama yazma.
3. **Karışık belge türleri.** Gerçek belgeler ham (PDF, taranmış PDF, Word, Excel) ya da hazır Markdown olarak gelebilir. Dönüştürmede içerik kaybı olmamalı.
4. **Bulut kullanımı.** Buluta yalnızca parçalar (chunk) gider, bütün belge gitmez. Yalnızca ZDR (Zero Data Retention) sağlayan sağlayıcılar kullanılır.
5. **Maliyet / kalite dengesi.** Ucuz ama zayıf model kabul edilmez; maliyet de uçmamalı. Model değişikliği ölçümle gerekçelendirilir.
6. **Uygulama boş açılmaz.** Repodaki örnek belgeler ve FastReact belgeleri uygulamada yüklü kalır.

## Harcama ve indeksleme

API limiti sınırlı. Gereksiz çağrı ve gereksiz indeksleme yapma.

- **Yeniden indeksleme yapma** — ekip açıkça istemedikçe. Ölçümler ve testler mevcut indeksle çalışır. Bir değişiklik yeniden indeksleme gerektiriyorsa, yapma; gerektiğini ve tahmini süresini/maliyetini rapora yaz.
- Aynı soru + aynı istem + aynı model için API'yi ikinci kez çağırma; önbelleği kullan.
- Bir ölçüm turu beklenenden pahalıya gidecekse dur ve sor.
- Her soruyu ölçümde bir kez çalıştır. Sonuç beklendiği gibi değilse istemi tekrar tekrar değiştirip yeniden ölçme; nedenini yaz ve geç.
- İndeks kopyaları, vektör önbellekleri ve büyük ölçüm çıktıları repoya girmez (`.gitignore`).

## Kod hijyeni

Repo sade kalmalı. Daha önce "overengineered" bulundu; bunu tekrarlama.

- Yeni kod yazmadan önce aynı işi yapan bir şey var mı bak. Varsa onu değiştir, yanına ikincisini yazma.
- Yeni dosya/modül açıyorsan gerekçesini rapora yaz.
- Tek seferlik betikler repoya girmez; scratchpad'de kalır.
- Kullanılmayan kodu bulursan sil. "İleride lazım olur" diye kod bırakma.
- Bir sorunu çözmek için katman ekleme; önce mevcut akışın içinde çözülüp çözülemeyeceğine bak.

## Karar yetkisi

**Kendin karar verebilirsin:**
- Kod düzeni, yeniden adlandırma, ölü kod temizliği
- Hata düzeltmeleri, test ekleme/düzeltme
- Arayüzde küçük düzeltmeler
- Mevcut mimari içinde kalan küçük iyileştirmeler

**Önce ekibe sor:**
- Yeniden indeksleme, parça boyutu / bölme mantığı değişikliği
- Yeni model, yeni bağımlılık, reranker gibi yeni bileşenler
- Cevap modelinin istemindeki (prompt) değişiklikler
- Para veya sunucu gerektiren her şey
- Değerlendirme setlerinin ve beklenen cevap dosyalarının (`evals/...beklenenler.json` vb.) içeriği — bunları düzeltme, sorunu bildir
- `docs/acik-notlar.md`'deki ertelenmiş işlerden birine başlamak

## Çalışma biçimi

- Her iş kendi dalında yapılır. Ana dala doğrudan yazma, birleştirme yapma.
- Aynı hatanın etrafında tur atma. Bir yaklaşım işe yaramazsa nedenini yaz, açık notlara ekle, sıradaki işe geç.
- Ertelenen fikirler ve öneriler `docs/acik-notlar.md`'ye yazılır; oradan kendiliğinden iş seçme.
- Her dal gönderilmeden önce şunlar geçmeli:
  - `ruff`, format, `mypy`, `pytest`
  - Web dosyası değiştiyse `npm test` ve `npm run build`
- Örnek belgeleri yükleme: `uv run python -m apps.sample_documents`
- Başlattığın uygulama ya da arka plan sürecini işin bitince kapat ve raporda söyle.

## Rapor biçimi

Her iş sonunda kısa ve dürüst bir rapor ver:

- Ne yapıldı, hangi dalda
- **Hedeflenen sorun gerçekten çözüldü mü** — çözülmediyse açıkça yaz
- Testler ve ölçümler (önce / sonra), doğrulanmış yanlış değer sayısı
- Maliyet ve süre değişimi
- Net satır değişimi (eklenen / silinen) ve açılan yeni dosyalar
- Ekibin karar vermesi veya bakması gerekenler
