"""Sentetik tech pack'i PDF'e çizer ve doğru cevabı aynı çizimden kaydeder.

Her değer çizildiği anda kutusuyla birlikte kaydedilir: doğru cevap sayfadaki yazıdan ayrı bir
kopya değildir. Sayfanın altındaki kimlik ("SYN-3 · 4/6") taranmış sayfayı doğru cevapla
eşleştirmek içindir; doğru cevaba girmez.
"""

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from evals.ocr_truth import Box, TruthDocument, TruthPage, TruthValue, ValueKind
from evals.render.pdf import FONT_DIR
from evals.scenarios.techpack import Document, Page, Style, Table

FONTS = {
    "DejaVu": ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf"),
    "PTSans": ("PT_Sans-Web-Regular.ttf", "PT_Sans-Web-Bold.ttf"),
    "PTSerif": ("PT_Serif-Web-Regular.ttf", "PT_Serif-Web-Bold.ttf"),
}
_MARGIN = 36.0
_PAD = 3.0
_ASCENT = 0.8
_DESCENT = 0.25
_LIGHT = colors.Color(0.9, 0.9, 0.9)
_LINE = colors.Color(0.55, 0.55, 0.55)
_STACKED_RE = re.compile(r"^([-−]?)(\d+ )?(\d+)/(\d+)$")


def register_fonts() -> None:
    for name, (regular, bold) in FONTS.items():
        if f"TP-{name}" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(f"TP-{name}", str(FONT_DIR / regular)))
            pdfmetrics.registerFont(TTFont(f"TP-{name}-Bold", str(FONT_DIR / bold)))


