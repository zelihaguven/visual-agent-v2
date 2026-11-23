# Visual Agent

Önceden yüklenmiş belgelere yazarak ya da konuşarak soru sorulan, her cevabı kaynağıyla gösteren web aracı.

Durum: belge yükleme, işleme, kaynaklı soru-cevap, sohbet bağlamı, ses ve web arayüzü çalışıyor (A0–A7). Giriş henüz yok.

Mikrofon tarayıcıda yalnız `localhost` ya da HTTPS üzerinden açılır. Ağdaki tabletlerden kullanmak için uygulama HTTPS arkasında yayınlanmalıdır. Ses yalnız bellekte işlenir, diske yazılmaz; konuşma modelleri `VA_STT_MODEL`, `VA_TTS_MODEL` ve `VA_TTS_VOICE` ile değiştirilir.

## Yerel kurulum

Tek bilgisayarda, yönetici yetkisi olmadan çalışır. Her şey tek süreçtedir: API, belge işçisi ve arayüz aynı adresten açılır; veriler `data/` klasöründe kalır (SQLite dosyası, gömülü Qdrant, yüklenen belgeler). GPU gerekmez. Neden böyle kurulduğu: [0003](docs/kararlar.md#karar-0003).

Gereken: Windows (ya da macOS/Linux), veri saklamayan uçlara erişimi olan bir OpenRouter anahtarı ve aşağıdaki araçlar. Hepsi kullanıcı klasörüne kurulur.

| Araç | Ne için | Kurulum (yönetici yetkisi gerekmez) |
| --- | --- | --- |
| [uv](https://docs.astral.sh/uv/) | Python ve paketler | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| Node.js 26 | Arayüzü derlemek | [nodejs.org](https://nodejs.org/en/download) "Windows Binary (.zip)" dosyasını `%LOCALAPPDATA%\Programs\nodejs` klasörüne açın |
| Tesseract 5 (Türkçe ve İngilizce dil verisiyle) | Taranmış sayfalar, fotoğraflar, belgelerdeki görseller | Ayrıntı: [Araçlar](#araçlar) |
| LibreOffice | Office dosyaları (.docx, .pptx, .doc, .xls ...) | Ayrıntı: [Araçlar](#araçlar) |

Tesseract ya da LibreOffice yoksa uygulama yine açılır: açılışta hangi belgelerin işlenemeyeceği yazılır, o belgeler listede kendi hata mesajıyla görünür. PDF, .xlsx, metin ve SQL dosyaları bunlarsız çalışır.

1. Ayar dosyasını oluşturun; `VA_OPENROUTER_API_KEY` satırının başındaki `#` işaretini kaldırıp anahtarı yazın. Bu dosya repoya girmez.

   ```powershell
   copy .env.example .env
   ```

2. `baslat.bat` dosyasına çift tıklayın. Paketleri kurar, arayüz eskiyse derler, eksik araçları bildirir ve tarayıcıda <http://127.0.0.1:8080> adresini açar. Kapatmak için pencerede Ctrl+C. macOS/Linux'ta: `uv sync --frozen --no-dev --extra retrieval --extra ingest && uv run --no-sync python -m apps.local`.

İlk açılış internetten modelleri indirir ve uzun sürer: arama modeli (bge-m3, ~2,3 GB) açılışta, belge işleme modelleri (Docling) ilk belgede. Modeller kullanıcının önbellek klasöründe kalır (BM25 modeli `data/models/fastembed`), sonraki açılışlar hızlıdır. İlk açılış ve ilk belge işlendikten sonra `.env`'e `VA_MODELS_OFFLINE=true` yazın: uygulama modelleri yalnız yerel önbellekten yükler, internetsiz açılır; model eksikse ne eksik olduğunu söyleyip durur. Soru sormak için önce soldan belge yükleyin; işlenip "Hazır" olunca sorulabilir.

Örnek belgeler (`ornek-belgeler/`: FastReact kılavuzu ve üretilmiş test belgeleri) yalnız deneme ve ölçüm içindir, üretimde kullanılmaz. Yeni bilgisayarda uygulama açıkken `uv run --no-sync python -m apps.sample_documents` ile yüklenir; yüklü olanlar atlanır, kökteki test soruları yüklenmez.

Gömülü Qdrant klasörü tek sürece kilitlenir: uygulama aynı anda bir kez açılabilir. Ölçüm komutları kendi klasörlerini kullanır, uygulama açıkken de çalışır.

### Araçlar

Uygulama araçları PATH'te ya da ayarla verilen yolda arar (`VA_TESSERACT_PATH`, `VA_SOFFICE_PATH`; `.env` içine tam `.exe` yolu). `baslat.bat` şu klasörleri kendisi PATH'e ekler: `%LOCALAPPDATA%\Programs\nodejs`, `%LOCALAPPDATA%\Programs\Tesseract-OCR`, `%LOCALAPPDATA%\Programs\LibreOffice\program`.

- **Tesseract:** [UB Mannheim kurulumu](https://github.com/UB-Mannheim/tesseract/wiki), "yalnız benim için" seçilerek `%LOCALAPPDATA%\Programs\Tesseract-OCR` klasörüne. Türkçe dil verisi kurulumda seçilir ya da `tur.traineddata` dosyası ([tessdata_fast](https://github.com/tesseract-ocr/tessdata_fast)) `tessdata` klasörüne kopyalanır. Kontrol: `tesseract --list-langs` içinde `tur` ve `eng`.
- **LibreOffice:** [libreoffice.org](https://www.libreoffice.org/download/download-libreoffice/) MSI dosyası kurulmadan açılır (yönetici istemez):

  ```powershell
  msiexec /a LibreOffice_x.y.z_Win_x86-64.msi /qb TARGETDIR="$env:LOCALAPPDATA\Programs\LibreOffice"
  ```

### Taranmış sayfaların okuyucusu

Metin katmanı olmayan sayfalar (tarama, fotoğraf) PaddleOCR-VL ile okunur, Tesseract ikinci kez okur; sayısı tutmayan değer cevapta gizlenir ([0011](docs/kararlar.md)). Okuyucu `.env` içindeki tek ayarla seçilir:

| `VA_PAGE_READER` | Nerede | Başlatma |
| --- | --- | --- |
| `local` | Windows, Linux; ekran kartı varsa onu, yoksa işlemciyi kullanır | Ayrı süreç yok; `baslat.bat` yeter. Model ilk taranmış sayfada iner. |
| `mlx-vlm-server@http://localhost:8111/` | Apple Silicon | Ayrı pencerede `uvx --from "mlx-vlm>=0.3.11" mlx_vlm.server --host 127.0.0.1 --port 8111`. Model (3,6 GB) ilk sayfada iner. |
| `llama-cpp-server@http://adres/` | İşlemcide ayrı sunucu | llama.cpp `llama-server`, PaddleOCR-VL-1.6 GGUF dosyalarıyla. Bu repoda denenmedi. |

Ayar boşsa ya da okuyucuya ulaşılamıyorsa taranmış sayfası olan belge indekslenmez, listede "Okuyucu bekleniyor" olarak kalır; okuyucu çalışınca belgede "Yeniden işle"ye basılır. Bu sayfalar başka yoldan okunmaz. Metin katmanı olan belgeler okuyucusuz işlenir. `local` kipi Windows'ta ve işlemcide denenmedi; hızı ölçülmedi.

### Güncelleme

```powershell
git pull
```

Sonra `baslat.bat`: yeni paketler kurulur, arayüz değiştiyse yeniden derlenir. Açık sayfaları yenileyin. Yarım kalan belge işleri uygulama açılınca kendiliğinden yeniden başlar.

### Ağdan erişim

Arayüz yalnız bu bilgisayardan (`127.0.0.1`) açılır. Tabletlerden kullanmadan önce [açık notlardaki](docs/acik-notlar.md) "Canlıya alırken" maddelerine bakın: giriş yokken ağdaki herkes belgeleri görebilir, yerel kurulumda güvenlik başlıkları ve hız sınırı yoktur, mikrofon da yalnız HTTPS üzerinden açılır.

## Geliştirme

Python:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

Web (`apps/web`). `npm run dev` API'yi `apps.local`'in açtığı adreste bekler; önce kök klasörde `uv run python -m apps.local --no-browser` çalıştırın (port `.env`'deki `WEB_PORT`, yoksa 8080):

```bash
npm ci
npm test
npm run build
npm run dev
```

Test belgelerini ve doğru cevapları üretmek için:

```bash
uv run python -m evals.generate --seed 7 --output evals/output/set7
```

Soru hattını uçtan uca ölçmek için (gömülü Qdrant, `--work` klasöründe):

```bash
uv run python -m evals.run_questions --set evals/output/set7 --work evals/output/run7
```

Ölçüm koşucuları `--work` altındaki parça önbelleğini kullanır, belgeyi yeniden işlemez (`evals/index_cache.py`); belge işleme kodu değiştiğinde ölçüm, çalışma klasörünün bir kopyasında yapılır (`chunks.json` ve `ingest.json` silinerek; ya da elle, yalnız kural sürümü eskiyen belgelerin parçaları yeniden üretilip `chunks.json`'a yazılarak).

Model cevapları `evals/output/answer-cache` altında saklanır; aynı istek yeniden gönderilmez. Önbellekten gelen soruların süresi ve maliyeti rapora girmez, sayıları yazılır. Yeniden sormak için `--refresh-cache`. Uygulama bu önbelleği kullanmaz.

Diğer ölçüm araçları:

| Komut | Ne yapar |
| --- | --- |
| `evals.generate --kind sinir --seed 7 --output evals/output/sinir7` | Sınır setini üretir (yanlış sütun, olumsuzlama, model başına sayfa) |
| `evals.run_questions … --offline` | Ağa gitmeden yalnız önbellekten ölçer; önbellekte olmayan sorular "miss" olarak listelenir |
| `evals.run_questions … --questions a,b` | Yalnız bu soruları sorar (takip sorularının önceki turları dahil) |
| `evals.run_questions … --repeat 10` | Aynı soruları önbelleksiz tekrar sorar (kararlılık ölçümü) |
| `evals.run_questions … --retrieval-only` | Yalnız aramayı ölçer, modele gitmez |
| `evals.run_documents --documents ornek-belgeler/FastReact_Knowledge --questions … --work … --output …` | Bir belge klasörünü (FastReact) kendi soru listesiyle ölçer; `--offline` aynı anlamda |

Hepsi `uv run python -m` ile çalışır.

## Yapı

| Yol | Görev |
| --- | --- |
| `apps/api` | HTTP API; yerelde arayüzü de sunar |
| `apps/worker` | Belge işleme işçisi; yerelde API sürecinde, sunucuda ayrı süreç |
| `apps/local.py`, `baslat.bat` | Yerel başlatma |
| `apps/web` | Web arayüzü |
| `src/visual_agent` | Çekirdek paket; katman sınırları testle korunur |
| `evals` | Test belgesi üretimi ve ölçüm |
| `docs/kararlar.md` | Alınan kararlar |
| `docs/acik-notlar.md` | Sonraya bırakılan konular |
| `docs/sesli-altin-soru-seti.md` | Sesli modu elle denemek için soru seti ve duyurular |

Ayarlar `VA_` önekli ortam değişkenlerinden ya da `.env` dosyasından okunur: [`settings.py`](src/visual_agent/settings.py).
