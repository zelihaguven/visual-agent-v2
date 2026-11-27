# Doğru cevap tablosu, ikinci set (ölçümden önce; sayfa görüntülerinden elle)

Tür: M = metinli sayfa, K = karışık (metin katmanı + görsel/şekil), Y = metin katmanı yok/görsel ağırlıklı.
Değer kimliği: belge-sayfa-no. Her değer etiketiyle (bağıyla) birlikte doğru sayılır.
Değerler yalnızca 1300 px sayfa görüntülerinden (küçük yazılar için 3-4x büyütülmüş kesitlerden) yazıldı;
parçalardan ya da metin katmanından değil. Birinci setin sayfaları kullanılmadı.

## Ölçüt (ölçümden önce yazıldı, sonra değişmez)
1. Her planda yanlış gösterilen değer sayısı tabandan fazla olamaz.
2. Metinli sayfalarda (QM s.8, 22, 28, 39, 41, 43) tabanda doğru gösterilen tek bir değer bile bir planda
   bozulamaz (yanlışa ya da gizliye dönemez).
3. Kural 1: değer, iki okuyucu uyuşmadıkça "gösterilen" sayılmaz.
Sınıflar: doğru gösterilen / yanlış gösterilen (yanlış karakter ya da yanlış etikete bağlı) / gizlenen doğru /
gizlenen yanlış / okunamayan (çıktıda yok).
Setin sayfaları: QM 8, 21, 22, 27, 28, 39, 41, 43; Bold 3 Stripes 4, 9, 11, 14, 17, 22, 23, 25; föy 6026412
1, 5, 6, 7, 8, 10, 13, 15.

Düzeltme notu (2026-11-27, commit a3f05a2): ölçüt 2'nin QM sayfa listesi birinci setten yanlışlıkla
kopyalanmıştı (QM s.7, 16, 34, 38); bu setin metinli QM sayfalarıyla (8, 22, 28, 39, 41, 43) düzeltildi. Aynı
commit'te bloğa yalnız bilgi olarak "Setin sayfaları" satırı eklendi. Değerlere dokunulmadı. Bold s.11 metinli (M)
işaretliydi, ölçüt 2'ye yazılmadı; ölçüt sonuç görüldükten sonra değiştirilmez. Sonradan bakıldı: taban 0 doğru,
A-q1 1 doğru, bozulan 0.

Not (ikinci set): Ölçüt 2'nin bu setteki karşılığı metinli QM sayfaları 8, 22, 28, 39, 41, 43'tür.

## Quality Manual (4a484fff…)
Sayfa seçimi: metinli 8 (puan/yüzde listesi), 22 (metin içinde sayılar), 28 (AQL düzeyleri), 39, 41, 43
(sürüm tablosu: tarih/sayfa/bölüm sütunları); karışık 21 (fotoğraf + şekil başlığı), 27 (çıkartma görseli +
şekil içi açıklama kutusu, kesirli ölçüler). inspect_pdf bütün QM sayfalarını "text" sayar; birinci setteki gibi
birden çok görsel kutusu olan sayfalar (21, 27) K, diğerleri M. Metin katmanı olmayan sayfa yok.

