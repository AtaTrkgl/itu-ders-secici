# **İTÜ Kepler Ders Seçici**

Bu _repo_ sayesinde otomatik bir şekilde, önceden zamanlayarak ve _HTTP request_ kullanarak [İTÜ Kepler](https://kepler-beta.itu.edu.tr/ogrenci/) üzerinden ders seçebilirsiniz.

## Nasıl Kullanılır

1. İlk olarak yapmanız gereken `data` adında bir klasör oluşturup içerisine gerekli _input_ dosyalarını oluşturmak olacak.
   1. `data/creds.txt` dosyasına, birinci satıra itü hesap adınızı (itu e-posta adresinizin @itu.edu.tr kısmından önceki yeri), ikinci satıra da hesap şifrenizi girin. Örneğin İsmail Koyuncu (<koyuncu@itu.edu.tr>) iseniz:

        ```text
        koyuncu
        cokGucluSifre123
        ```

   2. `data/crn_list.txt` dosyasına, her satırda farklı bir CRN olacak şekilde almak istediğinizi CRN'leri girin. Örnek:

        ```text
        21340
        21311
        21332
        ```

   3. `data/time.txt` dosyasına ders seçiminizin ne zaman başlayacağını "`YIL AY GÜN SAAT DAKİKA`" formatında girin. Örneği _6 Şubat 2024 Saat:10:00_ için:

        ```text
        2024 2 6 10 0
        ```

2. Kurulu değil ise _Python_ kurun, proje kodlanırken _3.10.4_ sürümü kullanıldı. ([Detaylı bilgi](https://www.python.org/downloads/)).
3. Gerekli paketleri kurmak için aşağıdaki komutu çalıştırın.  

   ```console
   pip install -r requirements.txt
   ```

4. Programı başlatmak için aşağıdaki kodu çalıştırın, çalıştırmadan önce `data/time.txt` dosyasına girdiğinizi zamana 2 dakikadan fazla kaldığından emin olun. Aksi taktirde hata alacaksınız.

   ```console
   python src/run.py
   ```

5. Program çalışmaya başladığında, ders seçimi sonlanınca bilgisayarın kapatılıp kapatılmayacağı sorulacak, **\[E\]** harfine basmanız durumunda bilgisayar otomatik olarak kapatılacaktır. (NOT: Sadece Windows cihazlarda çalışır.)

## Nasıl Çalışır / Program Akışı

1. `data` dosyasına girilen _input_ değerleri okunur.
2. `data/time.txt` dosyasında belirtirlen ders seçim zamanına 2 dakika kalana kadar beklenir.
3. [İTÜ Kepler](https://kepler-beta.itu.edu.tr/ogrenci/) sitesi açılır ve `data/creds.txt` dosyasındaki bilgiler ile giriş yapılır.
4. Ders seçim zamanına 45 saniye kalana kadar beklenir.
5. Ders seçim zamanına 10 saniye kalana kadar, sitenin _Network_ sekmesinden ders seçimi için kullanılan _API Token_ durmadan alınır.
6. Ders seçimine 10 saniye kalması ile beraber, 0.05 saniye aralıklarla 300 kere ders seçimi için _HTTP request_ yollanır. Bu süreç, [İTÜ Kepler](https://kepler-beta.itu.edu.tr/ogrenci/) arayüzüne durmadan CRN'lerin - `data/crn_list.txt` dosyasındaki sırayla - girilip onaylanması ile aynı sonucu yaratır fakat websitesi çökmelerine daha dayanıklıdır.
7. Süreç boyuncaki eylemler loglanır ve `logs/logs.txt` dosyasına kaydedilir.
8. Program sonlanır.
