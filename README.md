# **İTÜ Kepler Ders Seçici**

![GitHub repo size](https://img.shields.io/github/repo-size/AtaTrkgl/itu-ders-secici)
![GitHub License](https://img.shields.io/github/license/AtaTrkgl/itu-ders-secici)
![GitHub Repo stars](https://img.shields.io/github/stars/AtaTrkgl/itu-ders-secici?style=flat)

Bu _repo_ sayesinde otomatik bir şekilde, önceden zamanlayarak ve _HTTP request_ kullanarak [İTÜ Kepler](https://obs.itu.edu.tr/ogrenci/) üzerinden ders seçebilirsiniz.

## Nasıl Kurulur ve Kullanılır

1. İlk olarak _repo_'yu bilgisayarınıza kurun. Aşağıdaki iki seçenekten istediğiniz ile indirebilirsiniz.
   - Bilgisayarınızda _Git_ kurulu ise aşağıdaki kod'u kullanın.

      ```console
      git clone https://github.com/AtaTrkgl/itu-ders-secici.git
      ```

   - Manuel olarak indirmek için ise _GitHub_ sayfasındaki yeşil "Code" Tuşuna basın ve açılan pencereden "Download ZIP" tuşuna basın. Ardından indirdiğiniz _ZIP_ dosyasını sağ tıklayıp ayıklayın.
2. Kurulu değil ise _Python_ kurun. ([Detaylı bilgi](https://www.python.org/downloads/)). Kurulumda dikkat etmeniz gerekenler; ilk penceredeki _Add Python to PATH_ kutucuğunu ve _Optional Features_ bölümündeki _pip_ kutucuğunu tiklemeniz gerekiyor.
3. Gerekli paketleri kurmak için aşağıdaki komutu çalıştırın.  

   ```console
   pip install -r requirements.txt
   ```

4. Daha sonra yapmanız gereken, gerekli bilgileri programa girmek. Bunun için aşağıdaki iki yöntemden istediğinizi kullanabilirsiniz.
   - Gerekli dosyaları oluşturmak için aşağıdaki kodu kullanarak kurulum sihirbazını çalıştırın, sürecin devamında ekrandaki adımları takip edin.

      ```console
      python src/setup.py
      ```

   - _repo_'nun içinde `data` adında bir klasör oluşturup içerisine gerekli _input_ dosyalarını oluşturmak olacak
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

     3. `data/time.txt` dosyasına ders seçiminizin ne zaman başlayacağını "`YIL AY GÜN SAAT DAKİKA`" formatında, girin. Örneği _6 Şubat 2024 Saat:10:00_ için:

          ```text
          2024 02 06 10 00
          ```

     4. **⚠️ Ders bırakmak istemiyorsanız, bu adımı atlayın.** Ders bırakmak için `data/scrn_list.txt` dosyasına, her satırda farklı bir CRN olacak şekilde **bırakmak** istediğinizi CRN'leri girin. Örnek:

          ```text
          10556
          10557
          ```

   Yukarıdaki adımlardan herhangi birini tamamladığınızda, dosya yapınız bu şekilde görünecek:

   ```text
   .
   ├── data
   │   ├── creds.txt
   │   ├── crn_list.txt
   │   └── time.txt
   ├── src
   │   ├── run.py
   │   ...
   ├── README.md
   └── requirements.txt
   ...
   ```

5. Programı başlatmak için aşağıdaki kodu çalıştırın, çalıştırmadan önce `data/time.txt` dosyasına girdiğinizi zamana 2 dakikadan fazla kaldığından emin olun. Aksi taktirde hata alacaksınız.

   ```console
   python src/run.py
   ```

6. Program çalışmaya başladığında, ders seçimi sonlanınca bilgisayarın kapatılıp kapatılmayacağı sorulacak, **\[E\]** harfine basmanız durumunda bilgisayar otomatik olarak kapatılacaktır. (NOT: Sadece Windows cihazlarda çalışır.)

## Nasıl Çalışır / Program Akışı

1. `data` dosyasına girilen _input_ değerleri okunur.
2. `data/time.txt` dosyasında belirtirlen ders seçim zamanına `2` dakika (Eğer kod yeterince önce çalıştırılmışsa `5` dakika) kalana kadar beklenir.
3. [İTÜ OBS (Kepler)](https://obs.itu.edu.tr/ogrenci/) sitesi açılır ve `data/creds.txt` dosyasındaki bilgiler ile giriş yapılır.
4. Ders seçim zamanına `45` saniye kalana kadar beklenir.
5. Ders seçim zamanına `30` saniye kalana kadar, sitenin _Network_ sekmesinden ders seçimi için kullanılan _API Token_ durmadan alınır.
6. Ders seçimine `30` saniye kalması ile beraber, _API Token_ okunması durdurulur ve ders seçimi beklenikir. Ders seçiminin başlangıçından `50` saniye (`src/run.py` dosyasındaki `SPAM_DUR` değişkeninin değeri belirler.) sonraya kadar; `3` saniye (`src/run.py` dosyasındaki `DELAY_BETWEEN_TRIES` değişkeninin değeri belirler.) aralıklarla ders seçimi için _HTTP request_ yollanır. Bu süreç, [İTÜ OBS (Kepler)](https://obs.itu.edu.tr/ogrenci/) arayüzüne durmadan CRN'lerin - `data/crn_list.txt` dosyasındaki sırayla - girilip onaylanması ile aynı sonucu yaratır fakat websitesi çökmelerine daha dayanıklıdır.
7. Süreç boyuncaki eylemler loglanır ve `logs/logs.txt` dosyasına kaydedilir.
8. Program sonlanır ve programın başında onay verildiyse bilgisayar kapatılır.

## Test Etmek

Bu programın en güzel tarafı, ders seçimi için [İTÜ OBS (Kepler)](https://obs.itu.edu.tr/ogrenci/) arayüzü yerine _HTTP request_ kullanmasıdır. Bu sayede, aktif bir ders seçim zamanı içinde değilken ve ders kayıt taslak da aktif değilken bile test edebilirsiniz.

`data/time.txt` dosyasında girdiğiniz ders kayıt zamanını test etmek için yakın bir zamana çekerek test edebilirsiniz ve sonuçları [İTÜ OBS (Kepler) - Ders Kayıt İşlem Geçmişi](https://obs.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayitIslemGecmisi) sayfasından görebilirsiniz (Hata olarak aktif bir ders seçim zamanı içinde değilsiniz mesajını göreceksiniz).

Burada tek dikkat etmeniz gereken şey, test için girdiğiniz zamanın şu andan 2 dakikadan ileride olması, aksi taktirda program akışının 1. kısmındaki _" ders seçim zamanına 2 dakika kalana kadar beklenir."_ kısmı hataya neden olacaktır.

## Geliştirme Planları

> Bu _repo_'ya katkıda bulunmak isterseniz aşağıdaki eklemeler ile başlayabilirsiniz 😊

- [ ] _API Token_ alınmasını durdurup, _HTTP request_ ile ders seçimine geçmek yerine; _API Token_ alınmasını farklı bir _thread_ üzerinde durmadan devam ettirerek başka bir _thread_ üzerinden de _HTTP request_ atarak hata ihtimali daha da indirilebilir.
- [ ] Kurulum sırasındaki `data` klasörü ve içindeki dosyaların oluşturulması için daha kullanıcı dostu bir arayüz geliştirilebilir. (`setup.py` ile buna benzer bir şey eklendi fakat hala bir arayüz eklenilebilir.)
- [ ] Ders seçimi için yollanan _HTTP request_'leri, önceden belirlenmiş bir süre boyunca _spam_'lamak yerine, _HTTP request_'in _return code_'una bakarak devam edilebilir. Derslerin hepsi seçilince otomatik durup seçilememesi durumunda sadece seçilemeyen dersleri almaya çalışmaya devam edebilir. Bu sayede ayrıca yedek CRN sistemi eklenebilir ve seçilemeyen ders yerine yedek CRN alınabilir.
- [ ] Yatay geçiş yapanların [İTÜ OBS (Kepler)](https://obs.itu.edu.tr/ogrenci/) giriş ekranında hangi bölümünü kullanacağını soran bir sayfa daha çıkıyor. Kod şu anda buna karşın hiç bir şey yapmıyor ve manuel olarak hızlıca seçilmediği sürece çalışmıyor. Bu ekranda otomatik olarak güncel bölümün seçilmesi eklenilebilir.
