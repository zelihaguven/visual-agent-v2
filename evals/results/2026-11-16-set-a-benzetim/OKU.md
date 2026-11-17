# Set A benzetimi ölçüm kaydı (karar 0010)

- `hat.py` uygulamanın belge işleme hattını çağırır. Karar 0011'den sonra uygulamanın hattı
  değişti: eski hattı ("mevcut hat" adayı) ölçmek için `c79e4ce` kullanılmalı. Bugünkü kodla
  çalıştırılırsa yeni hattı ölçer.
- Dört betik (`hat.py`, `paddle_calistir.py`, `tesseract.py`, `puanla.py`) ölçüldükleri haliyle
  donmuştur (`tests/test_ocr_score.py`).
- Set A'ya yeniden okuyucu çalıştırılmaz; yeni tasarım yeni tohumla üretilen set B ile ölçülür.
