# Visual Agent

Önceden yüklenmiş belgelere yazarak ya da konuşarak soru sorulan, her cevabı kaynağıyla gösteren web aracı.

Durum: belge yükleme, işleme, kaynaklı soru-cevap, sohbet bağlamı, ses ve web arayüzü çalışıyor (A0–A7). Giriş henüz yok.

Mikrofon tarayıcıda yalnız `localhost` ya da HTTPS üzerinden açılır. Ağdaki tabletlerden kullanmak için uygulama HTTPS arkasında yayınlanmalıdır. Ses yalnız bellekte işlenir, diske yazılmaz; konuşma modelleri `VA_STT_MODEL`, `VA_TTS_MODEL` ve `VA_TTS_VOICE` ile değiştirilir.

## Kurulum

Gereken: Docker (Compose ile) ve veri saklamayan uçlara erişimi olan bir OpenRouter anahtarı. GPU gerekmez, her şey CPU'da çalışır.

1. Ayar dosyasını oluşturun ve içindeki `VA_OPENROUTER_API_KEY` değerini doldurun. Bu dosya repoya girmez.

   ```bash
   cp .env.example .env
   ```

2. Servisleri derleyip başlatın. İlk derleme paketleri indirir ve yavaş bağlantıda bir saate yaklaşabilir; sonraki kod güncellemeleri saniyeler sürer.

   ```bash
   docker compose up -d --build
   ```

3. Belge işleme modellerini bir kez indirin. Modeller bir birimde kalır, her kurulumda bir kez yeterlidir.

   ```bash
   docker compose run --rm worker docling-tools models download layout tableformer rapidocr --output-dir /opt/docling-models
   ```

Arayüz: <http://127.0.0.1:8080>. Soru sormak için önce soldan belge yükleyin; işlenip "Hazır" olunca sorulabilir. Arama modelleri servis açılışında arka planda yüklenir, ilk açılışta internetten indirilir.

### Güncelleme

```bash
git pull
docker compose up -d --build
```

Güncellemeden sonra açık sayfaları yenileyin. Yarım kalan belge işleri işçi açılınca kendiliğinden yeniden başlar.

### Ağdan erişim

Arayüz varsayılan olarak yalnız bu bilgisayardan açılır. Tabletlerden kullanmadan önce [açık notlardaki](docs/acik-notlar.md) giriş ve HTTPS maddelerine bakın: giriş yokken ağdaki herkes belgeleri görebilir, mikrofon da yalnız HTTPS üzerinden açılır.

## Geliştirme

Python:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy
```

Web (`apps/web`):

```bash
npm ci
npm test
npm run dev
```

Test belgelerini ve doğru cevapları üretmek için:

```bash
uv run python -m evals.generate --seed 7 --output evals/output/set
```

Belge işleme kapsamını işçi imajında, internetsiz ölçmek için:

```bash
docker build --target ingest -t visual-agent-ingest .
docker run --rm --network none -v "$PWD/evals:/app/evals:ro" visual-agent-ingest python -m evals.ingest_check --set evals/output/set
```

## Yapı

| Yol | Görev |
| --- | --- |
| `apps/api` | HTTP API |
| `apps/worker` | Belge işleme işçisi |
| `apps/web` | Web arayüzü |
| `src/visual_agent` | Çekirdek paket; katman sınırları testle korunur |
| `evals` | Test belgesi üretimi ve ölçüm |
| `docs/decisions` | Alınan kararlar |
| `docs/acik-notlar.md` | Sonraya bırakılan konular |

Ayarlar `VA_` önekli ortam değişkenlerinden okunur: [`settings.py`](src/visual_agent/settings.py).
