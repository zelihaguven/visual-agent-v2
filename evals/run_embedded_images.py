"""Bugünkü eski OCR yolunun (gömülü görsel: RapidOCR + Tesseract) set A benzetimindeki ölçümü.

Set A benzetiminin taranmış sayfaları ve telefon fotoğrafları (karar 0009), metinli bir sayfaya
gömülü görsel olarak konur (Word'e ya da PDF'e yapıştırılmış tablo görüntüsü gibi) ve
uygulamanın bugünkü belge işleme hattından geçer. Böyle sayfalar sayfa okuyucusuna gitmez:
metinli sayfadaki görseli eski yol okur (karar 0018). Ölçek korunur (küçültme yok): görsel,
hattın 300 dpi çizdiği sayfada kendi piksel boyutundadır. Pikseller bire bir aynı değildir: hat
görseli sayfa çiziminden keser ve çizim yeniden örnekler (karar 0022, Sınırlar).

Puanlama dondurulmuş betikle yapılır (`evals/results/2026-11-16-set-a-benzetim/puanla.py`,
karar 0008); çıktı 0010'daki tabloyla aynı satırlardır. Sayfa okuyucusu çalıştırılmaz: bir sayfa
okuyucuya ya da ocrmypdf yoluna düşerse, ya da görsel okunmadan atlanırsa koşu durur.

Puanlayıcı `figure` türü parçayı tek hücreli satır sayar: görsel tablo olarak tanınmadıysa doğru
okunan değer de "atlama" çıkar ve "yanlış gösterilen" olduğundan düşük görünür. Bu yüzden çıktıya
taramadan okunan parçaların türü de yazılır (`ozet.json`); eşik (0022) onunla birlikte okunur.

    python -m evals.run_embedded_images --output evals/output/set-a-gomulu

Benzetim girdileri yoksa aynı tohumla üretilir. `--only syn2_s6_foto` tek belgeyle dener.
"""

import argparse
import contextlib
import io
import json
import math
import runpy
import shutil
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

import pypdfium2
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from evals.render.imaging import degrade_set
from evals.render.pdf import FONT_DIR
from visual_agent.domain.document import UNDETECTED_LANGUAGE, DocumentMeta
from visual_agent.ingest.page_reader import POINTS_PER_INCH, RENDER_DPI
from visual_agent.ingest.pipeline import PageInfo, ingest_document
from visual_agent.ingest.text_layer import IMAGE_COVER_RATIO, PageKind
from visual_agent.ingest.tools import default_tools, inspect_pdf, skipped_image_warnings

SET_A = Path("evals/assets/techpack_set_a")
SIMULATION = Path("evals/output/techpack-sentetik-A-benzetim")
SIMULATION_SEED = 20261116
RECORD = Path("evals/results/2026-11-16-set-a-benzetim")
"""Dondurulmuş puanlama ve okuyucunun kayıtlı okumaları (karar 0010); değiştirilmez."""
CAPTION = "Aşağıdaki görsel belgenin taranmış bir sayfasıdır."
"""Sayfayı metinli yapan satır. Sayı ve kod taşımaz: puanlanan değerlere karışmaz."""
_FONT = "DejaVuSans"
_MARGIN = 36.0
_PAGE_HEIGHT_FACTOR = 2.2
"""Sayfa görselin bu kadar katı yüksekliktedir: görsel sayfanın yarısından azını kaplar, sayfa
metinli sayılır ve görseli gömülü görsel yolu okur."""
_ROWS = (
    ("Doğru gösterilen", ("doğru gösterilen",)),
    ("Yanlış gösterilen", ("yanlış gösterilen",)),
    ("  bağ kopması", ("bağ kopması",)),
    ("  yanlış karakter", ("yanlış karakter",)),
    ("  ayraç", ("ayraç farkı",)),
    ("Atlama", ("atlama",)),
    ("Gizlendi (doğruydu / yanlıştı)", ("gizlendi (doğruydu)", "gizlendi (yanlıştı)")),
)


