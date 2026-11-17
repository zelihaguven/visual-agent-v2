"""PaddleOCR-VL çıktısının ikinci okuması: Tesseract, blok bazında sayarak (dondurulmuş kod)."""
import json, sys, time
from pathlib import Path
from PIL import Image
from evals.ocr_score import second_reading_marks, tesseract_reader
M = Path(sys.argv[1]); read = tesseract_reader(); times = {}
for res in sorted((M / "paddle").glob("*/s*_res.json")):
    n = res.name.split("_")[0]
    image = Image.open(M / "sayfalar" / res.parent.name / f"{n}.png")
    start = time.time()
    marks = second_reading_marks(res, image, read)
    (res.parent / f"{n}_uncertain.json").write_text(json.dumps({str(k): v for k, v in marks.items()}))
    times[f"{res.parent.name}/{n}"] = round(time.time() - start, 1)
(M / "paddle" / "tesseract_sureleri.json").write_text(json.dumps(times))
print("ikinci okuma bitti", len(times), "sayfa", round(sum(times.values()), 1), "sn")
