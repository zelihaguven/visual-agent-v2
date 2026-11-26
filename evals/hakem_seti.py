# ruff: noqa: E501 - set tablosu ve ölçülen istem satır satır korunur
"""LLM hakem ölçümü: istem, etiketli çift seti ve çalıştırıcı (kararlar, "LLM hakem yok").

GEÇİCİ SET: üretilmiş föylerden 40 çift (15 yanlış, 25 doğru), etiketler indeksteki satır
metninden elle doğrulandı (2026-11-26). Gerçek belgelerle büyütülecek: T1 (tek varyantlı satır,
Kural D) ve T3 (Türkçe cümle, İngilizce ölçü satırı) için gerçek hatalardan çiftler eklenecek.
T3 ileride ölçülecekse tanımı FastReact alan tablolarını (C22, C23) dışarıda bırakacak biçimde
daraltılır.

Hakem uygulamanın yardımcı modelidir (ZDR, sıcaklık 0); her çift `--runs` kez sorulur. Satırlar
uygulama veritabanından "belge başlığı öneki, parça no" ile okunur; parça numaraları bugünkü
indekse bağlıdır, yeniden işlemeden sonra denetlenmelidir.

    python -m evals.hakem_seti --output evals/output/hakem.jsonl   # API çağırır (200 çağrı ≈ 0,015 $)
    python -m evals.hakem_seti --summary evals/output/hakem.jsonl  # yalnız özet
"""

import argparse
import asyncio
import json
import sqlite3
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import httpx

from apps.api.question_log import percentile
from visual_agent.ask.clients import helper_model
from visual_agent.generation.openrouter import fetch_zdr_index
from visual_agent.settings import Settings

SYSTEM = (
    "Sen bir doğrulama hakemisin. Sana bir kullanıcı sorusu, bir cevap cümlesi, cümlenin dayandığı "
    "alıntılanan tablo satırı ve aynı belgedeki ilgili kardeş satırlar verilir. Tek sorun: Bu cümle, "
    "alıntılanan satırın söylediğini mi söylüyor?\n"
    "- Uyumlu: cümledeki her iddia (değer; hangi ölçü, alan ya da etiket; hangi renk, varyant ya da "
    "beden; hangi kullanım yeri) alıntılanan satırdaki etiket ve değerle aynı şeyi kastediyor. Türkçe "
    "cümle İngilizce satırı doğru çeviriyorsa uyumludur.\n"
    "- Uyumsuz: cümle satırdaki değeri satırın etiketinden başka bir şey diye sunuyor (ör. kardeş "
    "satırdaki başka bir etiketin anlamıyla), satırın yazmadığı bir niteleyici iddia ediyor, ya da "
    "sorulan ölçüyü/alanı başka bir ölçünün/alanın satırıyla cevaplıyor.\n"
    "Kardeş satırlar yalnız karşılaştırma içindir; cümle onlara dayanmıyor. Kendi bilgini ekleme.\n"
    'Yalnız JSON döndür: {"uyumlu": true ya da false, "gerekce": "en çok 20 sözcük"}'
)
_MAX_TOKENS = 120
_DB = "data/visual_agent.db"

