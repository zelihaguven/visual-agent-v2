# Visual Agent

Önceden yüklenmiş belgelere yazarak ya da konuşarak soru sorulan, her cevabı kaynağıyla gösteren web aracı.

Durum: belge yükleme, işleme, kaynaklı soru-cevap ve web arayüzü çalışıyor (A0–A5). Konuşma bağlamı, ses ve giriş henüz yok.

## Çalıştırma

Docker ile bütün servisler:

```bash
cp .env.example .env
docker compose up --build
```

Arayüz: <http://127.0.0.1:8080>

Belge işleme modelleri imaja gömülmez. Temiz kurulumda bir kez indirin:

```bash
docker compose run --rm worker docling-tools models download layout tableformer rapidocr --output-dir /opt/docling-models
```

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

Ayarlar `VA_` önekli ortam değişkenlerinden okunur: [`settings.py`](src/visual_agent/settings.py).
