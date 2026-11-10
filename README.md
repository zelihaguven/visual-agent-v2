# Visual Agent

Önceden yüklenmiş belgelere yazarak ya da konuşarak soru sorulan, her cevabı kaynağıyla gösteren web aracı.

Durum: belge yükleme, işleme, kaynaklı soru-cevap, sohbet bağlamı, ses ve web arayüzü çalışıyor (A0–A7). Giriş henüz yok.

Mikrofon tarayıcıda yalnız `localhost` ya da HTTPS üzerinden açılır. Ağdaki tabletlerden kullanmak için uygulama HTTPS arkasında yayınlanmalıdır. Ses yalnız bellekte işlenir, diske yazılmaz; konuşma modelleri `VA_STT_MODEL`, `VA_TTS_MODEL` ve `VA_TTS_VOICE` ile değiştirilir.

## Yerel kurulum (Docker'sız)

Tek bilgisayarda, Docker ve yönetici yetkisi olmadan çalışır. Her şey tek süreçtedir: API, belge işçisi ve arayüz aynı adresten açılır; veriler `data/` klasöründe kalır (SQLite dosyası, gömülü Qdrant, yüklenen belgeler). GPU gerekmez. Neden böyle kurulduğu: [0003](docs/decisions/0003-yerel-tek-surec.md).

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

2. `baslat.bat` dosyasına çift tıklayın. Paketleri kurar, arayüz eskiyse derler, eksik araçları bildirir ve tarayıcıda <http://127.0.0.1:8080> adresini açar. Kapatmak için pencerede Ctrl+C. macOS/Linux'ta: `uv sync --extra retrieval --extra ingest && uv run python -m apps.local`.

İlk açılış internetten modelleri indirir ve uzun sürer: arama modeli (bge-m3, ~2,3 GB) açılışta, belge işleme modelleri (Docling, RapidOCR) ilk belgede. Modeller kullanıcının önbellek klasöründe kalır, sonraki açılışlar hızlıdır. Soru sormak için önce soldan belge yükleyin; işlenip "Hazır" olunca sorulabilir.

Gömülü Qdrant klasörü tek sürece kilitlenir: uygulama aynı anda bir kez açılabilir. Ölçüm komutları kendi klasörlerini kullanır, uygulama açıkken de çalışır.

### Araçlar

Uygulama araçları PATH'te ya da ayarla verilen yolda arar (`VA_TESSERACT_PATH`, `VA_SOFFICE_PATH`; `.env` içine tam `.exe` yolu). `baslat.bat` şu klasörleri kendisi PATH'e ekler: `%LOCALAPPDATA%\Programs\nodejs`, `%LOCALAPPDATA%\Programs\Tesseract-OCR`, `%LOCALAPPDATA%\Programs\LibreOffice\program`.

- **Tesseract:** [UB Mannheim kurulumu](https://github.com/UB-Mannheim/tesseract/wiki), "yalnız benim için" seçilerek `%LOCALAPPDATA%\Programs\Tesseract-OCR` klasörüne. Türkçe dil verisi kurulumda seçilir ya da `tur.traineddata` dosyası ([tessdata_fast](https://github.com/tesseract-ocr/tessdata_fast)) `tessdata` klasörüne kopyalanır. Kontrol: `tesseract --list-langs` içinde `tur` ve `eng`.
- **LibreOffice:** [libreoffice.org](https://www.libreoffice.org/download/download-libreoffice/) MSI dosyası kurulmadan açılır (yönetici istemez):

  ```powershell
  msiexec /a LibreOffice_x.y.z_Win_x86-64.msi /qb TARGETDIR="$env:LOCALAPPDATA\Programs\LibreOffice"
  ```

### Güncelleme

```powershell
git pull
```

Sonra `baslat.bat`: yeni paketler kurulur, arayüz değiştiyse yeniden derlenir. Açık sayfaları yenileyin. Yarım kalan belge işleri uygulama açılınca kendiliğinden yeniden başlar.

### Ağdan erişim

Arayüz yalnız bu bilgisayardan (`127.0.0.1`) açılır. Tabletlerden kullanmadan önce [açık notlardaki](docs/acik-notlar.md) "Yayına almadan önce" maddelerine bakın: giriş yokken ağdaki herkes belgeleri görebilir, yerel kurulumda güvenlik başlıkları ve hız sınırı yoktur, mikrofon da yalnız HTTPS üzerinden açılır.

## Sunucu (Docker)

Sunucu paketi: Qdrant ayrı serviste, belge işçisi ayrı süreçte, arayüzü nginx sunar; veritabanı yine SQLite dosyasıdır (API ve işçi aynı birimi paylaşır). Bu bilgisayarda denenemedi; CI'daki `services` işi derleyip açılışını sınar.

1. `.env` dosyasını yukarıdaki gibi oluşturun.

2. Servisleri derleyip başlatın. İlk derleme paketleri indirir ve yavaş bağlantıda bir saate yaklaşabilir.

   ```bash
   docker compose up -d --build
   ```

3. Belge işleme modellerini bir kez indirin. Modeller bir birimde kalır.

   ```bash
   docker compose run --rm worker docling-tools models download layout tableformer rapidocr --output-dir /opt/docling-models
   ```

Arayüz: <http://127.0.0.1:8080>. Güncelleme: `git pull` ve `docker compose up -d --build`.

## Geliştirme

Python:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy
```

Web (`apps/web`; `npm run dev` API'yi `localhost:8000` adresinde bekler):

```bash
npm ci
npm test
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

Model cevapları `evals/output/answer-cache` altında saklanır; aynı istek yeniden gönderilmez. Önbellekten gelen soruların süresi ve maliyeti rapora girmez, sayıları yazılır. Yeniden sormak için `--refresh-cache`. Uygulama bu önbelleği kullanmaz.

Belge işleme kapsamını ölçmek için:

```bash
uv run python -m evals.ingest_check --set evals/output/set7
```

## Yapı

| Yol | Görev |
| --- | --- |
| `apps/api` | HTTP API; yerelde arayüzü de sunar |
| `apps/worker` | Belge işleme işçisi; yerelde API sürecinde, sunucuda ayrı süreç |
| `apps/local.py`, `baslat.bat` | Yerel başlatma |
| `apps/web` | Web arayüzü |
| `src/visual_agent` | Çekirdek paket; katman sınırları testle korunur |
| `evals` | Test belgesi üretimi ve ölçüm |
| `docs/decisions` | Alınan kararlar |
| `docs/acik-notlar.md` | Sonraya bırakılan konular |

Ayarlar `VA_` önekli ortam değişkenlerinden ya da `.env` dosyasından okunur: [`settings.py`](src/visual_agent/settings.py).