Y, D = "yanlış", "doğru"
B48, P12, T78, S17, P55 = "6013448", "6026412", "6029278", "6026417", "6028355"
FR = "12_Reference_Import_Data_Order_Items"
Row = tuple[str, int]
# (kimlik, kategori, etiket, soru, cümle, alıntılanan satırlar, kardeş satırlar, kaynak/not)
# T1: tek varyantlı satır (Kural D), T2: önekli etiket (Kural E), T3: Türkçe cümle, İngilizce ölçü satırı.
Pair = tuple[str, str, str, str, str, list[Row], list[Row], str]
PAIRS: list[Pair] = [
    # --- yanlış (15) ---
    ("W01", "T2", Y, "6013448'in beden aralığı nedir", "6013448 modelinin beden aralığı XS-5XL'dir.", [(B48, 207)], [(B48, 9), (B48, 10), (B48, 212)], "#2389 canlı; Chart Size Range şablon aralığı"),
    ("W02", "T2", Y, "6013448'in beden aralığı (Size Range) nedir?", "Apparel için beden aralığı XS-5XL olarak belirtilmiştir.", [(B48, 207)], [(B48, 9), (B48, 10)], "#2279"),
    ("W03", "T2", Y, "6013448'in beden aralığı (Size Range) nedir?", "Beden aralığı Apparel (XS-5XL) olarak belirtilmiştir.", [(B48, 207)], [(B48, 9), (B48, 10)], "#2311"),
    ("W04", "T2", Y, "6013448'in beden aralığı (Size Range) nedir?", "Beden aralığı (Chart Size Range) XS-5XL'dir.", [(B48, 207)], [(B48, 9), (B48, 10)], "#2375, bilinen sınır"),
    ("W05", "T2", Y, "Challenger Train Pant hangi bedenlerde üretiliyor", "Challenger Train Pant XXS-4XL beden aralığında üretilmektedir.", [(P12, 104)], [(P12, 11), (P12, 12), (P12, 103)], "S1 (b) koşu 4"),
    ("W06", "T2", Y, "6026412 hangi bedenlerde üretiliyor", "6026412'nin beden aralığı XXS-4XL'dir.", [(P12, 104)], [(P12, 11), (P12, 12)], "satır değiştirme"),
    ("W07", "T1", Y, "6029278 tişörtün beyaz renginde gövde kumaşı hangisi", "6029278 tişörtün beyaz renginde gövde kumaşı KNT-226129.", [(T78, 57)], [(T78, 59), (T78, 60)], "#57 City Khaki satırı"),
    ("W08", "T1", Y, "6029278 tişörtün beyaz renginde gövde kumaşı hangisi", "Beyaz renkte gövde kumaşı KNT-226133.", [(T78, 60)], [(T78, 59), (T78, 57)], "#60 yaka ribanası (Usage: COLLARBAND)"),
    ("W09", "T1", Y, "6029278 City Khaki renkte gövde kumaşı hangisi", "City Khaki renkte gövde kumaşı KNT-226131.", [(T78, 59)], [(T78, 57), (T78, 60)], "satır değiştirme (#59 White)"),
    ("W10", "T3", Y, "6026417 şortta MD bedende ön ağ kaç?", "MD bedende ön ağ 7.", [(S17, 102)], [(S17, 99), (S17, 100)], "Haiku eşleşmesi: Front Pocket Opening"),
    ("W11", "T3", Y, "6026417 şortun MD bedende paça ağzı kaç?", "MD bedende paça ağzı 12 1/4.", [(S17, 99)], [(S17, 95)], "satır değiştirme (Front Rise)"),
    ("W12", "T3", Y, "6026417 şortun MD bedende bel genişliği kaç?", "MD bedende bel genişliği 7.", [(S17, 98)], [(S17, 90), (S17, 91)], "satır değiştirme (Inseam)"),
    ("W13", "T3", Y, "6026417 şortta MD bedende arka ağ kaç?", "MD bedende arka ağ 12 1/4.", [(S17, 99)], [(S17, 100)], "satır değiştirme (Front Rise)"),
    ("W14", "T3", Y, "6026417 şortta paça kıvırma yüksekliği kaç?", "Paça kıvırma yüksekliği 7.", [(S17, 97)], [(S17, 96)], "satır değiştirme (Drawcord)"),
    ("W15", "T3", Y, "6028355 pantolonda uzun boy (Tall/Long) iç boy ölçüsü MD bedende kaç?", "MD bedende uzun boy iç boy ölçüsü 32.", [(P55, 110)], [(P55, 111)], "satır değiştirme (normal boy)"),
    # --- doğru (25) ---
    ("C01", "T2", D, "6013448'in beden aralığı nedir", "6013448'in beden aralığı XS-4XL, SMT-4XLT.", [(B48, 9)], [(B48, 207), (B48, 10)], "Size Range"),
    ("C02", "T2", D, "6013448'in beden aralığı (Size Range) nedir?", "Apparel için Chart Size Range XS-5XL.", [(B48, 207)], [(B48, 9)], "#2343, etiketiyle"),
    ("C03", "T2", D, "6013448'in beden aralığı (Size Range) nedir?", "Ürün ekibi bilgilerine göre gerçek bedenler XS-4XLT'dir.", [(B48, 10)], [(B48, 9), (B48, 212)], "#2311 Actual Sizes"),
    ("C04", "T2", D, "6013448'in beden aralığı (Size Range) nedir?", "Diğer bir kaynağa göre beden aralığı XS-4XL, SMT-4XLT şeklindedir.", [(B48, 9)], [(B48, 207)], "#2311"),
    ("C05", "T2", D, "6013448 hangi bedenlerde üretiliyor", "Ürünün bedenleri XS, SM, SMT, MD, MDT, LG, LGT, XL, XLT, XXL, XXLT, 3XL, 3XLT, 4XL, 4XLT.", [(B48, 212)], [(B48, 10), (B48, 207)], "Style Actual Sizes (Kural E bunu gizler)"),
    ("C06", "T2", D, "Challenger Train Pant hangi bedenlerde üretiliyor", "6026412'nin beden aralığı XS-XXL(4).", [(P12, 11)], [(P12, 104), (P12, 12)], "Size Range"),
    ("C07", "T2", D, "Challenger Train Pant hangi bedenlerde üretiliyor", "6026412'nin gerçek bedenleri XS-XXL.", [(P12, 12)], [(P12, 103), (P12, 11)], "Actual Sizes"),
    ("C08", "T2", D, "6026412 ölçü şablonunun beden aralığı nedir", "Ölçü şablonunun (Chart Size Range) aralığı XXS-4XL.", [(P12, 104)], [(P12, 11)], "şablon sorusu, etiketiyle"),
    ("C09", "T1", D, "6029278 tişörtün beyaz renginde gövde kumaşı hangisi", "Beyaz renkte gövde kumaşı KNT-226131.", [(T78, 59)], [(T78, 57), (T78, 60)], "S2 doğru cevabı"),
    ("C10", "T1", D, "6029278 tişörtün beyaz renginde gövde kumaşı hangisi", "6029278 tişörtün beyaz renginde gövde kumaşı KNT-226131/LIVe Jersey -60/40 -140 gms.", [(T78, 59)], [(T78, 57)], "#2192 cümlesi"),
    ("C11", "T1", D, "6029278 tişörtün beyaz renginde gövde kumaşı hangisi", "Beyaz (100: White) rengi için gövde kumaşı KNT-226131/LIVe Jersey -60/40 -140 gms.", [(T78, 59)], [(T78, 57)], "#2206 cümlesi"),
    ("C12", "T1", D, "6029278 City Khaki renkte gövde kumaşı hangisi", "City Khaki renkte gövde kumaşı KNT-226129.", [(T78, 57)], [(T78, 59)], "#57"),
    ("C13", "T1", D, "6029278 beyaz renkte yaka ribanası kumaşı hangisi", "Beyaz renkte yaka ribanası kumaşı KNT-226133.", [(T78, 60)], [(T78, 59)], "#60 COLLARBAND"),
    ("C14", "T3", D, "6026417 şortta MD bedende ön ağ kaç?", "MD bedende ön ağ 12 1/4.", [(S17, 99)], [(S17, 100), (S17, 102)], "#2188 Front Rise"),
    ("C15", "T3", D, "6026417 şortta MD bedende ön ağ (front rise) kaç?", "6026417 şortta MD bedende ön ağ 12 1/4'tür.", [(S17, 99)], [(S17, 100)], "#2200"),
    ("C16", "T3", D, "6026417 şortun MD bedende paça ağzı (leg opening) kaç?", "MD bedende Leg Opening at Edge - Short Inseam (Short) değeri 11 3/4'tür.", [(S17, 95)], [(S17, 94)], "#2211"),
    ("C17", "T3", D, "Peki XL?", "6026417 şortun XL bedende paça ağzı (Leg Opening at Edge - Short Inseam (Short)) 13 1/2'dir.", [(S17, 95)], [(S17, 94)], "#2212 takip"),
    ("C18", "T3", D, "6026417 şortta MD bedende arka ağ kaç?", "MD bedende arka ağ 15 7/8.", [(S17, 100)], [(S17, 99)], "Back Rise"),
    ("C19", "T3", D, "6026417 şortun MD bedende bel genişliği kaç?", "MD bedende bel genişliği 15.", [(S17, 90)], [(S17, 91)], "Waist Width at Edge - Relaxed"),
    ("C20", "T3", D, "6026417 şortun MD bedende iç boyu kaç?", "MD bedende iç boy 7.", [(S17, 98)], [(S17, 97)], "Inseam - Shorts"),
    ("C21", "T3", D, "6028355 pantolonda uzun boy (Tall/Long) iç boy ölçüsü MD bedende kaç?", "MD bedende uzun boy iç boy ölçüsü 34'tür.", [(P55, 111)], [(P55, 110)], "#2205 / #2399"),
    ("C22", "T3", D, "Order items içe aktarmada OI.CUSTSTYLE alanının tipi nedir?", "OI.CUSTSTYLE alanının tipi T15'tir.", [(FR, 10)], [(FR, 9)], "#2213 (FastReact)"),
    ("C23", "T3", D, "Peki OI.CUSTREF?", "OI.CUSTREF alanının tipi T50'dir.", [(FR, 9)], [(FR, 10)], "#2214 (FastReact)"),
    ("C24", "T3", D, "6026417 şortta MD bedende ön cep ağzı kaç?", "MD bedende ön cep ağzı 7.", [(S17, 102)], [(S17, 99)], "Front Pocket Opening"),
    ("C25", "T3", D, "6026417 şortta bel bandı yüksekliği kaç?", "Bel bandı yüksekliği bütün bedenlerde 2.", [(S17, 89)], [(S17, 90)], "WB Height"),
]  # fmt: skip


