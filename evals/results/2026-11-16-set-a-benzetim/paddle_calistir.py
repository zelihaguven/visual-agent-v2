"""PaddleOCR-VL-1.6 resmi akış (düzen + bölge, MLX sunucusu): her sayfa görüntüsü bir kez."""
import sys, time, os, json, shutil
from pathlib import Path
from paddleocr import PaddleOCRVL
pages, out = Path(sys.argv[1]), Path(sys.argv[2])
pipe = PaddleOCRVL(pipeline_version="v1.6", vl_rec_backend="mlx-vlm-server",
                   vl_rec_server_url="http://localhost:8111/", vl_rec_api_model_name="PaddlePaddle/PaddleOCR-VL-1.6")
times = {}
for image in sorted(pages.glob("*/*.png")):
    doc, name = image.parent.name, image.stem          # <kaynak_belge>/s<n>.png
    target = out / doc; target.mkdir(parents=True, exist_ok=True)
    start = time.time()
    for r in pipe.predict(str(image)):
        r.save_to_json(save_path=str(target / f"{name}_tmp"))
    produced = next((target / f"{name}_tmp").glob("*_res.json"))
    shutil.move(str(produced), str(target / f"{name}_res.json")); shutil.rmtree(target / f"{name}_tmp")
    times[f"{doc}/{name}"] = round(time.time() - start, 1)
    print(doc, name, times[f"{doc}/{name}"], "sn", flush=True)
(out / "sureler.json").write_text(json.dumps(times))
