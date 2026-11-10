# 0004: Yerel kurulumda ölçüm sonuçları

Tarih: 2026-11-10. Ölçümler üretilmiş test setiyle, Docker'sız yerel kurulumda ([0003](0003-yerel-tek-surec.md)) yapıldı. Soru bazındaki sonuçlar ve ölçüm bilgileri: [`evals/baselines/taban/`](../../evals/baselines/taban).

## Geçerli taban

[0002](0002-olcum-kararlari.md)'deki sayılar (geliştirme 33/35, son sınav 37/40) Docker imajındaki araç sürümleriyle ölçüldü ve yalnız referanstır. 35 soruluk geliştirme ölçümü yeniden üretilemiyor: test üreticisi o tarihten beri değişmediği halde `--seed 7` bugün 40 soru veriyor, eski koşuların soru bazındaki sonuçları da saklanmamış. Bundan sonraki her karşılaştırma bu bilgisayardaki tabana göre yapılır.

Araçlar: Tesseract 5.4.0, LibreOffice 26.8.2, Docling 2.149.0, OCRmyPDF 17.13.0, RapidOCR 3.10.0. Cevap modeli `google/gemma-4-26b-a4b-it`. Ölçülen kod `441a394`, puanlama `95e1870`.

| Set | Geçen | Doğrulanmış yanlış değer | Atlanan netleştirme | Gereksiz ret | Maliyet (canlı sorular) |
| --- | --- | --- | --- | --- | --- |
| Geliştirme (`--seed 7`) | 37/40 | 0 | 0 | 1 | 0,0084 $ |
| Son sınav (`--seed 11`) | 37/40 | 0 | 1 | 0 | 0,0065 $ (30 soru) |

Son sınavda 10 sorunun bazı yardımcı model istekleri geliştirme koşusuyla birebir aynı olduğu için önbellekten geldi; bu soruların süre ve maliyeti özete girmedi.

Geçmeyenler:

| Soru | Belge türü | Set | Sonuç |
| --- | --- | --- | --- |
| `dikim-tarama-etiket` | tarama | geliştirme | "Bulunamadı" (gereksiz ret); 0002'de son sınavda da görülmüştü |
| `dikim-foto-olcu` | fotoğraf | ikisi de | Değer doğrulanamadı |
| `dikim-sohbet-1-t4` | metinli PDF | ikisi de | Model değişince beden düştü, beden yeniden soruldu |
| `dikim-revizyon-netlestir` | metinli PDF (iki sürüm) | son sınav | Netleştirme yerine iki sürümün değeri kaynağıyla listelendi (atlanan netleştirme) |

## Puanlama: atlanan netleştirme ayrı sayılır

Netleştirme beklenen soruda rozetli cevap, altın verideki farklı değerlerin hepsini kaynağıyla ve başka değer olmadan veriyorsa "atlanan netleştirme" sayılır ve ayrı raporlanır; durma koşulu değildir. Değerlerin yalnız bir kısmı verildiyse (tahmin), kaynak gösterilmediyse ya da cevapta başka değer varsa "doğrulanmış yanlış değer" sayılır; bu her ölçümde 0 olmalıdır. Ayrım yalnız altın veriden yapılır. Eski sayımla son sınavdaki tek "doğrulanmış yanlış" bu soruydu; kayıtlı cevaplar modele gitmeden yeniden puanlandı.

## Kararsız sorular

İki soru önbelleksiz 5'er kez soruldu. Adım 5 karşılaştırmasında bu sorular gerileme sayılmadan önce ayrıca incelenir.

| Soru | Geliştirme | Son sınav | Not |
| --- | --- | --- | --- |
| `dikim-revizyon-netlestir` | 5/5 | 1/5 | Geçmeyen 4 tekrarın hepsi atlanan netleştirme; doğrulanmış yanlış değer yok |
| `dikim-sohbet-1-t4` | 0/5 | 0/5 | Takip sorusu tamamlanırken beden her seferinde düşüyor |
