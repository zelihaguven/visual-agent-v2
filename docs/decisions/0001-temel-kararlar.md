# 0001: Yeni sürümün temel kararları

Tarih: 2026-11-08

Bu repo, eski `visual_agent` pilotunun yerine temiz yapıyla yazılan sürümdür. Eski repo olduğu gibi durur; kod ve ölçüm sonuçları oradan okunabilir.

| Konu | Karar |
| --- | --- |
| Kapsam | Herkesin önceden yüklenmiş belgelere soru sorduğu genel araç |
| İlk kullanım | Önce SQL aracı kullanan uzmanlar ve iş analistleri, sonra dikim departmanı |
| Arayüz | Tablet ve bilgisayara uyumlu web |
| Giriş | İlk sürümde kapalı; Microsoft girişi ve departmanlar sonra eklenir |
| Cevap modeli | OpenRouter üzerinden, ZDR zorunlu, 8 kaynak. Başlangıç Gemma 4 26B; seçim yeni test setinde verimlilik ve maliyete göre yapılır |
| Arama | Yerel bge-m3, BM25, RRF; reranker yok |
| Kurallar | Yalnız her belgede geçerli ana kurallar; belgeye özel elle yazılmış kural yok |
| Doğrulama | Sayı, kod ve teknik ad, cümlenin kendi alıntısında birebir geçer |
| Komutlar | Belgedeki komut aynen gösterilir; sistem yerleştirmez, değiştirmez, çalıştırmaz |
| Ses | Anlık işlenir, saklanmaz; sağlayıcıda veri saklamama aranır |
| Test belgeleri | Gerçekleri baştan bilinen, kontrollü üretilmiş belgeler |
| PDF işleme | Docling ve pypdfium2; AGPL lisanslı PyMuPDF kullanılmaz |
| Ağır araçlar | LibreOffice, Tesseract ve Docling yalnız işçi imajında; belgeler internetsiz işlenir |
| OCR güvenliği | İki okumada uyuşmayan değer belirsiz işaretlenir ve doğrulanmış gösterilmez |