class _Pen:
    """Sol-üst köşeye göre çizer; kaydedilen kutular da bu düzendedir."""

    def __init__(self, canvas: Canvas, style: Style, height: float) -> None:
        self.canvas, self.style, self.height = canvas, style, height
        self.regular, self.bold = f"TP-{style.font}", f"TP-{style.font}-Bold"

    def width(self, text: str, bold: bool = False, size: float | None = None) -> float:
        font = self.bold if bold else self.regular
        return float(pdfmetrics.stringWidth(text, font, size or self.style.size))

    def text(
        self, x: float, baseline: float, text: str, bold: bool = False, size: float | None = None
    ) -> Box:
        size = size or self.style.size
        match = _STACKED_RE.match(text) if self.style.fraction == "stacked" and not bold else None
        if match is None:
            self.canvas.setFont(self.bold if bold else self.regular, size)
            self.canvas.drawString(x, self.height - baseline, text)
            right = x + self.width(text, bold, size)
        else:
            right = self._stacked(x, baseline, match, size)
        return (x, baseline - _ASCENT * size, right, baseline + _DESCENT * size)

    def _stacked(self, x: float, baseline: float, match: re.Match[str], size: float) -> float:
        """Kesir küçük rakamlarla: pay yukarıda, payda aşağıda (gerçek föylerdeki gibi)."""
        sign, whole, top, bottom = match.groups()
        small = size * 0.65
        pieces = (
            (f"{sign}{whole or ''}", size, 0.0),
            (top, small, 0.35 * size),
            ("/", size, 0.0),
            (bottom, small, -0.1 * size),
        )
        for piece, piece_size, rise in pieces:
            if piece:
                self.canvas.setFont(self.regular, piece_size)
                self.canvas.drawString(x, self.height - baseline + rise, piece)
                x += pdfmetrics.stringWidth(piece, self.regular, piece_size)
        return x

    def rule(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.canvas.setStrokeColor(_LINE)
        self.canvas.setLineWidth(0.5)
        self.canvas.line(x1, self.height - y1, x2, self.height - y2)

    def fill(self, x: float, top: float, width: float, height: float, color: colors.Color) -> None:
        self.canvas.setFillColor(color)
        self.canvas.rect(x, self.height - top - height, width, height, stroke=0, fill=1)
        self.canvas.setFillColor(colors.black)


def _wrap(pen: _Pen, text: str, width: float) -> list[str]:
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and pen.width(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    return [*lines, current] if current else lines


class _PageWriter:
    def __init__(self, pen: _Pen, page_width: float, page_height: float) -> None:
        self.pen, self.right, self.bottom = pen, page_width - _MARGIN, page_height - _MARGIN - 20
        self.y = _MARGIN
        self.values: list[TruthValue] = []
        self.leading = pen.style.size * 1.35

    def record(self, kind: ValueKind, value: str, box: Box, **where: object) -> None:
        if value.strip():
            self.values.append(TruthValue(kind=kind, value=value, box=box, **where))

    def line(self, text: str, bold: bool = False, size: float | None = None) -> None:
        size = size or self.pen.style.size
        baseline = self.y + _ASCENT * size
        self.record(ValueKind.TEXT, text, self.pen.text(_MARGIN, baseline, text, bold, size))
        self.y += size * 1.35

    def banner(self, banner: tuple[str, ...]) -> None:
        half = (self.right - _MARGIN) / 2
        for row in ((banner[0], banner[1]), (banner[2], banner[3])):
            for column, text in enumerate(row):
                x = _MARGIN + column * half
                self.record(
                    ValueKind.TEXT,
                    text,
                    self.pen.text(
                        x + _PAD, self.y + _PAD + _ASCENT * self.pen.style.size, text, bold=True
                    ),
                )
                self.pen.rule(x, self.y, x, self.y + self.leading + 2 * _PAD)
            self.pen.rule(_MARGIN, self.y, self.right, self.y)
            self.y += self.leading + 2 * _PAD
        self.pen.rule(_MARGIN, self.y, self.right, self.y)
        self.y += self.leading

    def form(self, pairs: tuple[tuple[str, str], ...], columns: int) -> None:
        span = (self.right - _MARGIN) / columns
        label_width = max(self.pen.width(label, bold=True) for label, _ in pairs) + 2 * _PAD
        rows = -(-len(pairs) // columns)
        for index, (label, value) in enumerate(pairs):
            x = _MARGIN + (index // rows) * span
            top = self.y + (index % rows) * (self.leading + 2 * _PAD)
            if self.pen.style.ruling == "zebra" and index % 2 == 0:
                self.pen.fill(x, top, span - 6, self.leading + 2 * _PAD, _LIGHT)
            baseline = top + _PAD + _ASCENT * self.pen.style.size
            self.pen.text(x + _PAD, baseline, label, bold=True)
            box = self.pen.text(x + label_width, baseline, value)
            self.record(ValueKind.PAIR, value, box, label=label)
            if self.pen.style.ruling == "grid":
                self.pen.rule(
                    x, top + self.leading + 2 * _PAD, x + span - 6, top + self.leading + 2 * _PAD
                )
        self.y += rows * (self.leading + 2 * _PAD) + self.leading

    def _widths(self, table: Table) -> list[float]:
        """Sütun en geniş yazısı kadar; sığmazsa uzun metinli sütun daralır ve satır kayar."""
        widths = [
            max(
                [self.pen.width(table.columns[c], bold=True)]
                + [self.pen.width(r[c]) for r in table.rows if len(r) > c]
            )
            + 2 * _PAD
            for c in range(len(table.columns))
        ]
        available = self.right - _MARGIN
        wide = table.wide_column
        if wide is not None and sum(widths) > available:
            widths[wide] = max(60.0, available - (sum(widths) - widths[wide]))
        return widths

    def table(self, table: Table, index: int) -> None:
        pen, size = self.pen, self.pen.style.size
        widths = self._widths(table)
        x_starts = [_MARGIN + sum(widths[:c]) for c in range(len(widths))]
        table_right = x_starts[-1] + widths[-1]
        header_height = self.leading + 2 * _PAD
        pen.fill(_MARGIN, self.y, table_right - _MARGIN, header_height, _LIGHT)
        for c, name in enumerate(table.columns):
            pen.text(x_starts[c] + _PAD, self.y + _PAD + _ASCENT * size, name, bold=True)
        self._rules(x_starts, table_right, self.y, header_height)
        self.y += header_height
        for row_number, row in enumerate(table.rows):
            if len(row) == 1:
                if self.y + header_height > self.bottom:
                    break
                baseline = self.y + _PAD + _ASCENT * size
                self.record(
                    ValueKind.TEXT, row[0], pen.text(_MARGIN + _PAD, baseline, row[0], True)
                )
                self._rules([_MARGIN], table_right, self.y, header_height)
                self.y += header_height
            elif not self._value_row(table, index, row, row_number, widths, x_starts):
                break
        pen.rule(_MARGIN, self.y, table_right, self.y)
        self.y += self.leading
        if table.note:
            self.line(table.note)

    def _value_row(
        self,
        table: Table,
        index: int,
        row: tuple[str, ...],
        row_number: int,
        widths: list[float],
        x_starts: list[float],
    ) -> bool:
        """Satırı çizer ve hücrelerini kaydeder; sayfada yer yoksa False."""
        pen, size = self.pen, self.pen.style.size
        table_right = x_starts[-1] + widths[-1]
        cells = [
            _wrap(pen, text, widths[c] - 2 * _PAD) if c == table.wide_column else [text]
            for c, text in enumerate(row)
        ]
        height = max(len(lines) for lines in cells) * self.leading + 2 * _PAD
        if self.y + height > self.bottom:
            return False
        if pen.style.ruling == "zebra" and row_number % 2 == 1:
            pen.fill(_MARGIN, self.y, table_right - _MARGIN, height, _LIGHT)
        for c, lines in enumerate(cells):
            top = self.y + _PAD + _ASCENT * size
            boxes = [
                pen.text(x_starts[c] + _PAD, top + n * self.leading, line)
                for n, line in enumerate(lines)
            ]
            if boxes:
                box = (boxes[0][0], boxes[0][1], max(b[2] for b in boxes), boxes[-1][3])
                where = {"table": index, "row_key": row[table.key_column]}
                self.record(ValueKind.CELL, row[c], box, column=table.columns[c], **where)
        self._rules(x_starts, table_right, self.y, height)
        self.y += height
        return True

    def _rules(self, x_starts: list[float], right: float, top: float, height: float) -> None:
        self.pen.rule(_MARGIN, top, right, top)
        if self.pen.style.ruling == "grid":
            for x in [*x_starts, right]:
                self.pen.rule(x, top, x, top + height)

    def lines(self, lines: tuple[str, ...]) -> None:
        for text in lines:
            for piece in _wrap(self.pen, text, self.right - _MARGIN):
                if self.y + self.leading > self.bottom:
                    return
                self.line(piece)


def render(document: Document, target: Path, set_label: str) -> TruthDocument:
    register_fonts()
    size = landscape(A4) if document.style.landscape else A4
    canvas = Canvas(str(target), pagesize=size, invariant=1)
    canvas.setTitle(document.doc_id)
    pages: list[TruthPage] = []
    total = len(document.pages)
    for number, page in enumerate(document.pages, start=1):
        writer = _PageWriter(_Pen(canvas, document.style, size[1]), size[0], size[1])
        _page(writer, document, page)
        identity = (
            f"{document.doc_id.upper().replace('SYN', 'SYN-')} · {number}/{total} · {set_label}"
        )
        canvas.setFont("TP-DejaVu", 6)
        canvas.drawString(_MARGIN, 18, identity)
        canvas.showPage()
        pages.append(TruthPage(page=number, page_type=page.page_type, values=tuple(writer.values)))
    canvas.save()
    return TruthDocument(doc_id=document.doc_id, source="synthetic", pages=tuple(pages))


def _page(writer: _PageWriter, document: Document, page: Page) -> None:
    writer.banner(document.banner)
    writer.line(page.title, bold=True, size=document.style.size + 4)
    if page.pairs:
        writer.form(page.pairs, page.form_columns)
    if page.table is not None:
        writer.table(page.table, 1)
    writer.lines(page.lines)


def generate_set(seed: int, count: int, output: Path, set_label: str) -> list[tuple[str, str]]:
    """Belgeleri, doğru cevapları ve sha256 özetlerini yazar. Doğru cevaptaki her değer dijital
    PDF'in metin katmanında kendi kutusunda bulunmalı; bulunmazsa hata verir."""
    import hashlib
    from random import Random

    from evals.ocr_truth import layer_mismatches, write_truth
    from evals.scenarios.techpack import build_document

    rng = Random(seed)
    output.mkdir(parents=True, exist_ok=True)
    digests: list[tuple[str, str]] = []
    truths: list[TruthDocument] = []
    for number in range(1, count + 1):
        document = build_document(rng, number, tuple(FONTS))
        pdf = output / f"{document.doc_id}.pdf"
        truth = render(document, pdf, set_label)
        mismatches = layer_mismatches(pdf, truth)
        if mismatches:
            raise ValueError(
                f"{document.doc_id}: metin katmanı doğru cevapla uyuşmuyor: {mismatches[:5]}"
            )
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        truths.append(truth.model_copy(update={"seed": seed, "pdf_sha256": digest}))
        digests.append((pdf.name, digest))
    write_truth(truths, output)
    for truth in truths:
        name = f"{truth.doc_id}.json"
        digests.append((name, hashlib.sha256((output / name).read_bytes()).hexdigest()))
    return digests


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Sentetik tech pack setini üretir.")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--set-label", default="A")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for name, digest in generate_set(args.seed, args.count, args.output, args.set_label):
        print(f"{digest}  {name}")


if __name__ == "__main__":
    main()
