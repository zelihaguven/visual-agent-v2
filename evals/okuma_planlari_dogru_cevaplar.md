# Doğru cevap tablosu (ölçümden önce; sayfa görüntülerinden elle)

Tür: M = metinli sayfa, K = karışık (metin katmanı + görsel/şekil), Y = metin katmanı yok/görsel ağırlıklı.
Değer kimliği: belge-sayfa-no. Her değer etiketiyle (bağıyla) birlikte doğru sayılır.

## Ölçüt (ölçümden önce yazıldı, sonra değişmez)
1. Her planda yanlış gösterilen değer sayısı tabandan fazla olamaz.
2. Metinli sayfalarda (QM s.7, 16, 34, 38) tabanda doğru gösterilen tek bir değer bile bir planda bozulamaz
   (yanlışa ya da gizliye dönemez).
3. Kural 1: değer, iki okuyucu uyuşmadıkça "gösterilen" sayılmaz.
Sınıflar: doğru gösterilen / yanlış gösterilen (yanlış karakter ya da yanlış etikete bağlı) / gizlenen doğru /
gizlenen yanlış / okunamayan (çıktıda yok).

## Quality Manual (4a484fff…)
Sayfa seçimi: metinli 7, 16, 34, 38 (taban doğruluğunun korunması; 16 ve 38 tablo); karışık 15 (görsel tablo),
29 (görsel tablo), 35 (şekil + not), 36 (akış şekli). Metin katmanı olmayan sayfa yok.

| Kimlik | S. | Tür | Etiket | Doğru değer |
|---|---|---|---|---|
| QM-7-1 | 7 | M | yeni tedarikçi kontrollü onboarding süresi | six month |
| QM-7-2 | 7 | M | Yellow Light: preferred'a geçiş | within the next 6-12 months |
| QM-7-3 | 7 | M | PTH yılda en az | five times a year |
| QM-7-4 | 7 | M | azaltma eşiği | 92% or higher, two consecutive quarters |
| QM-7-5 | 7 | M | azaltılmış sıklık | twice per year (total of three times) |
| QM-7-6 | 7 | M | PTH puanı | 4 points - Full Compliance (Green) |
| QM-15-1 | 15 | K | Defect Rate, Green | <=2.5% |
| QM-15-2 | 15 | K | Defect Rate, Yellow | 2.51-3.99% |
| QM-15-3 | 15 | K | Defect Rate, Red | >>4.0% |
| QM-15-4 | 15 | K | 1st Pass Rate, Green | >=96% |
| QM-15-5 | 15 | K | 1st Pass Rate, Yellow | 90-95.9% |
| QM-15-6 | 15 | K | 1st Pass Rate, Red | <<90% |
| QM-15-7 | 15 | K | OQL, Green | <=2.5% |
| QM-15-8 | 15 | K | SQL, Yellow | 2.51-3.99% |
| QM-15-9 | 15 | K | 2nd Quality Rate, Green | <=1% |
| QM-15-10 | 15 | K | 2nd Quality Rate, Yellow | 1.01-2.5% |
| QM-15-11 | 15 | K | Expense Offset, Yellow | $0.01-$5000.00 |
| QM-15-12 | 15 | K | Expense Offset, Red | >>$5000.00 |
| QM-16-1 | 16 | M | QA Scorecard ağırlığı: PTH audit scores | 10% |
| QM-16-2 | 16 | M | ağırlık: Field QA inspections (OQL) | 20% |
| QM-16-3 | 16 | M | ağırlık: UA distribution house inspections (SQL) | 20% |
| QM-16-4 | 16 | M | ağırlık: Customer Focus | 20% |
| QM-16-5 | 16 | M | PTH tablosu 95-100 | Score 5 |
| QM-16-6 | 16 | M | PTH tablosu 90-94.99 | Score 4 |
| QM-16-7 | 16 | M | PTH tablosu <75 | Score 0 |
| QM-16-8 | 16 | M | OQL/SQL tablosu 0-0.99 | Score 5 |
| QM-16-9 | 16 | M | OQL/SQL tablosu 1-1.99 | Score 4 |
| QM-16-10 | 16 | M | OQL/SQL tablosu >=5 | Score 0 |
| QM-16-11 | 16 | M | OQL/SQL tablosu N/A | Score 2.5 |
| QM-16-12 | 16 | M | Customer Complaint 0-2 | Score 5 |
| QM-16-13 | 16 | M | Customer Complaint 11+ | Score 0 |
| QM-16-14 | 16 | M | Customer Satisfaction 5+ | Score 0 |
| QM-16-15 | 16 | M | Lab Accreditation New Applicant | % 50, Score 3 |
| QM-29-1 | 29 | K | Lot 2-8 örneklem | 2 |
| QM-29-2 | 29 | K | Lot 151-280 örneklem | 13 |
| QM-29-3 | 29 | K | Lot 151-280, AQL 1.5 kabul/red | 0 / 1 |
| QM-29-4 | 29 | K | Lot 151-280, AQL 2.5 kabul/red | 1 / 2 |
| QM-29-5 | 29 | K | Lot 501-1200 örneklem | 32 |
| QM-29-6 | 29 | K | Lot 501-1200, AQL 1.5 kabul/red | 1 / 2 |
| QM-29-7 | 29 | K | Lot 501-1200, AQL 4.0 kabul/red | 3 / 4 |
| QM-29-8 | 29 | K | Lot 35001+ örneklem | 200 |
| QM-29-9 | 29 | K | Lot 35001+, AQL 2.5 kabul/red | 10 / 11 |
| QM-29-10 | 29 | K | Lot 35001+, AQL 4.0 kabul/red | 14 / 15 |
| QM-34-1 | 34 | M | algılanacak demir küre çapı | 1.0 mm |
| QM-34-2 | 34 | M | günlük kalibrasyon | four times (4X) |
| QM-34-3 | 34 | M | hassasiyet ayarı | 1.0 mm |
| QM-34-4 | 34 | M | hassasiyet aralığı | 1.0 mm – 1.2 mm |
| QM-34-5 | 34 | M | test noktası sayısı | 9 places |
| QM-35-1 | 35 | K | test kartı Bottom | 0mm |
| QM-35-2 | 35 | K | test kartı Middle | 40mm |
| QM-35-3 | 35 | K | test kartı Top | 80mm |
| QM-35-4 | 35 | K | şekil etiketi (orta sıra) | 40mm HEIGHT (LEFT/CENTER/RIGHT) |
| QM-35-5 | 35 | K | şekil başlığı | LOCATION ON CONVEYOR BELT; HEIGHT ABOVE CONVEYOR BELT |
| QM-36-1 | 36 | K | Figure 7-2 makine etiketleri | A, B |
| QM-36-2 | 36 | K | Figure 7-2 konum etiketleri | FACE DOWN, FACE UP |
| QM-36-3 | 36 | K | metin: art arda makine | two machines immediately consecutive, two different angles |
| QM-38-1 | 38 | M | Version 1.0 tarihi | 09/03/14 (Initial Release) |
| QM-38-2 | 38 | M | Version 1.1 tarihi | 09/30/14 |
| QM-38-3 | 38 | M | Version 2.0 tarihi | 8/25/15 |
| QM-38-4 | 38 | M | Heat Transfer Stretch test (v2.0 satırı, s.54, 5.10) | 30% (130% önceden yanlış yazılmış) |
| QM-38-5 | 38 | M | idari ücret (v2.0, 6.4) | $1.00pp outside Europe, $2.00pp inside Europe |

