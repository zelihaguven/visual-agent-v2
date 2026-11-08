# Visual Agent

Önceden yüklenmiş belgelere yazarak ya da konuşarak soru sorulan, her cevabı kaynağıyla gösteren web aracı.

Durum: iskelet, test belgesi üreticisi ve doğrulama çekirdeği hazır (A0–A2). Uçtan uca soru-cevap henüz yok.

## Çalıştırma

Docker ile bütün servisler:

```bash
cp .env.example .env
docker compose up --build
```

Arayüz: <http://127.0.0.1:8080>

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
