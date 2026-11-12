# FastReact Asistanı — Kabul Testi

Her sorunun beklenen cevap özü ve kaynak dosyası, oluşturulan knowledge dosyalarından tek tek doğrulanmıştır. Bir cevap şu üç kontrolü geçmelidir:

- Doğru menü yolu verilmiş mi?
- Citation'larda beklenen dosya (veya aynı sayfanın başka bir part'ı) çıkmış mı?
- Uydurma alan, menü veya sürüm bilgisi yok mu?

## A. Ayarlar ve kurulum

| # | Soru | Beklenen cevap özü | Beklenen kaynak |
|---|---|---|---|
| 1 | Tarihlerin yanında hafta numarası göstermek istiyorum, nereden açarım? | Main Menu > Setup > Configure > General, Defaults altında **Week numbers > Enabled**. Her yıl için "First week commencing date" (Year 1–3) tanımlanmalı. Configure uyarısı da verilmeli. | `08_Setup_Configure_General_part1.md` |
| 2 | "Log to text file" seçeneğini açmalı mıyım? | Destek ekibinin sorun teşhisi içindir; yalnızca FastReact destek ekibi isterse açılır. | `08_Setup_Configure_General_part1.md` |
| 3 | Activity Scheduler menüsünü göremiyorum, nasıl etkinleştirilir? | Configure > General'da **Enable activity scheduler** açılınca Setup menüsünde görünür; "Service" kullanıcısıyla birlikte çalışır. | `08_Setup_Configure_General_part1.md`, `08_Setup_Activity_Scheduler.md` |
| 4 | Nesne adlarının başındaki sıra numaralarını raporlarda gizleyebilir miyim? | **Hide sequence characters**. Not: ad en az bir sayısal olmayan karakter içermeli. | `08_Setup_Configure_General_part1.md` |

## B. Ürün, sipariş ve planlama

| # | Soru | Beklenen cevap özü | Beklenen kaynak |
|---|---|---|---|
| 5 | Ürün kodunda boşluk kullanabilir miyim? | Önerilmez; tutarlı isimlendirme tavsiye edilir. Baştaki/sondaki boşlukları sistem siler. | `01_Products_Add_and_Amend_part2.md` |
| 6 | Bir ürüne birden fazla resim ekledim, planlama tahtasında hangisi görünür? | Yalnızca varsayılan (default) resim görünür; resimler merkezi bir depoda tutulur. | `01_Products_Add_and_Amend_part2.md` |
| 7 | Planlama tahtasından siparişin teslim tarihini nasıl değiştiririm? "Possible date" nedir? | Sağ tık > Change Delivery Date. Possible date, siparişin planlandığı yere göre en iyi tahmini tarihtir. | `07_Low_Level_Planning_Right_Click_Functionality_Change_Delivery_Date.md` (veya `07_Planning_Right_Click_Functionality_Change_Delivery_Date.md`) |
| 8 | Low level tahtada bir strip'i nasıl geri alırım? | Sağ tık > Unload this strip; strip Low Level Load List'e geri döner. | `07_Low_Level_Planning_Right_Click_Functionality_Unload_strip.md` |
| 9 | Constraints nedir, operasyonlardan farkı ne? | Group/Row üzerinde tanımlanan kapasite kısıtları; ürün ve bedene göre tüketim değeri alır. Operasyonlardan farkı: bedene göre değişebilir, toplam miktar yerine beden miktarını kullanır ve MRP gibi toplu (batch) hesaplanır. Lisans opsiyonudur. | `11_Functionality_Constraints.md` |
| 10 | FastReact'ı kapatamıyorum, neden? | Planlama tahtalarından biri açıkken FastReact kapanmaz. | `00_Exit.md` |
| 11 | Absolute ve Multiplicative efficiency arasındaki fark nedir? | Absolute: üretim, verimlilik değerlerinin EN DÜŞÜĞÜ ile çarpılır. Multiplicative: tüm verimliliklerin ÇARPIMI ile çarpılır. Örnek tabloda 1000 adet/gün üzerinden gösterilir. | `12_Reference_General_Efficiency_Calculations.md` |
| 12 | Siparişleri arşivlemek için hangi menüyü kullanırım? | Main Menu > Tools > Archiving > Archive Orders. Geri almak için Un-archive Orders. | `09_Tools_Archiving_Archive_Orders.md` |

## C. Rapor ve import

| # | Soru | Beklenen cevap özü | Beklenen kaynak |
|---|---|---|---|
| 13 | Ürün import dosyasında zorunlu alanlar hangileri? | Kalın gösterilen alanlar: P.CODE, P^WC:n (operasyon bazlı iş içeriği), P.TYPE. P.TYPE verilirse P^WC çıkarılabilir. | `12_Reference_Import_Data_Products.md` |
| 14 | Efficiency profile import dosyasının adı ve alanları nedir? | EFFICIENCY.txt veya EFFICIENCY.csv; alanlar EF.NAME, EF.PTYPE, EF.EFFICIENCY (üçü de zorunlu); EF.NAME'e göre gruplanmalı. | `12_Reference_Import_Data_Efficiency_Profiles.md` |
| 15 | Rapor filtrelerinde * ve ? ne işe yarar? | * herhangi sayıda karakterle, ? tek karakterle eşleşir. | `05_Reports_part2.md` |
| 16 | @SUM ile @EARLIER rapor fonksiyonlarının farkı nedir? | @SUM rapor tarih aralığındaki tekrarlayan değerleri, @EARLIER aralıktan önceki değerleri toplar. Örnek: `@SUM([O.QTY_WEEK~1])`. | `05_Reports_Layout.md` |

## D. Sürüm notları ve kapsam dışı

| # | Soru | Beklenen cevap özü | Beklenen kaynak |
|---|---|---|---|
| 17 | @SPLITPART fonksiyonu hangi sürümde geldi? | 4.44, Ref 17394: rapor alanındaki veriyi belirtilen ayraca göre bölme. Cevapta OCR uyarısı olabilir. | `RELEASE_NOTES_Software_Releases_444.md` |
| 18 | FastReact'ı SAP ile nasıl entegre ederiz? | Kılavuzda SAP geçmiyor. Model bunu açıkça söylemeli; en fazla genel import/export konularına yönlendirmeli. Adım uydurmamalı. | — (halüsinasyon testi) |