def _row_text(con: sqlite3.Connection, titles: dict[str, str], ref: Row) -> str:
    prefix, number = ref
    doc = next(doc_id for doc_id, title in titles.items() if title.startswith(prefix))
    found = con.execute(
        "select payload from chunks where chunk_id=?", (f"{doc}:{number}",)
    ).fetchone()
    return str(json.loads(found[0])["text"])


def _user_message(con: sqlite3.Connection, titles: dict[str, str], pair: Pair) -> str:
    _, _, _, question, sentence, quoted, siblings, _ = pair
    return (
        f"Soru: {question}\nCümle: {sentence}\nAlıntılanan satır:\n"
        + "\n".join(f"- {_row_text(con, titles, r)}" for r in quoted)
        + "\nAynı belgedeki ilgili satırlar:\n"
        + "\n".join(f"- {_row_text(con, titles, r)}" for r in siblings)
    )


async def run(output: Path, runs: int) -> None:
    con = sqlite3.connect(f"file:{_DB}?mode=ro", uri=True)
    titles: dict[str, str] = dict(con.execute("select doc_id, title from documents"))
    settings = Settings()
    if settings.openrouter_api_key is None:
        raise SystemExit("VA_OPENROUTER_API_KEY gerekli")
    key = settings.openrouter_api_key.get_secret_value()
    url = str(settings.openrouter_url).rstrip("/")
    async with httpx.AsyncClient(timeout=60) as http:
        judge = helper_model(http, settings, key, await fetch_zdr_index(http, url, key))
        with output.open("w", encoding="utf-8") as out:
            for pair in PAIRS:
                user = _user_message(con, titles, pair)
                for attempt in range(runs):
                    started = time.perf_counter()
                    try:
                        data, error = await judge.complete(SYSTEM, user, _MAX_TOKENS), None
                    except Exception as exc:  # noqa: BLE001 - ölçüm hatayı kaydedip sürer
                        data, error = {}, repr(exc)[:200]
                    row = {"id": pair[0], "cat": pair[1], "label": pair[2], "run": attempt,
                           "verdict": data.get("uyumlu"), "reason": data.get("gerekce"),
                           "seconds": time.perf_counter() - started, "error": error}  # fmt: skip
                    out.write(json.dumps(row, ensure_ascii=False) + "\n")
                print(pair[0], flush=True)


