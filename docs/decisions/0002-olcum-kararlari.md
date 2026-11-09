# 0002: Ölçümle verilen kararlar

Tarih: 2026-11-09. Ölçümler üretilmiş test setiyle yapıldı. Gerçek belgelerle yeniden denenecek konular [açık notlarda](../acik-notlar.md).

## Cevap modeli: `google/gemma-4-26b-a4b-it`

Yalnız veri saklamayan uçlar denendi. Geliştirme setinin 35 sorusu; süre cevabın tamamıdır.

| Model | Geçen | Yanlış değer | Ortanca süre | Maliyet (35 soru) |
| --- | --- | --- | --- | --- |
| Gemma 4 26B | 33 | 0 | 1,57 sn | 0,0068 $ |
| Qwen 3.6 35B | 31 | 0 | 3,14 sn | 0,0026 $ |
| DeepSeek V4.1 Flash | 31 | 1 | 1,05 sn | 0,0200 $ |
| Claude Haiku 5.5 | 31 | 1 | 1,20 sn | 0,0184 $ |
| Mistral Small 3.2 | 30 | 2 | 1,11 sn | 0,0050 $ |
| Qwen 3.8 27B | 27 | 1 | 0,68 sn | 0,0311 $ |
| Gemma 4 31B | 25 | 1 | 0,91 sn | 0,0144 $ |

Önce yanlış değer, sonra doğruluk, süre ve maliyet ölçüt alındı. İstem Gemma üzerinde ayarlandığı için karşılaştırma ona biraz avantaj sağlar. GPT-OSS 120B ve GLM 5.3 Flash isteklere cevap vermediği için ölçülemedi; Gemini 3.1 Flash Lite istemcinin ZDR denetiminden geçmedi.

## Son sınav

Hiç işlenmemiş yeni tohumlu set (`--seed 11`), sonucuna göre ayar yapılmadı: 40 sorudan 37'si geçti, doğrulanmış yanlış değer 0, gereksiz ret 1. Geçmeyenler: taranmış belgede etiket sorusu "bulunamadı" oldu, fotoğraftaki değer doğrulanamadı, model değişince beden yeniden soruldu.

İlk İK sorularını içeren eski set bütün ayar koşularında çalıştığı için görülmemiş sayılmadı.

## Tablo varyant denetimi (K9): eklenmedi

Son sınav dahil doğrulanmış yanlış değer çıkmadı. Eklenecek denetim gereksiz soru riski taşıyor. Gerçek tablolarda yanlış satır ya da sütun görülürse yeniden ele alınacak.

## Konuşma

- Yazıya çevirme: `elevenlabs/scribe-v2`. Beş sentetik cümlede `M beden`i doğru duyan tek aday.
- Seslendirme: `google/gemini-3.8-flash-lite-tts`. Kullanıcı dinleyerek seçti; ElevenLabs daha hızlı ama anlaşılırlığı daha düşük bulundu.
- Selamlaşma, envanter ve bekleme cümleleri sabit metindir; ses yalnız bunlar ve doğrulanan cümlelerden üretilir.
