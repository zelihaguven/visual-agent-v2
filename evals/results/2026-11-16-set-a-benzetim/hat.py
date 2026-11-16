"""Mevcut hat (resim yolundan): her taranmış PDF ve fotoğraf ayrı belge olarak işlenir.
Uygulamadaki ilk yüklemeyle aynı: dil bilinmiyor (OCR tur+eng), hücre okuyucu açık."""
import json, sys, tempfile, time
from pathlib import Path
from visual_agent.domain.document import UNDETECTED_LANGUAGE, DocumentMeta
from visual_agent.ingest.cell_reader import cell_reader_from_settings
from visual_agent.ingest.pipeline import ingest_document
from visual_agent.ingest.tools import default_tools
from visual_agent.settings import Settings

inputs, out = Path(sys.argv[1]), Path(sys.argv[2])
tools = default_tools(cell_reader=cell_reader_from_settings(Settings()))
result, times = {}, {}
for path in sorted(p for p in inputs.iterdir() if p.suffix in (".pdf", ".jpg")):
    start = time.time()
    with tempfile.TemporaryDirectory() as work:
        r = ingest_document(path, DocumentMeta(doc_id=path.stem, title=path.stem, language=UNDETECTED_LANGUAGE), tools, Path(work))
    result[path.stem] = [c.model_dump(mode="json") for c in r.chunks]
    times[path.stem] = round(time.time() - start, 1)
    print(path.name, times[path.stem], "sn", len(r.chunks), "parça", r.report.uncertain_values, "belirsiz", flush=True)
out.write_text(json.dumps({"chunks": result, "seconds": times}, ensure_ascii=False))