| Kimlik | S. | Tür | Etiket | Doğru değer |
|---|---|---|---|---|
| QM2-8-1 | 8 | M | PTH maddesi 3 points | Compliant on Most Items (Yellow) |
| QM2-8-2 | 8 | M | PTH maddesi 2 points | More Than One Area Out of Compliance (Orange) |
| QM2-8-3 | 8 | M | PTH maddesi 1 point | All Areas Out of Compliance (Red); mandatory photo & comment |
| QM2-8-4 | 8 | M | final PTH SCORE Green | (90%) – On Track |
| QM2-8-5 | 8 | M | final PTH SCORE Yellow | (80-89.9%) |
| QM2-8-6 | 8 | M | final PTH SCORE Red | (79.9%) |
| QM2-8-7 | 8 | M | 8D CAP gerektiren puan | 1 point (on the 4-point scale) |
| QM2-21-1 | 21 | K | iğne değişimi asgari sıklık | Once every 24 hours |
| QM2-21-2 | 21 | K | iğne değişimi diğer tetikleyiciler | Style change, Color change, Start of morning shift |
| QM2-21-3 | 21 | K | bölüm başlığı 5.4.2 | Needle Change Policy |
| QM2-21-4 | 21 | K | şekil başlığı | Figure 5-1: Example of splaying seams to check for needle holes |
| QM2-21-5 | 21 | K | bölüm 5.5 başlığı | Stage 5. Specifications |
| QM2-21-6 | 21 | K | On-Field/Uniform ölçüm oranı | must be measured 100% for critical (sayfa sonu; cümle s.22'de "measurements" ile sürer) |
| QM2-22-1 | 22 | M | bölüm 5.6 başlığı | Stage 6. Factory 100% Inspection |
| QM2-22-2 | 22 | M | final inspection için PO tamamlanma | 80%+ completed |
| QM2-22-3 | 22 | M | On-Field / IOF Purchase Group | 401 (On-Field), 201 (IOF) |
| QM2-22-4 | 22 | M | INTSQR gönderim süresi | no later than the 3rd business day of each month |
| QM2-22-5 | 22 | M | NOTE yürürlük tarihi | As of July 1, 2018 |
| QM2-22-6 | 22 | M | yeni fabrika eğitim süresi | 90 day training period |
| QM2-22-7 | 22 | M | onaysız sevkiyat sayılır | Free of Charge (FOC) |
| QM2-27-1 | 27 | K | polybag IRREGULAR çıkartması kaldırıldı | Effective October 2020 |
| QM2-27-2 | 27 | K | eski uygulama koli çıkartması ölçüsü | 2" x 4" rectangular sticker |
| QM2-27-3 | 27 | K | çıkartma kırmızı zemin rengi | Pantone color 199C |
| QM2-27-4 | 27 | K | ayakkabı ambalaj çıkartması ölçüsü | 1" round label or 1"x2" rectangular sticker |
| QM2-27-5 | 27 | K | "IRR" işaret ölçüsü (metin) | 1/2" x 3/4" |
| QM2-27-6 | 27 | K | şekil içi açıklama kutusu | Mark shoe with the letter "IRR" here. Dimensions should be 1/2 in. x 3/4 in |
| QM2-27-7 | 27 | K | şekil başlıkları | Figure 5-2: Irregular Sticker Example; Figure 5-3: Irregular Footwear Marking |
| QM2-27-8 | 27 | K | Note | Slides will not use this stamp |
| QM2-28-1 | 28 | M | 8D yöntemi yürürlük | Effective October 1, 2017 |
| QM2-28-2 | 28 | M | bölüm 5.11 başlığı | PIVOT 88 Nonconformity Report (NCR) and Field Initiated 8D RCA |
| QM2-28-3 | 28 | M | 8D RCA kayıt formu | Appendix H – 8D Root Cause Analysis Form |
| QM2-28-4 | 28 | M | DH denetim planı | AQL 4.0 Normal Single Plan |
| QM2-28-5 | 28 | M | Factory QA Final Inspection düzeyi | AQL Normal Level 1.5 |
| QM2-28-6 | 28 | M | Field QA düzeyi | AQL Normal Level 2.5 |
| QM2-28-7 | 28 | M | Distribution House QA düzeyi | Normal Level 4.0 |
| QM2-39-1 | 39 | M | B/C grade yetkisiz sevkiyat tek seferlik ücret | raised from $1000.00 to $2500.00 |
| QM2-39-2 | 39 | M | Version 2.1 satırı Date / Page# / Section | 12/15/15 / 26 / 6.4 |
| QM2-39-3 | 39 | M | NOCSAE AQL satırı Date / Page# / Section | 12/15/15 / 17 / 5.7 |
| QM2-39-4 | 39 | M | Version 3.0 tarihi | 09/30/16 |
| QM2-39-5 | 39 | M | Section 9.3 (Page# 45) | Footwear FFC/ESC/FSH forms RETIRED; Section15.0 and Appendix O |
| QM2-39-6 | 39 | M | Section 9.7 (Page# 48), MSQR | moved: UA Materials Manual 19.4 and Appendix D |
| QM2-39-7 | 39 | M | Section 9.8 (Page# 49), Mill Issue | moved: UA Materials Manual Section 19.5 and Appendix E |
| QM2-41-1 | 41 | M | Version 5. Date / Page# / Section | 07/01/2018 / 6 / 1 |
| QM2-41-2 | 41 | M | Section 3.1 (Page# 9) ürünler | belts, bags, shoes, apparel |
| QM2-41-3 | 41 | M | Section 3.2 (Page# 9) CFA süresi | 90 days post initial placement of purchase orders |
| QM2-41-4 | 41 | M | Section 5.4.1 Page# | 16 |
| QM2-41-5 | 41 | M | Pivot 88 kullanım ücreti | $.50 for each Inspection or Reinspection Report |
| QM2-41-6 | 41 | M | ücret faturalama | invoiced quarterly (non-merchandise expense offset) |
| QM2-41-7 | 41 | M | Section 9.15 Page# | 45 |
| QM2-43-1 | 43 | M | Version 7.0 Date / Page# / Section | 09/30/2019 / 21 / 5.9.1 |
| QM2-43-2 | 43 | M | Version 7.1 Date / Page# / Section | 9/2/2020 / 7 / 2.2 |
| QM2-43-3 | 43 | M | Version 7.2 Date / değişiklik | 10/1/2020 / Removed IRR/IRREGULAR sticker from App/Acc Polybags |
| QM2-43-4 | 43 | M | Version 7.4 tarihi; kaldırılan politika | 9/24/2021; Removed 2% purchase policy for B & C Grades |
| QM2-43-5 | 43 | M | Version 7.5 Date / Page# / Section | 11/29/2021 / 14-15 / 4.3 |
| QM2-43-6 | 43 | M | Version 7.6 Date / PTH asgari puan | 8/11/2022 / 92% minimum score |
| QM2-43-7 | 43 | M | Version 7.7 Date / Page# / Section | 1/18/2023 / 19 / 5.7 |
| QM2-43-8 | 43 | M | Version 7.9 Date / Page# / Section | 10/13/2023 / 17 / 4.3.4 |

## Bold 3 Stripes (52db0f28…)
Sayfa seçimi: metinli 11 (metin katmanı var, şekil etiketleri görselde); karışık 9 (fotoğraf etiketleri + alıntı),
14 ve 17 (yerleşim şeması + 2D kalıp + yerleşim metni); metin katmanı yok 4 (ikonlu kutular, üst simgeli tarih),
22 (kesim yönü şeması), 23 (altı fotoğraflı panel), 25 (ölçü aleti görseli, mm değerleri). Tür inspect_pdf'ten:
text = M, scanned = K, none = Y. 2, 3, 5, 7, 19, 24 içindekiler, 8 ve 20 yalnız başlık/fotoğraf, 18 s.17'nin
eşi, 27 Q&A sayfası olduğu için alınmadı.

| Kimlik | S. | Tür | Etiket | Doğru değer |
|---|---|---|---|---|
| B2-4-1 | 4 | Y | TIMELINES: Go lives | Apr 9th, 2025 |
| B2-4-2 | 4 | Y | USERS | adidas internal teams; All adidas T1 partners; All sample milestones in Development and bulk production |
| B2-4-3 | 4 | Y | OBJECTIVES (2. madde) | quality guideline for 3 stripes construction and workmanship requirement, consistent product quality across different T1s and COO |
| B2-4-4 | 4 | Y | EXPECTATION | Tier1s are responsible for implementing and maintaining expected requirement and standard (sample creation process and bulk production) |
| B2-9-1 | 9 | K | fotoğraf etiketleri (soldan sağa) | ACCEPTABLE, PUCKERING, BUBBLING, WAVY |
| B2-9-2 | 9 | K | onay işaretleri | ACCEPTABLE ✓; PUCKERING, BUBBLING, WAVY ✗ |
| B2-9-3 | 9 | K | alıntı üst satırı | STANDARD 28 |
| B2-9-4 | 9 | K | alıntı | "QUALITY IS WHAT TOOK ADIDAS TO THE TOP. AND ONLY QUALITY GUARANTEES OUR SUCCESS" |
| B2-9-5 | 9 | K | qualified 3S tanımı | meet the required measurements, clean appearance, free from bubbling, puckering, broken stitches |
| B2-9-6 | 9 | K | yıldızlı dipnot | Any visual aspect outside of these guidelines should be discussed and agreed between Tier 1 and BU |
| B2-11-1 | 11 | M | alt başlık | GENERAL WORKMANSHIP – NO SEE-THROUGH EFFECT |
| B2-11-2 | 11 | M | risk koşulu | Light-color stripes applied on top of dark color material → risk of see-through effect |
| B2-11-3 | 11 | M | If NO see-through effect | No overlap seam allowance needed |
| B2-11-4 | 11 | M | If found see-through effect | Make 3S seam allowance overlapped balance at both sides |
| B2-11-5 | 11 | M | tüketim notu | higher fabric consumption; define based on product value; visual/appearance alignment with CCDA |
| B2-11-6 | 11 | M | şekil etiketleri (sol / sağ kutu) | NO SEE-THROUGH ISSUE / SEE-THROUGH ISSUE; applicated stripe, shell, stitching |
| B2-14-1 | 14 | K | alt başlık | 3S PLACEMENT FOR TOP \| 3S ON SHOULDER & SLEEVE |
| B2-14-2 | 14 | K | kalıpta, öne | 2 Stripes +2 Spaces toward front |
| B2-14-3 | 14 | K | kalıpta, arkaya | 1 Stripe toward back from HPS |
| B2-14-4 | 14 | K | düz serili | 2 Stripes +2 Spaces are visible on front, 1 stripe is visible on back |
| B2-14-5 | 14 | K | yaka ribana dikişi | at HPS or positioned 2 cm from HPS toward back |
| B2-14-6 | 14 | K | omuz dikişi | always covered from middle stripe |
| B2-14-7 | 14 | K | şema etiketleri (yukarıdan aşağı) | BACK BODY; Stripe; HPS (kesikli çizgi, ilk şeridin alt kenarında); Space; Stripe; Space; Stripe; FRON BODY |
| B2-17-1 | 17 | K | alt başlık | 3S PLACEMENT FOR TOP \| 3S ON SIDESEAM |
| B2-17-2 | 17 | K | kalıpta, ön beden | 2 Stripes + 1 Space on front body |
| B2-17-3 | 17 | K | kalıpta, arka beden | 1 Stripe + 1 Space on back body |
| B2-17-4 | 17 | K | düz serili | 2 Stripes + 1 Space visible from front; 1 Stripe + 1 Space toward back |
| B2-17-5 | 17 | K | yan dikiş konumu | Keep adidas standard side seam position |
| B2-17-6 | 17 | K | şema etiketleri | SIDE SEAM; Space, Space; FRON BODY; BACK BODY |
| B2-22-1 | 22 | Y | başlık kutusu | CUTTING DIRECTION |
| B2-22-2 | 22 | Y | şema etiketleri | Grain, Bias, Straight, Selvage (iki kenarda) |
| B2-22-3 | 22 | Y | şema üst etiketi | FABRIC CUTTING DIRECTION |
| B2-22-4 | 22 | Y | cross-grain kesim | Avoid cross-grain cuts to prevent twisting and uneven tension |
| B2-22-5 | 22 | Y | Bias Cutting | enhance drape and reduce puckering, especially around curves areas |
| B2-22-6 | 22 | Y | şema altı not | Suggest to conduct a trial during development stage |
| B2-23-1 | 23 | Y | panel başlıkları | NEEDLE PLATE & GAUGES, FOLDERS, PRESSER FOOT, TENSION ROLLER, 3S PIPING FEEDER, EXTENSION BED |
| B2-23-2 | 23 | Y | FOLDERS | Short folder & same folder direction for all 3 pieces |
| B2-23-3 | 23 | Y | PRESSER FOOT | monitor the condition, thickness, and flatness of plastic plates |
| B2-23-4 | 23 | Y | TENSION ROLLER | roller and puller wide enough to cover all three stripes |
| B2-23-5 | 23 | Y | 3S PIPING FEEDER | piping feeder device with auto-release |
| B2-23-6 | 23 | Y | makine ayar kontrol listesi | part of changeover process, corrective action and daily maintenance |
| B2-25-1 | 25 | Y | marj etiketleri (soldan sağa) | 0< margin < 1mm; margin = 1mm; 1mm < margin < 2mm; margin = 2mm |
| B2-25-2 | 25 | Y | ölçü aleti yazısı (sağ üst görsel) | MEN / WOMEN / YOUTH (56mm) |
| B2-25-3 | 25 | Y | ölçü dizisi | 14-7-14-7-14 |
| B2-25-4 | 25 | Y | ölçü aleti etiketleri | FRONT, SIDE SEAM, HPS, BACK |
| B2-25-5 | 25 | Y | bant başlığı | CHECK STRIPE WIDTH, SPACING, SEAM ALLOWANCE IN ONE GO |
| B2-25-6 | 25 | Y | bağlantılar | Tutorial video.mp4; Tool Design file.pdf |
| B2-25-7 | 25 | Y | madde 3 | IT'S TIER 1 RESPONSIBILITY to define and develop the appropriate measuring tool |

## Föy 6026412 (119bde3c…), UA W Challenger Train Pant
Seçim: 6013448 dışındaki 16 föyün hepsi aynı şablonda ve inspect_pdf'e göre bütün sayfaları "none" (Y). 6026412
seçildi: istenen öncelikli föy; 16 sayfasının görüntüyle bakılan hepsinde şablonun bütün türleri var (kapak formu,
dört farklı etiketli çizim sayfası, 4 BOM sayfası, 2 Absolute + 2 Increment POM sayfası). Başka bir föyün
belirgin biçimde daha zengin olduğuna dair bir işaret görülmedi (sayfa sayısı 10-17, aynı şablon). Sayfalar: 1 kapak
formu, 5 etiketli çizim (dikiş talimatları, kesirler), 6 etiketli çizim (referans stil kodları), 7 kesit detayı
(kesirli dikiş ölçüleri), 8 harfli işaretli yerleşim (A/B/C), 10 BOM tablosu, 13 POM ölçü tablosu (Absolute),
15 POM fark tablosu (Increment). Bütün sayfalar taramadır (Y).

| Kimlik | S. | Tür | Etiket | Doğru değer |
|---|---|---|---|---|
| F2-1-1 | 1 | Y | Sample Status | Submit Prototype |
| F2-1-2 | 1 | Y | Supplier Request Round | Prototype 1 |
| F2-1-3 | 1 | Y | Main Material # | KNT-221845 |
| F2-1-4 | 1 | Y | Material Description | Challenger Track Suit- Training Bottoms- Circular Knit- Jersey- 28gg- 233gsm- 90Poly/10Elastane \| Wicking- Disperse Dye - Low Shed |
| F2-1-5 | 1 | Y | Size Range / Actual Sizes | XS-XXL(4) / XS-XXL |
| F2-1-6 | 1 | Y | Season / Fit Type | SS28 / Fitted |
| F2-1-7 | 1 | Y | Sourcing Class | Bottoms - Knit Pants |
| F2-5-1 | 5 | Y | genel dikiş (sol üst) | 514 ALL SEAMS THEN 1/8" 1N 401 TOPSTITCH UNLESS OTHERWISE NOTED |
| F2-5-2 | 5 | Y | drawcord iliği | DRAWCORD AT INTERIOR VERTICAL BUTTONHOLES SPACED 1" APART |
| F2-5-3 | 5 | Y | cep ağzı | 1/2"; FOLLOW UA STANDARD: ONSEAM/SIDE SEAM TOP POCKET OPENING |
| F2-5-4 | 5 | Y | ön paça | 1/4" 2N 406, 3/4" FROM EDGE, SINGLE TURNBACK |
| F2-5-5 | 5 | Y | arka paça (sağ alt) | 1/2" 1N 301; SEE STANDARDS FOR WOMEN'S ANKLE ZIP GUARD |
| F2-5-6 | 5 | Y | iç bacak | NO TOPSTITCH ON INSEAM |
| F2-5-7 | 5 | Y | ANGLED ZIPPER | STARTS FROM SIDE LEG - OPENS TOWARDS BACK LEG |
| F2-5-8 | 5 | Y | REFERENCE STYLE (kırmızı) | 1379598 FW24 BASE W CH TR PANT FOR FIT |
| F2-6-1 | 6 | Y | REFERENCE STYLE (sol üst, kırmızı) | 6004073 |
| F2-6-2 | 6 | Y | arka baldır biye | INSERTED SELF FABRIC 1/8" PIPING TO BACK CALF PANEL SEAM |
| F2-6-3 | 6 | Y | arka bacak panel şekli | FOLLOW REF STYLE: 6022328 (MEN'S THERMAL PANT) |
| F2-6-4 | 6 | Y | yan dikiş açısı | SIDE SEAM ANGLE TO FOLLOW REF STYLE: 6004073 |
| F2-6-5 | 6 | Y | görsel adı | Detail1 |
| F2-7-1 | 7 | Y | sol panel başlığı | FOLD OVER WAISTBAND W/ ENCASED ELASTIC |
| F2-7-2 | 7 | Y | üst dikiş | 1/4" 2N 401, 1/4" FROM TOP EDGE |
| F2-7-3 | 7 | Y | lastik yüksekliği (dikey ok) | 3/4" |
| F2-7-4 | 7 | Y | alt dikiş (sol panel) | 1/4" 2N 401 |
| F2-7-5 | 7 | Y | iç kat dikişi | 514 WAISTBAND INTERIOR PLY AND ELASTIC |
| F2-7-6 | 7 | Y | CROSS SECTIONAL VIEW etiketleri | 1/4" 2N 401 (üst ve alt), WAISTBAND INTERIOR, ELASTIC, 514, BODY EXTERIOR |
| F2-7-7 | 7 | Y | görsel adı | Detail2 |
| F2-8-1 | 8 | Y | işaret A | KNT-221845 - CHALLENGER |
| F2-8-2 | 8 | Y | işaret B | KNT-221845 - CHALLENGER |
| F2-8-3 | 8 | Y | işaret C | KNT-TBD - POCKET BAG |
| F2-8-4 | 8 | Y | C işaretinin çizim etiketi | POCKET BAGS |
| F2-8-5 | 8 | Y | görsel adı | Layout |
| F2-10-1 | 10 | Y | II-TR3011 Qty / Usage | 0.0000 / BUTTONHOLE INTERLINING |
| F2-10-2 | 10 | Y | II-TR3105 Usage | POCKET WELT, ANKLE ZIPPER WELT, ZIPPER GUARD |
| F2-10-3 | 10 | Y | El-102327 Qty / Usage | 0.9200 / PANT: ENCASED TO WAISTBAND |
| F2-10-4 | 10 | Y | El-102327 lastik eni | PAIHO-1.75 inch |
| F2-10-5 | 10 | Y | DC-100010_1 ölçü / Qty / Usage | 3/8 inch / 10mm; 1.4900 / INTERNAL WAISTBAND |
| F2-10-6 | 10 | Y | ZP-2774 Qty / Usage | 2.0000 / ANKLE ZIPS |
| F2-10-7 | 10 | Y | Pip-210083 tanım / Qty / Usage | 1/8" POLYESTER PIPING WITH 1/4" SA; 3.0500 / FORWARD SIDE SEAM |
| F2-13-1 | 13 | Y | Chart Size Range / Base Size | XXS-4XL / SM |
| F2-13-2 | 13 | Y | Tolerance / Grade Rule | KNIT 2 (K2) / Womens Bottoms - Alpha - 2024 |
| F2-13-3 | 13 | Y | Pattern Block | 1379598-CFAPP-X0Y0 |
| F2-13-4 | 13 | Y | WA025 SM / LG | 14 / 16 1/2 |
| F2-13-5 | 13 | Y | WA030 XXS / 4XL | 16 3/4 / 27 1/4 |
| F2-13-6 | 13 | Y | DE221 Tol(-) / Tol(+) / MD | -1 / 1 / 49 |
| F2-13-7 | 13 | Y | LG005 XS / MD | 10 7/8 / 12 1/8 |
| F2-13-8 | 13 | Y | LG040 Tol(-) / 3XL | -3/8 / 9 3/8 |
| F2-13-9 | 13 | Y | RS005 XL | 11 5/8 |
| F2-13-10 | 13 | Y | IO005 (bütün bedenler) | 27 3/4 |
| F2-15-1 | 15 | Y | WA025 MD / LG | 1 / 1 1/2 |
| F2-15-2 | 15 | Y | WA030 XXS | -1 |
| F2-15-3 | 15 | Y | DE221 LG | 3 |
| F2-15-4 | 15 | Y | HP020 XXS / SM | -1/4 / 5 1/2 |
| F2-15-5 | 15 | Y | LG005 MD / LG | 5/8 / 7/8 |
| F2-15-6 | 15 | Y | LG065 XXS / LG | -1/4 / 3/8 |
| F2-15-7 | 15 | Y | RS010 SM / LG | 15 / 5/8 |
| F2-15-8 | 15 | Y | PO345 MD / LG / XL | 1/4 / 0 / 1/4 |
| F2-15-9 | 15 | Y | tablo notu | Units: Fractions of inches; Grade Rule Display: Increment (SM sütunu ölçü, diğerleri fark) |

Toplam: QM 57, Bold 48, föy 58 değer (163). Türe göre: M 49, K 33, Y 81. (Satırlar betikle sayıldı.)
