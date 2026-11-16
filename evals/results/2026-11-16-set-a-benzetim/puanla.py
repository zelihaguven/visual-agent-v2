"""İki adayı dondurulmuş puanlamayla (evals/ocr_score.py) puanlar; karar kuralı 0008."""
import json, sys, collections
from pathlib import Path
from evals.ocr_score import Outcome, paddle_vl_page, pipeline_pages, score_page
from evals.ocr_truth import TruthDocument
from visual_agent.domain.document import Chunk

M = Path(sys.argv[1]); SET = Path("evals/assets/techpack_set_a")
truths = {f.stem: TruthDocument.model_validate_json(f.read_text()) for f in SET.glob("syn*.json")}
FRACTION = {"syn1": "tek karakter", "syn2": "küçük rakamlı (cm)", "syn3": "düz", "syn4": "tek karakter", "syn5": "küçük rakamlı"}
WRONG = {Outcome.WRONG, Outcome.SEPARATOR, Outcome.BROKEN}

def targets(source: str) -> tuple[str, list[int], str]:
    parts = source.split("_")
    if parts[-1] == "tarama":
        return parts[0], list(range(1, 7)), "tarama"
    return parts[0], [int(parts[1][1:])], "foto"

def pipeline_reads() -> dict[str, dict[int, object]]:
    data = json.loads((M / "hat_cikti.json").read_text())["chunks"]
    reads = {}
    for source, chunks in data.items():
        doc, pages, kind = targets(source)
        got = {p.page: p for p in pipeline_pages([Chunk.model_validate(c) for c in chunks])}
        if kind == "foto":  # tek sayfalık belge: hattın 1. sayfası föyün M. sayfasıdır
            got = {pages[0]: got.get(1)}
        reads[source] = got
    return reads

def paddle_reads() -> dict[str, dict[int, object]]:
    reads = {}
    for folder in sorted((M / "paddle").iterdir()):
        if not folder.is_dir():
            continue
        got = {}
        for res in folder.glob("s*_res.json"):
            n = int(res.name[1:].split("_")[0])
            marks_file = folder / f"s{n}_uncertain.json"
            marks = {int(k): v for k, v in json.loads(marks_file.read_text()).items()} if marks_file.exists() else {}
            got[n] = paddle_vl_page(res, n, marks)
        reads[folder.name] = got
    return reads

def score(reads):
    rows = []
    for source, got in reads.items():
        doc, pages, kind = targets(source)
        for n in pages:
            truth_page = truths[doc].pages[n - 1]
            for value, outcome in score_page(truth_page, got.get(n)):
                rows.append({"kaynak": kind, "belge": doc, "sayfa": n, "tür": truth_page.page_type,
                             "kesir": FRACTION[doc], "değer_türü": value.kind.value, "beklenen": value.value, "sonuç": outcome})
    return rows

def totals(rows):
    c = collections.Counter(r["sonuç"] for r in rows)
    return {"değer": len(rows), "doğru gösterilen": c[Outcome.CORRECT],
            "yanlış gösterilen": sum(c[o] for o in WRONG),
            **{o.value: c[o] for o in Outcome}}

def breakdown(rows, key):
    groups = collections.defaultdict(list)
    for r in rows:
        groups[r[key]].append(r)
    return {k: {"doğru": totals(v)["doğru gösterilen"], "yanlış": totals(v)["yanlış gösterilen"],
                "gizli_doğru": totals(v)[Outcome.HIDDEN_RIGHT.value], "değer": len(v)} for k, v in sorted(groups.items())}

report = {}
for name, reads in (("mevcut hat", pipeline_reads()), ("PaddleOCR-VL + Tesseract", paddle_reads())):
    rows = score(reads)
    report[name] = {"toplam": totals(rows),
                    "tarama": totals([r for r in rows if r["kaynak"] == "tarama"]),
                    "foto": totals([r for r in rows if r["kaynak"] == "foto"]),
                    "sayfa türü": breakdown(rows, "tür"), "kesir yazımı": breakdown(rows, "kesir"),
                    "değer türü": breakdown(rows, "değer_türü"),
                    "yanlış örnekler": [{k: (v.value if isinstance(v, Outcome) else v) for k, v in r.items()}
                                        for r in rows if r["sonuç"] in WRONG][:40]}
a, b = report["mevcut hat"]["toplam"], report["PaddleOCR-VL + Tesseract"]["toplam"]
wrong_ok = b["yanlış gösterilen"] <= a["yanlış gösterilen"]
if not wrong_ok:
    decision = "Reddedilir (yanlış gösterilen daha fazla)"
elif b["doğru gösterilen"] > a["doğru gösterilen"]:
    decision = "Benimsenir"
elif b[Outcome.HIDDEN_RIGHT.value] > a[Outcome.HIDDEN_RIGHT.value]:
    decision = "Ara durum"
else:
    decision = "Reddedilir (kazanç yok)"
report["karar"] = decision
(M / "rapor.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
print(json.dumps({k: (v["toplam"] if isinstance(v, dict) else v) for k, v in report.items()}, ensure_ascii=False, indent=1))
