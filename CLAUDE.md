# Visual Agent v2: çalışma kuralları

Önceden yüklenmiş belgelere yazarak ya da konuşarak soru sorulan, her cevabı kaynağıyla
gösteren web aracı. Başlamadan önce: README.md, docs/acik-notlar.md, docs/decisions/.

## Değişmeyen ilkeler
- Yanlış değer asla doğrulanmış gösterilmez. "Bulunamadı" ya da netleştirme sorusu,
  yanlış cevaptan iyidir. Haksız ret kabul edilebilir; haksız kabul edilemez.
- Belgeye ya da alana özel elle yazılmış kural yok. Her kural görülmemiş belgede de
  çalışmalı. Kural format düzeyinde olabilir (PDF, Word, markdown), belge düzeyinde
  olamaz. Belgeler ham ya da hazır markdown olarak gelebilir; ikisi de desteklenir.
  Test belgeleri üretimde kullanılmaz.
- Buluta yalnız soru ve parçalar gider, yalnız ZDR sağlayıcılara. Ses saklanmaz.
- Mevcut düzen korunur: katman sınırları (tests/test_architecture.py), mypy strict,
  ruff (karmaşıklık 10), kapsam eşiği, Türkçe docstring ve mesajlar.
- docs/acik-notlar.md: biten madde silinir, ertelenen madde eklenir. Ölçülmemiş bir
  çıkarım sonuç gibi yazılmaz.

## Çalışma biçimi
- Adımlar sırayla, her adım ayrı commit. Her adımdan sonra: `uv run pytest`,
  `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`,
  `apps/web` içinde `npm test` ve `npm run build`; sonra kısa rapor.
- Görevde yazmayan iş yapılmaz. Yolda fark edilen diğer sorunlar düzeltilmez,
  docs/acik-notlar.md'ye yazılır.
- Yeni kod yazmadan önce aynı işi yapan kod aranır ve o kullanılır. Yeni bağımlılık için
  önce sorulur.
- Bir varsayım doğrulanamıyorsa ya da iş tarif edilenden büyük bir tasarım değişikliği
  gerektiriyorsa uygulamadan önce sor.
- Gizli dosyalar (.env, anahtarlar): değer yazdırılmaz, loglanmaz; değişiklik yapmadan
  önce sorulur.
- Varsayılan dala doğrudan commit yok; dal açılır, PR ile birleşir.

## PR kuralları
- Bugbot'un çözülmemiş bulgusu varken PR birleşmez. Bugbot hiç incelemediyse beklenir.
  Bulguyu kendisi çözülmüş işaretlediyse yeni inceleme kaydı beklenmez.
- Bugbot bir kez inceler. Gerçek hata ya da haksız kabul düzeltilir; diğer bulgular
  docs/acik-notlar.md'ye yazılır ve PR birleşir.
- Aynı PR'da ikinci düzeltme turu için önce sor.
- PR'ı kimin birleştireceği her PR için ayrıca söylenir; söylenmediyse birleştirme.

## Ölçüm
- Geçerli taban: evals/baselines/taban (bu bilgisayar). Doğrulanmış yanlış değer her
  ölçümde 0 olmalı; değilse dur ve bildir.
- Ölçüm, uygulamanın kendi kodunu kullanır; ölçüm için ayrı kopya mantık yazılmaz. Tek
  seferlik betikler evals/output altında kalır, repoya girmez, iş bitince silinir.
- Aynı API çağrısı iki kez yapılmaz: cevap önbelleği evals/output altında. Denetim ya da
  puanlama değişikliği `python -m evals.replay` ile önbellekten, maliyetsiz ölçülür.
- Yeni model isteği ya da belge vektörü gerekiyorsa önce sor. Cevaplar LLM ile puanlanmaz.
- Kararsız sorular (0004) gerileme sayılmadan önce ayrıca incelenir.
- Ölçüm indeksleri (evals/output/run*-taban, evals/output/fastreact/calisma)
  değiştirilmez; yalnız kopyaları kullanılır.

## Yerel kurulum (bu bilgisayar)
- Windows, yönetici yetkisi yok, Docker yok. Uygulama: `baslat.bat`
  (http://127.0.0.1:8080). Node, Tesseract ve LibreOffice %LOCALAPPDATA%\Programs altında.
- Uygulamanın verisi data/ altında (SQLite, gömülü Qdrant, belgeler). İçinden hiçbir şey
  silinmez; gerekirse önce sorulur.
- Gömülü Qdrant klasörü tek sürece kilitlenir: uygulama açıkken aynı klasörü açan ikinci
  süreç çalıştırılmaz.
- Dosyalar LF ve UTF-8 yazılır (baslat.bat CRLF). Python'da yazarken satır sonu açıkça
  belirtilir.
