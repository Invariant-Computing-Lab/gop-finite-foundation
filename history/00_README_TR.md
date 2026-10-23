# Astra için nihai temel sürüm komut paketi

**Komut sürümü:** v2.0  
**Hedef çıktı:** GOP_TOE_FOUNDATION_v1_0  
**Paket türü:** Yürütme talimatı ve kaynaklar; yeni bilimsel sonuç veya bitmiş F2 değildir.

## Kullanım

Bu ZIP'i Astra'ya yükle ve `02_START_TR.txt` içeriğini gönder. Önceki sonuç arşivi,
denetim dosyaları, kavramsal makale ve eski talimatlar `inputs/` içine aynen
kopyalandı. Ayrı ayrı yeniden yüklemek gerekmez.

Ana İngilizce sözleşme `01_MASTER_EXECUTION_EN.md`. Kapanış kuralları
`RELEASE_AND_STOP_RULES.md`, sonraki çalışmalardan beslenme kuralları
`INTEGRATION_CONTRACT.md` içinde. Yeni talimatlarla tarihsel kaynakların ayrımı
`SOURCE_MAP.md` içinde. Girdi dosyalarının ad ve hash eşlemeleri
`INPUT_MANIFEST.json` içinde.

## “Nihai” ne demek?

Bu temel sürümün denklemi, kodu, iddiaları ve değerlendirmesi belirli bir sürüm
olarak kapanacak. Başarısız sonuçlar saklanmayacak. Evrensel teori iddiası
korunacak ama doğrulanmış kabul edilmeyecek. Ana adayın her eksikliğinde
otomatik yeni formül ve sınırsız deney döngüsü başlamayacak.

Temel bilimsel sorun, ana jeneratörle sınanan tahmincinin birbirinden kopuk
olmasıydı. Bu turda tahminleri gerçek aday denklem üretmeli. F0-P yalnızca
kendi adıyla karşılaştırıcı olarak kalabilir.

## Sonraki çalışmalar

Temel sürüm gerçekten üretildikten sonra `03_ADD_FUTURE_STUDY_TR.txt` kullanılır.
Temel ZIP + yeni kaynaklar birlikte verilir. Kaynaklar ilgili iddialara ve dört
programdan birine gerekçeli biçimde bağlanır. Kanıt, karşı örnek, kısıt, adapter
veya gerekçeli çekirdek-revizyon talebi oluşabilir. Orijinal çekirdek değiştirilmez;
yeni bulgunun çekirdeği zayıflatmasına veya yanlışlamasına izin verilir.

`04_RESUME_TR.txt` yalnızca kesinti içindir; tamamlanmış çalışmayı yeniden
başlatmaz. Gelecekteki veri ekleme komutu da temeli baştan kurma izni değildir.

## Bu pakette şimdi gerçekten bulunanlar

Komutlar, kaynakların değişmemiş kopyaları, JSON Schema ve boş şablonlar,
checksum dosyası ve standart Python ile çalışan paket bütünlük denetleyicisi.
Astra'nın geliştireceği F2 kodu ve gop_intake arayüzü henüz burada yok.
Şablonlardaki değerler veri veya deney sonucu değildir; `template_only=true`
kaydı gerçek kanıt olarak içeri alınamaz.

Paket kökünde byte bütünlüğünü denetlemek için:

```bash
python tools/verify_package.py --root .
```

Bu kontrol bilimsel doğruluğu değerlendirmez, iç arşivleri çalıştırmaz, ağa çıkmaz
ve önceki modellerin pickle dosyalarını yüklemez. Kaynakların SHA-256 eşleşmesini
ve paket dosyalarının mevcut olup olmadığını denetler.