## Bold 3 Stripes (52db0f28…)
Sayfa seçimi: metinli 12 (metin katmanı var ama içerik tablo/şekilde); karışık 6, 13, 15, 16 (şekil + tablo +
yerleşim metni); metin katmanı yok 10, 21, 26. Gerekçe: ölçüler şekil ve tablolarda; s.16 bugün bozuk, s.21 bugün
hiç okunmuyor.

| Kimlik | S. | Tür | Etiket | Doğru değer |
|---|---|---|---|---|
| B-6-1 | 6 | K | Bold Pro (SS27+) | 72mm, all adults |
| B-6-2 | 6 | K | Bold Essential (SS27+) | 56mm, all adults + kids junior + little kids |
| B-6-3 | 6 | K | Bold Stripes | 48mm, Kids infants |
| B-6-4 | 6 | K | eski dönem | SS25 until FW26, 4 different 3S dimensions |
| B-6-5 | 6 | K | yeni dönem | SS27 onward, 3 different 3S dimensions |
| B-6-6 | 6 | K | şekil: 72mm şerit/boşluk | 18 / 9 |
| B-6-7 | 6 | K | şekil: 56mm şerit/boşluk | 14 / 7 |
| B-6-8 | 6 | K | şekil: 48mm şerit/boşluk | 12 / 6 |
| B-6-9 | 6 | K | şekil: eski Men Bold Essential | 64mm (16 / 8) |
| B-10-1 | 10 | Y | cut seam | No cut seams are allowed within visible 3S areas |
| B-10-2 | 10 | Y | SPI | 12 stitches per inch |
| B-10-3 | 10 | Y | stitch margin | 1mm - 2mm |
| B-12-1 | 12 | M | 48mm, 2 needle distance | 8mm -> 9mm |
| B-12-2 | 12 | M | 56mm, 2 needle distance | 10mm -> 11mm |
| B-12-3 | 12 | M | 64mm, 2 needle distance | 12mm -> 13mm (applicable until FW26) |
| B-12-4 | 12 | M | 72mm, 2 needle distance | 14mm -> 15mm |
| B-12-5 | 12 | M | stitch margin | 1mm - 2mm |
| B-13-1 | 13 | K | Suggestion#1 panel width | 68mm (48mm 3S, kenar 10) |
| B-13-2 | 13 | K | Suggestion#2 panel width | 74mm (48mm 3S, kenar 15) |
| B-13-3 | 13 | K | Suggestion#3 panel width | 74mm (64mm 3S, kenar 5; until FW26) |
| B-13-4 | 13 | K | Suggestion#4 panel width | 82mm (72mm 3S, kenar 5) |
| B-13-5 | 13 | K | Suggestion#5 panel width | 102mm (72mm 3S, kenar 15) |
| B-13-6 | 13 | K | birim notu | measurement unit … is "mm" |
| B-15-1 | 15 | K | omuz, kalıp, öne | 2 Stripes +1 Space toward front |
| B-15-2 | 15 | K | omuz, kalıp, arkaya | 1 Stripe +1 Space toward back from HPS |
| B-15-3 | 15 | K | düz serili, önde | 2 Stripes are visible on front |
| B-15-4 | 15 | K | not | 72 mm or 64mm width small size risk |
| B-15-5 | 15 | K | geçerlilik | BU Sportwear until FW26 |
| B-16-1 | 16 | K | başlık | 3S ON SHOULDER & SLEEVE (RAGLAN SLEEVE REFERENCE) |
| B-16-2 | 16 | K | raglan, kalıp, öne | 2 Stripes +2 Spaces toward front |
| B-16-3 | 16 | K | raglan, kalıp, arkaya | 1 Stripe toward back from HPS |
| B-16-4 | 16 | K | not | notch on HPS |
| B-21-1 | 21 | Y | Reinforcement riski | 18 mm/16 mm single stripe width bubbling/puckering |
| B-21-2 | 21 | Y | Trims selection (azaltma) | tapes or elastics → upfront alignment with CCDA |
| B-21-3 | 21 | Y | Color Block riski | color migration |
| B-21-4 | 21 | Y | Insert Block Panel azaltma | best fit insert panel width to avoid 4 stripes optic |
| B-26-1 | 26 | Y | Version | 1 |
| B-26-2 | 26 | Y | Author | Anna Tran, Eliza Gunadi |
| B-26-3 | 26 | Y | Approver | Gail Jones, Walter Waehlt |
| B-26-4 | 26 | Y | Date | Apr 9th, 2025 |

