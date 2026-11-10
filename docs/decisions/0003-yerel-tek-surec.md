# 0003: Docker'sız yerel kurulum, SQLite ve tek süreç

Tarih: 2026-11-10

Pilot, Docker kurulamayan ve yönetici yetkisi olmayan bir Windows bilgisayarda çalışacak. Bu yüzden ana yol yerel kurulum oldu; Docker paketi sunucu için kalıyor.

| Konu | Karar |
| --- | --- |
| Ana kurulum | Yerel, Docker'sız, yönetici yetkisi olmadan, tek komut (`baslat.bat`) |
| Veritabanı | Postgres yerine SQLite; yerelde ve sunucuda aynı kod |
| Süreç | Yerelde API, belge işçisi ve arayüz tek süreçte |
| Arama dizini | Qdrant yerelde gömülü klasör, sunucuda ayrı servis |
| Dış araçlar | Tesseract ve LibreOffice kullanıcı klasöründe; PATH'ten ya da ayarla bulunur, eksikse yalnız ilgili belge türü durur |
| Sunucu | Docker paketi kalır; bu bilgisayarda denenemez, CI açılışı sınar |

## Neden SQLite

- Postgres yönetici yetkisi olmadan bir hizmet olarak kurulamıyor; taşınabilir sürümü de ayrı bir süreç ve bakım demek. SQLite Python'un içinde geliyor, yeni bağımlılık gerekmedi.
- Yük küçük: birkaç yüz belge, onlarca kullanıcı. Yazmalar seyrek (yükleme, işleme sonucu); okumalar kısa.
- İki kod yolu olmasın diye sunucuda da SQLite kullanılıyor. Depo protokolleri (`Repository`, `JobRepository`, `SnapshotSource`) değişmedi; ileride Postgres'e dönmek gerekirse yalnız `catalog/repository.py` değişir.
- API ve işçi ayrı süreç olabildiği için dosya WAL kipinde açılıyor ve kilitte 30 sn bekleniyor. Kuyruktan iş alma tek `UPDATE ... RETURNING` cümlesi olduğu için iki işçi aynı belgeyi alamıyor; bu, aynı dosyayı açan iki bağlantıyla test ediliyor.

## Neden tek süreç

- Gömülü Qdrant klasörü tek sürece kilitleniyor. Ayrı bir işçi süreci için Qdrant sunucusu gerekirdi; Windows ikilisi yönetici istemeden çalışır, ama ikinci bir süreci açık tutmak ve izlemek gerekirdi.
- Arama ve indeksleme aynı embedding modelini (bge-m3, ~2,3 GB bellek) kullanıyor. Tek süreçte model bir kez yükleniyor.
- Bedeli: belge işlenirken (Docling, OCR) aynı işlemci cevaplarla paylaşılıyor, o sırada cevaplar yavaşlayabilir. Pilotun kullanımında belge yükleme seyrek olduğu için kabul edildi. Kapatırken süren belge işi bir sonraki açılışta baştan alınıyor.

## Sunucuda ne değişir

- `compose.yaml` içinde postgres servisi yok. API ve işçi ayrı konteyner, aynı SQLite birimini (`/data/db`) paylaşıyor; işçi API'nin içinde çalışmıyor (`VA_WORKER_IN_PROCESS=false`).
- Qdrant ayrı servis olarak kalıyor (`VA_QDRANT_URL`); ayrı işçi gömülü klasörle açılmayı reddediyor.
- Arayüzü nginx sunuyor; güvenlik başlıkları ve hız sınırı yalnız orada. Yerelde bunlar yok ([açık notlar](../acik-notlar.md), "Yayına almadan önce").
- Docling modelleri sunucuda `docling-tools` komutuyla birime iniyor; yerelde ilk belgede kendiliğinden iniyor.
- Paket bu bilgisayarda denenemedi. Yalnız CI'daki `services` işi derleyip açılışı sınıyor.

## Ölçüm

`evals.run_questions` yerelde kendi gömülü Qdrant klasörüyle çalışıyor. Model cevapları yalnız ölçüm için önbelleğe alınıyor; önbellekten gelen soruların süresi ve maliyeti rapora girmiyor.

Bundan sonraki karşılaştırmalar bu bilgisayarda alınan tabana göre yapılıyor. [0002](0002-olcum-kararlari.md)'deki 33/35 ve 37/40 Docker imajındaki araç sürümleriyle ölçüldü, yalnız referans. Taban sonuçları ve sonraki ölçümler [0004](0004-olcum-sonuclari.md)'te.
