# === IMPORTS ===
from driver_manager import DriverManager
from selenium.webdriver.common.by import By
from time import sleep
from logger import Logger

# === CONSTANTS ===
PAGE_LOAD_DELAY = 3
TOKEN_URL = "https://obs.itu.edu.tr/api/ogrenci/Takvim/KayitZamaniKontrolu"

# === CLASS DEFINITON ===
class TokenFetcher:
    def __init__(self, url: str, login: str, password: str) -> None:
        # Create a new instance of the chrome web driver
        self.driver = DriverManager.create_driver()
        self.url = url
        self.creds = [login, password]
        
    def start_driver(self) -> None:
        Logger.log("Kepler açılıyor...")
        self.driver.get(self.url)

        # Wait to see if the URL changes to the login page
        sleep(PAGE_LOAD_DELAY)
        if "girisv3.itu.edu.tr" not in self.driver.current_url: 
            Logger.log("Kepler'e giriş yapılmış, giriş yapma aşaması atlanıyor...")
            return
        
        # Login to the system
        Logger.log("Kepler'e giriş yapılıyor...")
        input_elements = self.driver.find_elements(By.TAG_NAME, "input")
        index = 0

        for element in input_elements:
            # Skip the hidden elements
            if element.get_attribute("type") == "hidden": 
                continue

            # Fill in the credentials.
            element.click()
            if index <= 1:
                element.send_keys(self.creds[index])
            index += 1
            sleep(.1)

        Logger.log("Kepler'e giriş yapıldı, ders seçim sitesine yönlendiriliyor...")
        self.driver.get(self.url)
        sleep(PAGE_LOAD_DELAY)

    def fetch_token(self) -> str:
        # if the url is not the target url, open the target url
        if self.url not in self.driver.current_url:
            Logger.log("Ders seçim sitesi açılıyor...")
            self.start_driver()

        Logger.log("API Token okunuyor...")
        self.driver.refresh()
        sleep(1)
        for request in self.driver.requests:
            # if There is a response and the request is from the token url
            if request.response and TOKEN_URL in request.url:
                token = request.headers["authorization"]
                return token
        return "ERROR"
