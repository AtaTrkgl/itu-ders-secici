"""
İTÜ Ders Seçici - Kapsamlı Test Dosyası
API simülasyonu ile tüm hata kodları ve backup CRN özelliği test edilir.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# src klasörünü path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from request_manager import RequestManager


class MockResponse:
    """Simüle edilmiş API response"""
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = str(json_data) if not isinstance(json_data, str) else json_data
    
    def json(self):
        return self.json_data


class TestRequestManagerErrorCodes(unittest.TestCase):
    """Tüm hata kodlarını test eden sınıf"""
    
    def setUp(self):
        """Her test öncesi çalışır"""
        self.token = "test_token_12345"
        self.course_url = "https://obs.itu.edu.tr/api/ders-kayit/v21/"
        self.time_check_url = "https://obs.itu.edu.tr/api/ogrenci/Takvim/KayitZamaniKontrolu"
        self.backup_map = {"12345": "67890", "11111": "22222"}
        
        self.request_manager = RequestManager(
            self.token, 
            self.course_url, 
            self.time_check_url,
            self.backup_map
        )
    
    def _create_ecrn_response(self, crn: str, result_code: str) -> dict:
        """ecrn için API response oluşturur"""
        return {
            "ecrnResultList": [{"crn": crn, "resultCode": result_code}],
            "scrnResultList": []
        }
    
    def _create_scrn_response(self, crn: str, result_code: str) -> dict:
        """scrn için API response oluşturur"""
        return {
            "ecrnResultList": [],
            "scrnResultList": [{"crn": crn, "resultCode": result_code}]
        }

    # ==================== BAŞARILI KODLAR ====================
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_success_result(self, mock_logger, mock_post):
        """successResult - Başarılı işlem testi"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "successResult"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)  # Başarılı olduğu için listeden çıkmalı
        mock_logger.log.assert_any_call("CRN 12345 için işlem başarıyla tamamlandı.")
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_ekleme_islemi_basarili(self, mock_logger, mock_post):
        """Ekleme İşlemi Başarılı testi"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "Ekleme İşlemi Başarılı"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_silme_islemi_basarili(self, mock_logger, mock_post):
        """Silme İşlemi Başarılı testi"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [], "scrnResultList": [{"crn": "12345", "resultCode": "Silme İşlemi Başarılı"}]}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection([], ["12345"])
        
        self.assertNotIn("12345", scrn_list)

    # ==================== TEKRAR DENENEBİLİR HATALAR ====================
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val01_retry(self, mock_logger, mock_post):
        """VAL01 - Tekrar denenebilir hata"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "99999", "resultCode": "VAL01"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["99999"], [])
        
        self.assertIn("99999", crn_list)  # Tekrar denenmeli, listede kalmalı
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val02_kayit_zaman_engeli(self, mock_logger, mock_post):
        """VAL02 - Kayıt zaman engeli"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "99999", "resultCode": "VAL02"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["99999"], [])
        
        self.assertIn("99999", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val13_gecici_engel(self, mock_logger, mock_post):
        """VAL13 - Geçici engel"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "99999", "resultCode": "VAL13"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["99999"], [])
        
        self.assertIn("99999", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val14_sistem_yanit_vermiyor(self, mock_logger, mock_post):
        """VAL14 - Sistem geçici olarak yanıt vermiyor"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "99999", "resultCode": "VAL14"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["99999"], [])
        
        self.assertIn("99999", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val16_aktif_islem(self, mock_logger, mock_post):
        """VAL16 - Aktif işlem devam ediyor"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "99999", "resultCode": "VAL16"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["99999"], [])
        
        self.assertIn("99999", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val21_islem_hatasi(self, mock_logger, mock_post):
        """VAL21 - İşlem sırasında hata"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "99999", "resultCode": "VAL21"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["99999"], [])
        
        self.assertIn("99999", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_errload(self, mock_logger, mock_post):
        """ERRLoad - Sistem yanıt vermiyor"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "99999", "resultCode": "ERRLoad"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["99999"], [])
        
        self.assertIn("99999", crn_list)

    # ==================== KALICI HATALAR (Tekrar Denenmez) ====================
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val03_zaten_alindi(self, mock_logger, mock_post):
        """VAL03 - Ders zaten alınmış"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL03"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)  # Tekrar denenmemeli
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val04_ders_planinda_yok(self, mock_logger, mock_post):
        """VAL04 - Ders planında yok"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL04"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val05_kredi_siniri(self, mock_logger, mock_post):
        """VAL05 - Kredi sınırı aşıldı"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL05"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val07_aa_notu(self, mock_logger, mock_post):
        """VAL07 - AA notuyla geçilmiş"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL07"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val08_program_sarti(self, mock_logger, mock_post):
        """VAL08 - Program şartı sağlanmıyor"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL08"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val09_cakisma(self, mock_logger, mock_post):
        """VAL09 - Ders çakışması"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL09"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val10_kayitli_degil(self, mock_logger, mock_post):
        """VAL10 - Derse kayıtlı değil"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL10"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val11_onsart(self, mock_logger, mock_post):
        """VAL11 - Önşart sağlanmıyor"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL11"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val12_ders_acilmamis(self, mock_logger, mock_post):
        """VAL12 - Ders bu dönem açılmamış"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL12"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val15_max_crn(self, mock_logger, mock_post):
        """VAL15 - Maksimum 12 CRN sınırı"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL15"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val18_engellendi(self, mock_logger, mock_post):
        """VAL18 - CRN engellendi"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL18"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val19_onlisans(self, mock_logger, mock_post):
        """VAL19 - Önlisans dersi"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL19"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val20_tek_ders_birakma(self, mock_logger, mock_post):
        """VAL20 - Dönem başına 1 ders bırakma sınırı"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [], "scrnResultList": [{"crn": "12345", "resultCode": "VAL20"}]}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection([], ["12345"])
        
        self.assertNotIn("12345", scrn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_crn_not_found(self, mock_logger, mock_post):
        """CRNNotFound - CRN bulunamadı"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "CRNNotFound"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_crn_list_empty(self, mock_logger, mock_post):
        """CRNListEmpty - CRN listesi boş"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "CRNListEmpty"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        self.assertNotIn("12345", crn_list)


class TestBackupCRN(unittest.TestCase):
    """Yedek CRN özelliğini test eden sınıf"""
    
    def setUp(self):
        self.token = "test_token_12345"
        self.course_url = "https://obs.itu.edu.tr/api/ders-kayit/v21/"
        self.time_check_url = "https://obs.itu.edu.tr/api/ogrenci/Takvim/KayitZamaniKontrolu"
        self.backup_map = {"12345": "67890", "11111": "22222"}
        
        self.request_manager = RequestManager(
            self.token, 
            self.course_url, 
            self.time_check_url,
            self.backup_map
        )
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val06_kontenjan_yetersiz_with_backup(self, mock_logger, mock_post):
        """VAL06 - Kontenjan yetersiz, yedek CRN'ye geçiş"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL06"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        # Ana CRN listeden çıkmalı, yedek CRN eklenmeli
        self.assertNotIn("12345", crn_list)
        self.assertIn("67890", crn_list)
        self.assertEqual(self.request_manager.used_backups["12345"], "67890")
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_kontenjan_dolu_with_backup(self, mock_logger, mock_post):
        """Kontenjan Dolu - Yedek CRN'ye geçiş"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "11111", "resultCode": "Kontenjan Dolu"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["11111"], [])
        
        self.assertNotIn("11111", crn_list)
        self.assertIn("22222", crn_list)
        self.assertEqual(self.request_manager.used_backups["11111"], "22222")
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_val06_without_backup(self, mock_logger, mock_post):
        """VAL06 - Kontenjan yetersiz, yedek CRN yok - retry"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "99999", "resultCode": "VAL06"}], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["99999"], [])
        
        # Yedek olmadığı için listede kalmalı (retry)
        self.assertIn("99999", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_backup_crn_also_full(self, mock_logger, mock_post):
        """Yedek CRN de kontenjan dolu - ikinci retry"""
        # İlk çağrı: Ana CRN kontenjan dolu
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL06"}], "scrnResultList": []}')
        crn_list, _ = self.request_manager.request_course_selection(["12345"], [])
        
        # Yedek CRN'ye geçildi
        self.assertIn("67890", crn_list)
        
        # İkinci çağrı: Yedek CRN de kontenjan dolu
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "67890", "resultCode": "VAL06"}], "scrnResultList": []}')
        crn_list, _ = self.request_manager.request_course_selection(crn_list, [])
        
        # Yedek'in yedeği olmadığı için retry olarak kalmalı
        self.assertIn("67890", crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_multiple_crns_mixed_results(self, mock_logger, mock_post):
        """Birden fazla CRN - karışık sonuçlar"""
        response_data = {
            "ecrnResultList": [
                {"crn": "12345", "resultCode": "VAL06"},  # Yedek'e geç
                {"crn": "33333", "resultCode": "successResult"},  # Başarılı
                {"crn": "44444", "resultCode": "VAL09"}  # Çakışma - listeden çık
            ],
            "scrnResultList": []
        }
        mock_post.return_value = Mock(text=str(response_data).replace("'", '"'))
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345", "33333", "44444"], [])
        
        self.assertIn("67890", crn_list)  # Yedek eklendi
        self.assertNotIn("12345", crn_list)  # Ana çıktı
        self.assertNotIn("33333", crn_list)  # Başarılı, çıktı
        self.assertNotIn("44444", crn_list)  # Çakışma, çıktı


class TestUnknownErrorCodes(unittest.TestCase):
    """Bilinmeyen hata kodlarını test eden sınıf"""
    
    def setUp(self):
        self.request_manager = RequestManager(
            "test_token",
            "https://obs.itu.edu.tr/api/ders-kayit/v21/",
            "https://obs.itu.edu.tr/api/ogrenci/Takvim/KayitZamaniKontrolu",
            {}
        )
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_unknown_error_code_ecrn(self, mock_logger, mock_post):
        """Bilinmeyen hata kodu (ecrn) - KeyError olmamalı"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "VAL99"}], "scrnResultList": []}')
        
        # Bu çağrı KeyError vermemeli
        try:
            crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
            # Bilinmeyen kod için log kontrolü
            mock_logger.log.assert_any_call("CRN 12345 için bilinmeyen hata kodu: VAL99")
        except KeyError:
            self.fail("Bilinmeyen hata kodu KeyError verdi!")
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_unknown_error_code_scrn(self, mock_logger, mock_post):
        """Bilinmeyen hata kodu (scrn) - KeyError olmamalı"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [], "scrnResultList": [{"crn": "12345", "resultCode": "UNKNOWN_ERROR"}]}')
        
        try:
            crn_list, scrn_list = self.request_manager.request_course_selection([], ["12345"])
            mock_logger.log.assert_any_call("CRN 12345 için bilinmeyen hata kodu: UNKNOWN_ERROR")
        except KeyError:
            self.fail("Bilinmeyen hata kodu KeyError verdi!")
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_server_error_response(self, mock_logger, mock_post):
        """Sunucu hatası - Beklenmeyen response"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": "ServerError500"}], "scrnResultList": []}')
        
        try:
            crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        except KeyError:
            self.fail("Server error KeyError verdi!")
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_empty_result_code(self, mock_logger, mock_post):
        """Boş hata kodu"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [{"crn": "12345", "resultCode": ""}], "scrnResultList": []}')
        
        try:
            crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        except KeyError:
            self.fail("Boş hata kodu KeyError verdi!")


class TestTokenManagement(unittest.TestCase):
    """Token yönetimini test eden sınıf"""
    
    def test_static_token(self):
        """Statik token kullanımı"""
        rm = RequestManager(
            "static_token_123",
            "https://test.url",
            "https://test.url/time",
            {}
        )
        self.assertEqual(rm._get_current_token(), "static_token_123")
    
    def test_callable_token(self):
        """Callable token getter kullanımı"""
        token_getter = Mock(return_value="dynamic_token_456")
        rm = RequestManager(
            token_getter,
            "https://test.url",
            "https://test.url/time",
            {}
        )
        self.assertEqual(rm._get_current_token(), "dynamic_token_456")
        token_getter.assert_called_once()
    
    def test_token_changes(self):
        """Token değişikliği"""
        tokens = ["token1", "token2", "token3"]
        token_index = [0]
        
        def get_token():
            token = tokens[token_index[0]]
            token_index[0] = min(token_index[0] + 1, len(tokens) - 1)
            return token
        
        rm = RequestManager(get_token, "https://test.url", "https://test.url/time", {})
        
        self.assertEqual(rm._get_current_token(), "token1")
        self.assertEqual(rm._get_current_token(), "token2")
        self.assertEqual(rm._get_current_token(), "token3")


class TestTimeCheck(unittest.TestCase):
    """Zaman kontrolü testleri"""
    
    def setUp(self):
        self.request_manager = RequestManager(
            "test_token",
            "https://obs.itu.edu.tr/api/ders-kayit/v21/",
            "https://obs.itu.edu.tr/api/ogrenci/Takvim/KayitZamaniKontrolu",
            {}
        )
    
    @patch('request_manager.requests.get')
    @patch('request_manager.Logger')
    def test_time_check_kayit_olabilir(self, mock_logger, mock_get):
        """Kayıt olabilir durumu"""
        response_data = {
            "kayitZamanKontrolResult": {
                "ogrenciSinifaKayitOlabilir": True,
                "ogrenciSiniftanAyrilabilir": False
            }
        }
        mock_get.return_value = Mock(text=str(response_data).replace("'", '"').replace("True", "true").replace("False", "false"))
        
        result = self.request_manager.check_course_selection_time()
        self.assertTrue(result)
    
    @patch('request_manager.requests.get')
    @patch('request_manager.Logger')
    def test_time_check_ayrilabilir(self, mock_logger, mock_get):
        """Ayrılabilir durumu"""
        response_data = {
            "kayitZamanKontrolResult": {
                "ogrenciSinifaKayitOlabilir": False,
                "ogrenciSiniftanAyrilabilir": True
            }
        }
        mock_get.return_value = Mock(text=str(response_data).replace("'", '"').replace("True", "true").replace("False", "false"))
        
        result = self.request_manager.check_course_selection_time()
        self.assertTrue(result)
    
    @patch('request_manager.requests.get')
    @patch('request_manager.Logger')
    def test_time_check_kapali(self, mock_logger, mock_get):
        """Kayıt kapalı durumu"""
        response_data = {
            "kayitZamanKontrolResult": {
                "ogrenciSinifaKayitOlabilir": False,
                "ogrenciSiniftanAyrilabilir": False
            }
        }
        mock_get.return_value = Mock(text=str(response_data).replace("'", '"').replace("True", "true").replace("False", "false"))
        
        result = self.request_manager.check_course_selection_time()
        self.assertFalse(result)
    
    @patch('request_manager.requests.get')
    @patch('request_manager.Logger')
    def test_time_check_invalid_response(self, mock_logger, mock_get):
        """Geçersiz response"""
        mock_get.return_value = Mock(text='invalid json response')
        
        result = self.request_manager.check_course_selection_time()
        self.assertFalse(result)


class TestEdgeCases(unittest.TestCase):
    """Uç durumları test eden sınıf"""
    
    def setUp(self):
        self.request_manager = RequestManager(
            "test_token",
            "https://obs.itu.edu.tr/api/ders-kayit/v21/",
            "https://obs.itu.edu.tr/api/ogrenci/Takvim/KayitZamaniKontrolu",
            {"12345": "67890"}
        )
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_empty_crn_list(self, mock_logger, mock_post):
        """Boş CRN listesi"""
        mock_post.return_value = Mock(text='{"ecrnResultList": [], "scrnResultList": []}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection([], [])
        
        self.assertEqual(crn_list, [])
        self.assertEqual(scrn_list, [])
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_malformed_response(self, mock_logger, mock_post):
        """Bozuk JSON response"""
        mock_post.return_value = Mock(text='not a valid json')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], ["67890"])
        
        # Hata durumunda orijinal listeler korunmalı
        self.assertEqual(crn_list, ["12345"])
        self.assertEqual(scrn_list, ["67890"])
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_missing_result_lists(self, mock_logger, mock_post):
        """Eksik result listeleri"""
        mock_post.return_value = Mock(text='{"someOtherField": "value"}')
        
        crn_list, scrn_list = self.request_manager.request_course_selection(["12345"], [])
        
        # Hata durumunda orijinal listeler korunmalı
        self.assertEqual(crn_list, ["12345"])
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_null_backup_map(self, mock_logger, mock_post):
        """backup_map None olarak verildiğinde"""
        rm = RequestManager("token", "url", "time_url", None)
        self.assertEqual(rm.backup_map, {})


class TestStressScenarios(unittest.TestCase):
    """Stres testi senaryoları"""
    
    def setUp(self):
        # Çok sayıda yedek CRN tanımla
        self.backup_map = {str(i): str(i + 1000) for i in range(1, 101)}
        self.request_manager = RequestManager(
            "test_token",
            "https://obs.itu.edu.tr/api/ders-kayit/v21/",
            "https://obs.itu.edu.tr/api/ogrenci/Takvim/KayitZamaniKontrolu",
            self.backup_map
        )
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_all_crns_quota_full(self, mock_logger, mock_post):
        """Tüm CRN'ler kontenjan dolu"""
        crn_list = [str(i) for i in range(1, 11)]  # 10 CRN
        
        # Hepsi VAL06 dönsün
        result_list = [{"crn": crn, "resultCode": "VAL06"} for crn in crn_list]
        mock_post.return_value = Mock(text=str({"ecrnResultList": result_list, "scrnResultList": []}).replace("'", '"'))
        
        new_crn_list, _ = self.request_manager.request_course_selection(crn_list, [])
        
        # Tüm ana CRN'ler yedeğe geçmeli
        for i in range(1, 11):
            self.assertIn(str(i + 1000), new_crn_list)
            self.assertNotIn(str(i), new_crn_list)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_rapid_token_changes(self, mock_logger, mock_post):
        """Hızlı token değişimleri"""
        call_count = [0]
        
        def get_token():
            call_count[0] += 1
            return f"token_{call_count[0]}"
        
        rm = RequestManager(get_token, "url", "time_url", {})
        mock_post.return_value = Mock(text='{"ecrnResultList": [], "scrnResultList": []}')
        
        # 100 kez çağır
        for _ in range(100):
            rm.request_course_selection([], [])
        
        # Her çağrıda token alınmalı
        self.assertEqual(call_count[0], 100)
    
    @patch('request_manager.requests.post')
    @patch('request_manager.Logger')
    def test_mixed_error_codes_stress(self, mock_logger, mock_post):
        """Karışık hata kodları stres testi"""
        all_codes = [
            "successResult", "VAL01", "VAL02", "VAL03", "VAL04", "VAL05",
            "VAL06", "VAL07", "VAL08", "VAL09", "VAL10", "VAL11", "VAL12",
            "VAL13", "VAL14", "VAL15", "VAL16", "VAL18", "VAL19", "VAL20",
            "VAL21", "ERRLoad", "Kontenjan Dolu", "Ekleme İşlemi Başarılı",
            "Silme İşlemi Başarılı", "CRNNotFound", "CRNListEmpty",
            "UNKNOWN_CODE_1", "UNKNOWN_CODE_2"  # Bilinmeyen kodlar
        ]
        
        for i, code in enumerate(all_codes):
            mock_post.return_value = Mock(
                text=f'{{"ecrnResultList": [{{"crn": "{i}", "resultCode": "{code}"}}], "scrnResultList": []}}'
            )
            
            try:
                self.request_manager.request_course_selection([str(i)], [])
            except Exception as e:
                self.fail(f"Hata kodu '{code}' için exception: {e}")


if __name__ == "__main__":
    # Test sonuçlarını detaylı göster
    unittest.main(verbosity=2)