def source_images(path: Path) -> list[Image.Image]:
    """Kaynağın sayfa görüntüleri: fotoğrafın kendisi, tarama PDF'inin her sayfası."""
    if path.suffix != ".pdf":
        with Image.open(path) as opened:
            return [opened.convert("RGB")]
    document = pypdfium2.PdfDocument(path)
    try:
        scale = RENDER_DPI / POINTS_PER_INCH  # benzetim taramaları 300 dpi: bire bir
        return [page.render(scale=scale).to_pil().convert("RGB") for page in document]
    finally:
        document.close()


def build_document(images: Sequence[Image.Image], target: Path) -> None:
    """Her görüntü metinli bir sayfaya kendi piksel boyutunda gömülür (kayıpsız, küçültmesiz)."""
    if _FONT not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(_FONT, str(FONT_DIR / "DejaVuSans.ttf")))
    canvas = Canvas(str(target))
    point = POINTS_PER_INCH / RENDER_DPI  # hattın çizdiği sayfada bir piksel
    for image in images:
        width, height = image.width * point, image.height * point
        # Sayfa tam piksel boyutunda: görsel piksel ızgarasına oturur, kesit kaymaz.
        page_height = math.ceil(image.height * _PAGE_HEIGHT_FACTOR) * point + 2 * _MARGIN
        canvas.setPageSize((width + 2 * _MARGIN, page_height))
        canvas.setFont(_FONT, 11)
        canvas.drawString(_MARGIN, page_height - _MARGIN, CAPTION)
        canvas.drawImage(
            ImageReader(image), _MARGIN, page_height - 2 * _MARGIN - height, width, height
        )
        canvas.showPage()
    canvas.save()


def check_routing(name: str, pages: Sequence[PageInfo]) -> None:
    """Bu ölçüm yalnız gömülü görsel yolunu ölçer; başka yola düşen sayfa koşuyu durdurur."""
    for info in pages:
        cover = sum((b.right - b.left) * (b.bottom - b.top) for b in info.image_boxes)
        if info.kind is not PageKind.TEXT or not info.image_boxes:
            target = "sayfa okuyucusuna" if info.kind is PageKind.NONE else "başka bir yola"
            raise SystemExit(
                f"{name} s.{info.page}: sayfa {target} düşüyor (tür: {info.kind.value}, "
                f"görsel {len(info.image_boxes)}, alan {cover:.0f} pt², sınır "
                f"%{IMAGE_COVER_RATIO * 100:.0f}); koşu durduruldu."
            )
    skipped = skipped_image_warnings(list(pages))
    if skipped:
        raise SystemExit(f"{name}: görsel okunmadan atlanıyor ({skipped[0]}); koşu durduruldu.")


def run(inputs: Path, output: Path, only: Sequence[str]) -> dict[str, object]:
    sources = sorted(p for p in inputs.iterdir() if p.suffix in (".pdf", ".jpg"))
    sources = [p for p in sources if not only or p.stem in only]
    if not sources:
        raise SystemExit(f"{inputs}: ölçülecek kaynak yok")
    documents = output / "belgeler"
    documents.mkdir(parents=True, exist_ok=True)
    tools = default_tools()  # sayfa okuyucusu yok: okuyucu gerektiren belge işlenmez
    chunks: dict[str, object] = {}
    seconds: dict[str, float] = {}
    kinds: Counter[str] = Counter()
    for source in sources:
        built = documents / f"{source.stem}.pdf"
        build_document(source_images(source), built)
        check_routing(source.stem, inspect_pdf(built))
        started = time.time()
        meta = DocumentMeta(doc_id=source.stem, title=source.stem, language=UNDETECTED_LANGUAGE)
        with tempfile.TemporaryDirectory() as work:
            result = ingest_document(built, meta, tools, Path(work))
        read = Counter(chunk.kind.value for chunk in result.chunks if chunk.from_ocr)
        if not read:
            raise SystemExit(f"{source.stem}: görselden parça çıkmadı; koşu durduruldu.")
        kinds.update(read)
        chunks[source.stem] = [chunk.model_dump(mode="json") for chunk in result.chunks]
        seconds[source.stem] = round(time.time() - started, 1)
        print(
            f"{source.name}: {seconds[source.stem]} sn, {len(result.chunks)} parça, "
            f"{result.report.uncertain_values} belirsiz",
            file=sys.stderr,
            flush=True,
        )
    reads = {"chunks": chunks, "seconds": seconds}
    (output / "hat_cikti.json").write_text(json.dumps(reads, ensure_ascii=False), encoding="utf-8")
    return {**reads, "kinds": dict(kinds)}


