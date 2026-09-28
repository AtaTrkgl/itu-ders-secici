# **İTÜ Kepler Ders Seçici**

![GitHub repo size](https://img.shields.io/github/repo-size/AtaTrkgl/itu-ders-secici)
![GitHub License](https://img.shields.io/github/license/AtaTrkgl/itu-ders-secici)
![GitHub Repo stars](https://img.shields.io/github/stars/AtaTrkgl/itu-ders-secici?style=flat)

Bu _repo_ sayesinde otomatik bir şekilde, önceden zamanlayarak ve _HTTP request_ kullanarak [İTÜ Kepler](https://obs.itu.edu.tr/ogrenci/) üzerinden ders seçebilirsiniz.

## Test Edilen Dönemler

![Tested](https://img.shields.io/badge/tested-2026%2F2027%20Güz%20Dönemi-green)

![Tested](https://img.shields.io/badge/tested-2025%2F2026%20Güz%20Dönemi-green)
![Tested](https://img.shields.io/badge/tested-2025%2F2026%20Bahar%20Dönemi-green)
![Tested](https://img.shields.io/badge/tested-2025%2F2026%20Yaz%20Dönemi-green)

![Tested](https://img.shields.io/badge/tested-2024%2F2025%20Güz%20Dönemi-green)
![Tested](https://img.shields.io/badge/tested-2024%2F2025%20Bahar%20Dönemi-green)
![Tested](https://img.shields.io/badge/tested-2024%2F2025%20Yaz%20Dönemi-green)

![Tested](https://img.shields.io/badge/tested-2023%2F2024%20Bahar%20Dönemi-green)
![Tested](https://img.shields.io/badge/tested-2023%2F2024%20Yaz%20Dönemi-green)

## Nasıl Kurulur ve Kullanılır

1. İlk olarak _repo_'yu bilgisayarınıza kurun. Aşağıdaki iki seçenekten istediğiniz ile indirebilirsiniz.
   - Bilgisayarınızda _Git_ kurulu ise aşağıdaki kod'u kullanın.

      ```bash
      git clone https://github.com/AtaTrkgl/itu-ders-secici.git
      ```

   - Manuel olarak indirmek için ise _GitHub_ sayfasındaki yeşil "Code" Tuşuna basın ve açılan pencereden "Download ZIP" tuşuna basın. Ardından indirdiğiniz _ZIP_ dosyasını sağ tıklayıp ayıklayın.
2. Kurulu değil ise _Python_ kurun. ([Detaylı bilgi](https://www.python.org/downloads/)). Kurulumda dikkat etmeniz gerekenler; ilk penceredeki _Add Python to PATH_ kutucuğunu ve _Optional Features_ bölümündeki _pip_ kutucuğunu tiklemeniz gerekiyor.
3. Gerekli paketleri kurmak için aşağıdaki komutu çalıştırın.  

   ```bash
   pip install -r requirements.txt
   ```

   Linux'ta `selenium-wire` kaynaklı bir sorun yaşarsanız [Linux'ta selenium-wire sorunları](#linuxta-selenium-wire-sorunları) bölümündeki alternatif kurulumu deneyebilirsiniz.

4. Daha sonra yapmanız gereken, gerekli bilgileri programa girmek. Bunun için kurulum sihirbazını kullanmanız önerilir fakat isterseniz manuel olarak da girebilirsiniz.
   > ⚠️ Program zamanlama için bilgisayarınızın lokal zamanını kullanmaktadır, eğer bilgisayarınız Türkiye saat diliminde değil ise, lokal zamanınıza göre ders seçimi saatini ve tarihini giriniz.
   
   > 💡 Kurulum sihirbazı, girilen CRN'lerin doğrulunu [ITU Helper SDK](https://github.com/itu-helper/sdk) ile kontrol etmektedir.

   - **[ÖNERİLEN] Kurulum Sihirbazı ile Kurulum:** Gerekli dosyaları oluşturmak için aşağıdaki kodu kullanarak kurulum sihirbazını çalıştırın, sürecin devamında ekrandaki adımları takip edin.

      ```bash
      python src/setup.py
      ```

   - **Manuel Kurulum:** _repo_'nun içinde `data` adında bir klasör oluşturup içerisine gerekli `config.json` adında bir dosya oluşturun. ardından, dosyanın içerisine, aşağıdaki yazıyı yapıştırın ve boşlukları doldurun.

      <details>
         <summary>config.json Şablonu</summary>

      ```json
      {
         "account":
         {
            "username": "{İTÜ KULLANICI ADINIZ}",
            "password": "{İTÜ ŞİFRENİZ}"
         },
         "time":
         {
            "year": {DERS SEÇİM ZAMANI - YIL},
            "month": {DERS SEÇİM ZAMANI - AY},
            "day": {DERS SEÇİM ZAMANI - GÜN},
            "hour": {DERS SEÇİM ZAMANI - SAAT},
            "minute": {DERS SEÇİM ZAMANI - DAKİKA}
         },
         "courses":
         {
            "crn": [{ALINACAK CRN'ler, virgülle ayırılmış şekilde}],
            "scrn": [{BIRAKILACAK CRN'ler, virgülle ayırılmış şekilde}]
         }
      }  
      ```

      </details>

      <details>
         <summary>Doldurulmuş config.json Örneği</summary>

      İsmail Koyuncu (<koyuncu@itu.edu.tr>) için, 10 Şubat 2025, 14:00 tarihinde, _21340_, _21311_ ve _21332_ CRN'li dersleri alıp, hiç bir dersi bırakmayacak `config.json` örneği:

      ```json
      {
         "account":
         {
            "username": "koyuncu",
            "password": "cokGucluSifre123"
         },
         "time":
         {
            "year": 2025,
            "month": 2,
            "day": 10,
            "hour": 14,
            "minute": 0
         },
         "courses":
         {
            "crn": [21340, 21311, 21332],
            "scrn": []
         }
      }  
      ```

      </details>

      <details>
         <summary>Yedek CRN Kullanımı</summary>

      Bir dersin kontenjanının dolması durumunda otomatik olarak yedek bir CRN denenmesini istiyorsanız, `"CRN:YEDEK_CRN"` formatını kullanabilirsiniz.

      Örneğin, _21345_ CRN'li dersin kontenjanı dolarsa _21346_ CRN'li dersin alınmasını istiyorsanız:

      ```json
      {
         "courses":
         {
            "crn": [21340, "21345:21346", 21332],
            "scrn": []
         }
      }  
      ```

      Bu örnekte:
      - _21340_ ve _21332_ normal şekilde alınmaya çalışılacak
      - _21345_ alınamazsa (kontenjan doluysa), otomatik olarak _21346_ denenecek

      </details>

   Yukarıdaki yöntemlerden herhangi birini tamamladığınız takdirde, dosya yapınız aşağıdaki gibi görünmeli.

   ```text
   .
   ├── data
   │   └── config.json
   ├── src
   │   ├── run.py
   │   ...
   ├── README.md
   └── requirements.txt
   ...
   ```

5. Programı başlatmak için aşağıdaki kodu çalıştırın.

   ```bash
   python src/run.py
   ```

6. Program çalışmaya başladığında, ders seçimi sonlanınca bilgisayarın kapatılıp kapatılmayacağı sorulacak, **\[E\]** harfine basmanız durumunda bilgisayar otomatik olarak kapatılacaktır. (NOT: Sadece Windows cihazlarda çalışır.)

## Linux'ta selenium-wire sorunları

Varsayılan kurulum `selenium-wire` kullanır. Linux dağıtımınızda bu paketle ilgili bir sorun yaşarsanız alternatif olarak `selenium-wire-lw` kullanmayı deneyebilirsiniz. Program sorunsuz çalışıyorsa bu değişikliği yapmanız gerekmez.

İki paket de aynı `seleniumwire` modülünün dosyalarını kullandığından birlikte kurulmamalıdır. Önce yukarıdaki normal paket kurulumunu tamamlayın. Ardından programı çalıştırdığınız Python ortamında (sanal ortam kullanıyorsanız onu etkinleştirerek) aşağıdaki komutları sırayla çalıştırın. İlk komut, daha önce iki paketi de kurmuş olmanız durumunda çakışan kurulumu temizler; bir paketin kurulu olmadığını belirten uyarı almanız normaldir.

```bash
python -m pip uninstall selenium-wire selenium-wire-lw
python -m pip install selenium-wire-lw==3.0.2
```

Kaldırma işlemi sırasında onay istendiğinde `y` yazıp Enter'a basın. Kodda değişiklik yapmanız gerekmez; kurulumun kalan adımlarına devam edebilirsiniz.

**Not:** Daha sonra `pip install -r requirements.txt` komutunu tekrar çalıştırırsanız `selenium-wire` yeniden kurulur. `selenium-wire-lw` kullanmaya devam etmek için yukarıdaki kaldırma ve kurma adımlarını tekrar uygulayın.

## Nasıl Çalışır / Program Akışı

1. `data` dosyasına girilen _input_ değerleri okunur.
2. Belirtirlen ders seçim zamanına `5` dakika kalana kadar beklenir.
3. [İTÜ OBS (Kepler)](https://obs.itu.edu.tr/ogrenci/) sitesi açılır ve `data/config.json` dosyasındaki bilgiler ile giriş yapılır.
4. Ders seçim zamanına `45` saniye kalana kadar beklenir.
5. Ders seçim zamanına `30` saniye kalana kadar, sitenin _Network_ sekmesinden ders seçimi için kullanılan _API Token_ durmadan alınır.
6. Ders seçimine `30` saniye kalması ile beraber, _API Token_ okunması durdurulur ve ders seçimi beklenilir.
7. Ders seçimi başlayana kadar, `0.1` saniyede (`src/run.py` dosyasındaki `DELAY_BETWEEN_TIME_CHECKS` değişkeninin değeri belirler.) bir ders seçim vaktinin gelip gelmediği kontrol edilir.

   > 💡 Eğer program test modunda çalıştırılırsa, bu aşamada sadece girilen vaktin gelmesi beklenir.

8. Ders seçiminin başlandığı algılandıktan `10` dakika (`src/run.py` dosyasındaki `SPAM_DUR` değişkeninin değeri belirler.) sonraya kadar; `3` saniye (`src/run.py` dosyasındaki `DELAY_BETWEEN_TRIES` değişkeninin değeri belirler.) aralıklarla ders seçimi için _HTTP request_ yollanır. Bu süreç, [İTÜ OBS (Kepler)](https://obs.itu.edu.tr/ogrenci/) arayüzüne durmadan CRN'lerin - `data/crn_list.txt` dosyasındaki sırayla - girilip onaylanması ile aynı sonucu yaratır fakat websitesi çökmelerine daha dayanıklıdır. Bü süreçte bütün işlemlerin başarılı olması durumda program otomatik olaran sonlandırılacaktır.
9.  Süreç boyuncaki eylemler loglanır ve `logs/logs.txt` dosyasına kaydedilir.
10. Program sonlanır ve programın başında onay verildiyse bilgisayar kapatılır.

## Nasıl Test Edilir

Bu programın en güzel tarafı, ders seçimi için [İTÜ OBS (Kepler)](https://obs.itu.edu.tr/ogrenci/) arayüzü yerine _HTTP request_ kullanmasıdır. Bu sayede, aktif bir ders seçim zamanı içinde değilken ve ders kayıt taslak da aktif değilken bile test edebilirsiniz.

Programı test modunda çalıştırmak için, aşağıdaki komutu çalıştırın:

```bash
python src/run.py -test
```

Ardından sonuçları [İTÜ OBS (Kepler) - Ders Kayıt İşlem Geçmişi](https://obs.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayitIslemGecmisi) sayfasından görebilirsiniz (Hata olarak aktif bir ders seçim zamanı içinde değilsiniz mesajını göreceksiniz).

## Geliştirme Planları

> Bu _repo_'ya katkıda bulunmak isterseniz aşağıdaki eklemeler ile başlayabilirsiniz 😊

- [x] ~~_API Token_ alınmasını durdurup, _HTTP request_ ile ders seçimine geçmek yerine; _API Token_ alınmasını farklı bir _thread_ üzerinde durmadan devam ettirerek başka bir _thread_ üzerinden de _HTTP request_ atarak hata ihtimali daha da indirilebilir.~~
- [x] ~~Kurulum sırasındaki `data` klasörü ve içindeki dosyaların oluşturulması için daha kullanıcı dostu bir arayüz geliştirilebilir.~~
- [x] ~~Ders seçimi için yollanan _HTTP request_'leri, önceden belirlenmiş bir süre boyunca _spam_'lamak yerine, _HTTP request_'in _return code_'una bakarak devam edilebilir. Derslerin hepsi seçilince otomatik durup seçilememesi durumunda sadece seçilemeyen dersleri almaya çalışmaya devam edebilir. Bu sayede ayrıca yedek CRN sistemi eklenebilir ve seçilemeyen ders yerine yedek CRN alınabilir.~~
- [x] ~~Yatay geçiş yapanların [İTÜ OBS (Kepler)](https://obs.itu.edu.tr/ogrenci/) giriş ekranında hangi bölümünü kullanacağını soran bir sayfa daha çıkıyor. Kod şu anda buna karşın hiç bir şey yapmıyor ve manuel olarak hızlıca seçilmediği sürece çalışmıyor. Bu ekranda otomatik olarak güncel bölümün seçilmesi eklenilebilir.~~
