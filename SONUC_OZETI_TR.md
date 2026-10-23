# GOP TOE temel sürüm sonuçları

**GOP_TOE_FOUNDATION_v1_0 / 1.0.0 üretildi. Durum FROZEN_LIMITED.** Kullanılabilir, denetlenebilir bir çekirdek var; istenen bütün kapsamın tamamlandığı iddia edilmiyor. Her şeyin teorisi hedefi korunuyor, doğruluğu kurulmuş değil.

## Formül ve değişiklik

Ana klasik yasa `dz_i=P_i(z,u)dt+Σ_a Q_ia(z)dW_a`. P ve Q açık katsayılı, en fazla ikinci derece yerel polinomlar. Fiziksel duruma, toplam derecesi 2–4 olan ve sayısı en fazla min(2d,16) ile sınırlanmış türetilmiş koordinatlar eklenebiliyor. Ölçüm, geri etki, iç kayıt, eylem ve sonlu gecikmeli iletişim aynı sıralı F2 sisteminin içinde. Kuantum ve mantık işlemleri açıkça dışarıdan alınmış kurallarla ekleniyor.

Somut skaler örnek: `ẋ=−ax−bxw`, `ẇ=−raw−rbw²`, `w(0)=x(0)^r`, `r=2 veya 4`. Bu, kübik/beşinci derece yasayı doğrudan üretir. Ana yasa yerine ayrı F0-P tahmincisi kullanılmadı. Eski tahminci yalnızca adı ayrı bir karşılaştırıcıdır.

## Desteklenen sınırlı sonuçlar

- Üç skaler yapı için 48 bağımsız nihai dünya ve 96 iç içe ölçüm tekrarı çalıştırıldı. Katsayılar her dünyadaki 32 erişilebilir reset ölçümünden kestirildi; gizli simülatör katsayıları kestirime verilmedi. Bu bilinen yapıda uyarlamadır, bilinmeyen doğa yasası keşfi değil.
- 1, 16, 64 adımlı F2 tahminleri kaydedildi; F2 taşması 0. Ortalama mutlak katsayı hataları yaklaşık 0,00109 ve 0,00643.
- Kuvvetli/sönümlü mekanik örnekte yörünge hatası 2,23×10⁻⁹ düzeyinde; iş-enerji hesabı yapılırken açık sistem yanlışlıkla korunumlu sayılmadı.
- Ayrı iç duruma sahip iki uç, sensörler, fiziksel geri etki, eylem, mesaj ve gecikme tamponları 128 adım yürütüldü. Bağlantı kesilince karşı uca müdahale etkisi 0. Gecikme 1'den 3'e çıkınca ilk etki 11'den 13. adıma kaydı.
- Sonlu kuantum kanal/ölçüm kontrolleri ile 200 sıralı kapı örneği ve 128 adımlı bit bileşimleri çalıştı. Bu bilinen yasaların uygulama tutarlılığıdır.

## Aleyhte veya başarısız bulgular

- `ẋ=−x−x⁷`, seçilen en fazla dördüncü derece monom dilbilgisiyle tam kapanamaz. En büyük üs M≤4 ise türevin derecesi M+6, izinli ikinci derece ifadeninki en fazla2M'dir. Bu sınırlı tam temsil iddiası çürütülmüştür; bütün olası gelecekteki teoriler değil.
- F2, geliştirmede seçilen güçlü karşılaştırıcılara karşı önceden belirlenen üstünlük marjını aşmadı. Üç karar da INCONCLUSIVE; bu eşdeğerlik veya başarı anlamına gelmez.
- Nominal %80 bütün-dünya belirsizlik kapsamı kübikte%75, beşinci derecede%68,75, lojistikte%93,75. Hazırlama değişimi alt grubunda ilk iki aile 0/4 kapsam verdi. Bunlar saklanmadı.
- Stokastik liftin Euler–Maruyama kısıt RMS'i en ince kayıtlı çözümde 0,001128; 1e−5 sayısal toleransını karşılamıyor. Tam Ito özdeşliğiyle sayısal yaklaşım ayrıldı; testten sonra çözünürlük artırılmadı.

## Çözümsüz ve çalıştırılmamış alanlar

Yeni bir Lorentz kovaryansı, dinamik metrik/Einstein limiti, kuantum alanı, bütün cihaz/rezervuarların fiziksel kapanışı veya insan anlamı/klinik fayda sonucu yok. S05 kaynak doyumu ve S07 tanh etkileşimi eşlenmedi; yeni merkezî kuvvet, ayrıntılı termodinamik yol ve azaltılmış kuantum bellek paketleri çalıştırılmadı. Önceki fizik yükümlülüklerinin tamamı sonuç çizelgesinde korunuyor.

## Denetim ve kullanım

23 yazılım testi geçti. 4.536 skaler metrik satırı kaydedilmiş tahminlerden yeniden hesaplandı; 260 tahmin/deney kaydı kaynak denklem, kod, katsayı ve gözlem sözleşmesine bağlı. Fizik izlerinin genel ufuk etiketleri çıktı-metaverisi düzeltmesiyle gerçek zaman/indeks anlamına çevrildi; eski kayıt ve hashleri korundu. Denklem, skor ve çekirdek değişmedi.

Çekirdek SHA256:
`cc99f94bd75a67c0035c8342ef3fdc4ba1d937a586bef2ede4354f1d829ce8b7`

Yeni çalışma eklemek için temel ZIP'in bir çalışma kopyasını açıp `integration/NEXT_STUDY_PROMPT_TR.txt` talimatını kullan. Gerçek komutlar `python -m gop_intake init/ingest/assess/verify/export` şeklinde. Yeni çalışma çekirdeği desteklemek zorunda değil; karşı örnek, sınırlama veya UNMAPPED kalabilir. Çekirdek değişikliği yalnızca ayrı revizyon önerisi oluşturur.

İngilizce makale, düzenlenebilir kaynaklar, matematik eki, tek sayfalık denklem kartı, kod, gerçek sentetik deneyler, denetim ve özgün girdiler paket içindedir. Bu çalışma yayımlanmadı; yazar incelemesi gerektirir. Yeni aday arama döngüsü bu sürümle kapatıldı.