def score(output: Path) -> dict[str, dict[str, int]]:
    """Dondurulmuş puanlama betiği olduğu gibi çalıştırılır; `rapor.json` yazar. Betik okuyucu
    adayını da puanladığı için kayıtlı okumaları (0010) klasöre kopyalanır; yeniden okunmaz.
    `rapor.json`'da yalnız "mevcut hat" bölümü bu ölçümündür; "karar" alanı ve okuyucu
    karşılaştırması eski kayıttan gelir, geçerli değildir."""
    if not (output / "paddle").exists():
        shutil.copytree(RECORD / "paddle", output / "paddle")
    argv, sys.argv = sys.argv, [str(RECORD / "puanla.py"), str(output)]
    try:
        # Betiğin kendi özeti iki adayı karşılaştırır ve karar yazar; burada geçerli değil.
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(RECORD / "puanla.py"), run_name="__main__")
    finally:
        sys.argv = argv
    report = json.loads((output / "rapor.json").read_text(encoding="utf-8"))["mevcut hat"]
    return {name: report[name] for name in ("toplam", "tarama", "foto")}


def table(totals: dict[str, dict[str, int]]) -> str:
    """0010'daki tablonun satırları; sütunlar toplam, tarama ve fotoğraf."""
    lines = ["| | Toplam | Tarama | Fotoğraf |", "|---|---|---|---|"]
    names = ("toplam", "tarama", "foto")
    lines.append("| Değer | " + " | ".join(str(totals[n]["değer"]) for n in names) + " |")
    for label, keys in _ROWS:
        cells = (" / ".join(str(totals[n][key]) for key in keys) for n in names)
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Set A benzetimini gömülü görsel yolundan ölçer.")
    parser.add_argument("--inputs", type=Path, default=SIMULATION)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--only",
        type=lambda text: [item.strip() for item in text.split(",") if item.strip()],
        default=[],
        help="yalnız bu kaynaklar (virgülle; kuru deneme)",
    )
    arguments = parser.parse_args()
    if not arguments.inputs.exists():
        degrade_set(SET_A, arguments.inputs, SIMULATION_SEED)
    reads = run(arguments.inputs, arguments.output, arguments.only)
    seconds, kinds = reads["seconds"], reads["kinds"]
    assert isinstance(seconds, dict) and isinstance(kinds, dict)
    totals = score(arguments.output)
    summary = {"mevcut hat": totals, "taramadan okunan parça türleri": kinds}
    (arguments.output / "ozet.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(table(totals))
    listed = ", ".join(f"{kind} {count}" for kind, count in sorted(kinds.items()))
    print(f"\nTaramadan okunan parçalar: {listed}. `figure` satırlarının değerleri atlama sayılır.")
    print(f"Süre: {sum(seconds.values()):.0f} sn ({len(seconds)} kaynak). Bulut maliyeti: 0.")
    if arguments.only:
        print("Kuru deneme: sayılar yalnız seçilen kaynaklarındır, ölçüm sonucu değildir.")


if __name__ == "__main__":
    main()
