import requests
import json
from typing import Callable, Optional, cast
from logger import Logger

class RequestManager:

    # Source: https://github.com/MustafaKrc/ITU-CRN-Picker/blob/ffb2ca20c197092f54ade466439d890cd61acab6/core/crn_picker.py#L31
    codes_to_try_again = [  # The codes that indicate the operation was not successful but can be tried again.
        "VAL01",
        "VAL02",
        "VAL06",
        "VAL13",
        "VAL14",
        "VAL16",
        "ERRLoad",
        "NULLParam-CheckOgrenciKayitZamaniKontrolu",

        # Below are the codes that are not in the original source code.
        "Kontenjan Dolu",
        "VAL21",
    ]
    return_values = {
        "successResult": "CRN {} için işlem başarıyla tamamlandı.",
        "errorResult": "CRN {} için Operasyon tamamlanamadı.",
        None: "CRN {} için Operasyon tamamlanamadı.",
        "error": "CRN {} için bir hata meydana geldi.",
        "VAL01": "CRN {} bir problemden dolayı alınamadı.",
        "VAL02": "CRN {} kayıt zaman engelinden dolayı alınamadı.",
        "VAL03": "CRN {} bu dönem zaten alındığından dolayı tekrar alınamadı.",
        "VAL04": "CRN {} ders planında yer almadığından dolayı alınamadı.",
        "VAL05": "CRN {} dönemlik maksimum kredi sınırını aştığından dolayı alınamadı.",
        "VAL06": "CRN {} kontenjan yetersizliğinden dolayı alınamadı.",
        "VAL07": "CRN {} daha önce AA notuyla verildiğinden dolayı alınamadı.",
        "VAL08": "CRN {} program şartını sağlamadığından dolayı alınamadı.",
        "VAL09": "CRN {} başka bir dersle çakıştığından dolayı alınamadı.",
        "VAL10": "CRN {} dersine kayıtlı olmadığınızdan dolayı hiç bir işlem yapılmadı.",
        "VAL11": "CRN {} önşartlardan dolayı alınamadı.",
        "VAL12": "CRN {} şu anki dönemde açılmadığından dolayı alınamadı.",
        "VAL13": "CRN {} geçici olarak engellenmiş olması sebebiyle alınamadı.",
        "VAL14": "Sistem geçici olarak yanıt vermiyor.",
        "VAL15": "Maksimum 12 CRN alabilirsiniz.",
        "VAL16": "Aktif bir işleminiz devam ettiğinden dolayı işlem yapılamadı.",
        "VAL18": "CRN {} engellendğinden dolayı alınamadı.",
        "VAL19": "CRN {} önlisans dersi olduğundan dolayı alınamadı.",
        "VAL20": "Dönem başına sadece 1 ders bırakabilirsiniz.",
        "CRNListEmpty": "CRN {} listesi boş göründüğünden alınamadı.",
        "CRNNotFound": "CRN {} bulunamadığından dolayı alınamadı.",
        "ERRLoad": "Sistem geçici olarak yanıt vermiyor.",
        "NULLParam-CheckOgrenciKayitZamaniKontrolu" : "CRN {} kayıt zaman engelinden dolayı alınamadı.",
        "Ekleme İşlemi Başarılı" : "CRN {} için ekleme işlemi başarıyla tamamlandı.",

        # Below are the codes that are not in the original source code.
        "Kontenjan Dolu" : "CRN {} için kontenjan dolu olduğundan dolayı alınamadı.",
        "Silme İşlemi Başarılı" : "CRN {} için silme işlemi başarıyla tamamlandı.",
        "VAL21": "İşlem sırasında bir hata oluştu.",
        "VAL22": "CRN {} daha önce CC ve üstü harf notu ile verildiği için yükseltmeye alınamaz."
    }

    def __init__(self, token: str | Callable[[], str], course_selection_url: str, course_time_check_url: str) -> None:
        """
        Args:
            token: String token or callable token getter function
            course_selection_url: Course selection API URL
            course_time_check_url: Time check API URL
        """
        self._token: str | Callable[[], str] = token
        self._token_getter: Optional[Callable[[], str]] = token if callable(token) else None
        self.course_selection_url = course_selection_url
        self.course_time_check_url = course_time_check_url

    def _get_current_token(self) -> str:
        """Returns the current token."""
        if self._token_getter:
            return self._token_getter()
        return cast(str, self._token)

    def _get_headers(self) -> dict[str, str]:
        return {
            'Authorization': self._get_current_token(),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
        }

    def check_course_selection_time(self) -> bool:
        response = requests.get(self.course_time_check_url, headers=self._get_headers())
        Logger.log(f"Zaman kontrol request response mesajı: {response.text}", silent=True)

        try:
            result_json = json.loads(response.text)
            enrollment_data = result_json["kayitZamanKontrolResult"]
            return enrollment_data["ogrenciSinifaKayitOlabilir"] or enrollment_data["ogrenciSiniftanAyrilabilir"]
            
        except Exception:
            return False

    def request_course_selection(self, crn_list: list[str], scrn_list: list[str]) -> tuple[list[str], list[str]]:
        # Send the request to the server.
        response = requests.post(self.course_selection_url, headers=self._get_headers(), json={"ECRN": crn_list, "SCRN": scrn_list})
        Logger.log(f"Ders Seçim request response mesajı: {response.text}", silent=True)
        
        try:
            result_json = json.loads(response.text)

            # Log the results of crn_list and determine if it is to be retried.
            for crn_result in result_json["ecrnResultList"]:
                crn = crn_result["crn"]
                result_code = crn_result["resultCode"]

                Logger.log(RequestManager.return_values[result_code].format(crn))
                if result_code in RequestManager.codes_to_try_again:
                    Logger.log(f"CRN {crn} tekrar denenecek...")
                else:
                    crn_list.remove(crn)


            # Log the results of scrn_list and determine if it is to be retried.
            for scrn_result in result_json["scrnResultList"]:
                crn = scrn_result["crn"]
                result_code = scrn_result["resultCode"]

                Logger.log(RequestManager.return_values[result_code].format(crn))
                if result_code in RequestManager.codes_to_try_again:
                    Logger.log(f"CRN {crn} tekrar denenecek...")
                else:
                    scrn_list.remove(crn)


            return crn_list, scrn_list
        except Exception as e:
            Logger.log(f"CRN listesi işlenirken bir hata meydana geldi: {e}", silent=True)
            return crn_list, scrn_list
