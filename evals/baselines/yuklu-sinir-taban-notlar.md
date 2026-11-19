# `yuklu-sinir-taban.json` için notlar

Taban dosyası ölçüldüğü gibi durur; düzeltilmez. Aşağıdakiler onu okurken bilinmesi gerekenler.

## C1 tabanda olduğundan iyi görünüyor (2026-11-17)

Soru: "6013448 modelinin numune durumu nedir?" Beklenen: "Fit Approved, Hold Sampling".
Tabanın üç koşusunda üçü de "bulunamadı" (güvenli) çıktı. Aynı soru aynı kodla (`main` @ `a7ec817`)
8 kez daha soruldu:

| Sonuç | Koşu | Sınıf |
|---|---|---|
| "Numune durumu Regional Fit \| Fit Approved, Hold Sampling: US." doğrulanmış gösterildi | 4 | yanlış |
| Bulunamadı | 2 | güvenli |
| Netleştirme | 2 | güvenli |

Yani bu soru bugünkü hatta koşuların yaklaşık yarısında yanlış gösteriliyor; üç koşu bunu yakalamadı.
Neden okuma tarafında: kapak formu parçaya "Sample Status: Regional Fit | Fit Approved, Hold
Sampling: US" diye geçiyor, model satırı birebir alıntılıyor, doğrulayıcı alıntıya sadık cümleyi
geçiriyor. Soru sette "okuma" etiketli.

Bu yüzden sınır setindeki ölçümler bundan sonra 5 koşu yapılır.

## Ölçüm nasıl yapılır (2026-11-19)

Uygulama açıkken (`python -m apps.local`), birkaç soruyla ısıtıldıktan sonra:

    python -m evals.sinir_seti --url http://127.0.0.1:8080 --runs 5 --output evals/output/sinir.jsonl

Betik kilitsiz soruları `/api/ask` yolundan sorar ve her cevabı (tür, gösterilen doğrulanmış cümleler, gizlenen cümle sayısı, netleştirme sorusu ve seçenekleri, ilk doğrulanmış cümleye kadar süre) bir satıra yazar; özette ilk doğrulanmış cümlenin ortancası ve p95'i var. Soru günlüğü özeti (`python -m apps.api.question_log`) de aynı p95 tanımını kullanır. Sınıflar (doğru / güvenli / yanlış) cevap metni okunarak elle verilir.