## Föy 6013448 (61a65ac8…), UA Rival Flc Hoodie
Seçim: 17 föy aynı şablonda (hepsinde Colorway Gallery + Labeled Images). Düzen modeliyle tam sayım ~2 saat
sürecekti (sayfa başına >25 sn), durduruldu. Yerine bugünkü parçalardan "az metinli sayfa" sayıldı: en yüksek
6013448 ve 6026412 (6'şar); 6013448 seçildi (en çok sayfa, 29; kapak, ölçü ve fark sayfaları önceden görüntüyle
denetlenmişti). Bütün sayfalar taramadır (Y). Sayfalar: 1 kapak formu, 6 fotoğraf sayfası, 13 çizim, 14 etiketli
çizim (dikiş talimatları; bugün okunmuyor), 16 BOM tablosu, 20 BOM tablosu, 24 POM ölçü tablosu (Absolute),
28 POM fark tablosu (Increment).

| Kimlik | S. | Tür | Etiket | Doğru değer |
|---|---|---|---|---|
| F-1-1 | 1 | Y | Sample Status | Fit Approved, Hold Sampling |
| F-1-2 | 1 | Y | Main Material # | KNT-222888 |
| F-1-3 | 1 | Y | Size Range | XS-4XL, SMT-4XLT |
| F-1-4 | 1 | Y | Actual Sizes | XS-4XLT |
| F-1-5 | 1 | Y | Season | FW27 |
| F-1-6 | 1 | Y | Sourcing Manager | Kiara Vincent |
| F-1-7 | 1 | Y | Lifecycle | Carryover |
| F-6-1 | 6 | Y | başlık hücresi | Comments-Prototype 1-US-JADECA |
| F-6-2 | 6 | Y | fotoğraf etiketleri | FRONT, SIDE, BACK |
| F-13-1 | 13 | Y | başlık | Draft-Sample 10/26/26, 8:43 AM |
| F-13-2 | 13 | Y | çizim etiketi | BW |
| F-14-1 | 14 | Y | genel dikiş | 514 ON ALL SEAMS UNLESS OTHERWISE NOTED |
| F-14-2 | 14 | Y | Hood crossover | 7/8" |
| F-14-3 | 14 | Y | Knotted drawcord tip | placed 1 1/4" from edge, *knot included* |
| F-14-4 | 14 | Y | Stitch eyelet drawcord exit | placed 1 1/4" from hood cross over |
| F-14-5 | 14 | Y | yaka çevresi dikiş | 1N 401, 1/4" from seam |
| F-14-6 | 14 | Y | cep ağzı | 1/4" 406, 3/4" from pocket opening |
| F-14-7 | 14 | Y | cep uçları | 1N 301, 1/8" from seam; 1/2" bartack |
| F-14-8 | 14 | Y | etek bandı | 2 ply band with fold at bottom edge, 301 join seam, 2N 406 straddle stitch |
| F-14-9 | 14 | Y | kapüşon dönüşü | 1/4" 2N 301 1" hem, clean finished |
| F-14-10 | 14 | Y | HPS–HPS | fabric/finished trim from HPS to HPS - 301 |
| F-16-1 | 16 | Y | KNT-222888 Qty / Usage | 1.5454 / MAIN BODY (SOLID) |
| F-16-2 | 16 | Y | KNT-222890 Qty / Usage | 0.1861 / HEM AND CUFFS (SOLID) |
| F-16-3 | 16 | Y | KNT-222890 içerik | 325.0g/98% Cotton, 2% Elastane |
| F-16-4 | 16 | Y | KNT-226129 Qty / Usage | 0.2102 / HOOD LINER AND NECKTAPE (SOLID) |
| F-16-5 | 16 | Y | 026 Castlerock, MAIN BODY (HEATHERS) | Bros BC09 265 |
| F-16-6 | 16 | Y | II-TR3011 Usage / Qty | BEHIND DRAWCORDS / 0.0300 |
| F-16-7 | 16 | Y | II-TR3011, 410 Midnight Navy | Black |
| F-20-1 | 20 | Y | ED-LKTAG1.75 ölçü | 1.75" W x 0.871" H |
| F-20-2 | 20 | Y | ED-LKTAG1.75 LEFT CHEST, 500 Misty Purple | Black 001 |
| F-20-3 | 20 | Y | HS-107788, 268 Sepia | Black (vendor color) |
| F-20-4 | 20 | Y | VID-905974 ölçü | 16mm x 32mm |
| F-20-5 | 20 | Y | St-908032 UPC sticker ölçü | 2.0697 in x 1.4 in |
| F-24-1 | 24 | Y | Chart Size Range | Apparel (XS-5XL) |
| F-24-2 | 24 | Y | Base Size / Tolerance | LG / KNIT 1 (K1) |
| F-24-3 | 24 | Y | Fit Reference | 1390274 & 6007591 - LOOSE/RELAXED FIT |
| F-24-4 | 24 | Y | BL005 MD / LG | 28 1/2 / 29 |
| F-24-5 | 24 | Y | AB030 XS / 5XL | 17 1/2 / 29 1/2 |
| F-24-6 | 24 | Y | AB050 LG | 20 1/4 |
| F-24-7 | 24 | Y | BW005 Tol(-) / XL | -1/2 / 26 1/2 |
| F-24-8 | 24 | Y | BW120 MD / LG | 22 3/8 / 23 7/8 |
| F-24-9 | 24 | Y | tablo notu | Units: Fractions of inches; Grade Rule Display: Absolute |
| F-28-1 | 28 | Y | SL095 LG (ilk satır / Tall) | 11 1/4 / 10 3/4 |
| F-28-2 | 28 | Y | SL100 LG / SM | 7 1/2 / -3/8 |
| F-28-3 | 28 | Y | NK005 LG / MD | 8 / -3/8 |
| F-28-4 | 28 | Y | NK041 LG | 24 |
| F-28-5 | 28 | Y | HD010 LG / XXL | 11 / 3/4 |
| F-28-6 | 28 | Y | PO270 LG / XXL | 9 / 1/2 |
| F-28-7 | 28 | Y | tablo notu | Grade Rule Display: Increment (değerler fark, ölçü değil) |

Toplam: QM 61, Bold 40, föy 52 değer.