def summary(path: Path) -> None:
    """Kategori başına: yakalama (yanlış çiftte çoğunluk "uyumsuz"), en az bir "uyumlu" alan yanlış
    çift (kurtarma riski), yanlış veto (doğru çiftte çoğunluk "uyumsuz"), tutarsız çift, p95."""
    rows: list[dict[str, Any]] = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
    ]
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_pair[row["id"]].append(row)
    for cat in sorted({row["cat"] for row in rows}) + ["toplam"]:
        pairs = [p for p in by_pair.values() if cat in ("toplam", p[0]["cat"])]
        wrong = [p for p in pairs if p[0]["label"] == Y]
        right = [p for p in pairs if p[0]["label"] == D]

        def vetoed(p: list[dict[str, Any]]) -> bool:
            return sum(r["verdict"] is False for r in p) > len(p) / 2

        caught = sum(vetoed(p) for p in wrong)
        risky = sum(any(r["verdict"] is True for r in p) for p in wrong)
        false_veto = sum(vetoed(p) for p in right)
        mixed = sum(len({r["verdict"] for r in p}) > 1 for p in pairs)
        seconds = [r["seconds"] for p in pairs for r in p]
        print(
            f"{cat}: yakalama {caught}/{len(wrong)}, kurtarma riski {risky}, "
            f"yanlış veto {false_veto}/{len(right)}, tutarsız {mixed}, "
            f"p50 {percentile(seconds, 0.5):.2f} sn, p95 {percentile(seconds, 0.95):.2f} sn"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--output", type=Path, help="sonuç dosyası (JSON lines); API çağırır")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--summary", type=Path, help="var olan sonuç dosyasının özeti")
    args = parser.parse_args()
    if args.output:
        asyncio.run(run(args.output, args.runs))
        summary(args.output)
    elif args.summary:
        summary(args.summary)
    else:
        parser.error("--output ya da --summary gerekli")


if __name__ == "__main__":
    main()
