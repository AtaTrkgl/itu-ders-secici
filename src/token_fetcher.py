# === IMPORTS ===
from driver_manager import DriverManager
from selenium.webdriver.common.by import By
from time import sleep
from logger import Logger
import threading

# === CONSTANTS ===
PAGE_LOAD_DELAY = 3
TOKEN_URL = "https://obs.itu.edu.tr/api/ogrenci/Takvim/KayitZamaniKontrolu"
TOKEN_REFRESH_INTERVAL = 60  # Token refresh interval (seconds)

# === CLASS DEFINITON ===
class ContinuousTokenFetcher(threading.Thread):
    """
    Thread class that continuously fetches tokens in the background.
    Provides thread-safe token access.
    """
    def __init__(self, url: str, login: str, password: str, use_headless_browser: bool=False) -> None:
        super().__init__(daemon=True)
        self.url = url
        self.creds = [login, password]
        self.driver = None
        self._token = ""
        self._token_lock = threading.Lock()
        self._running = False
        self._started_event = threading.Event()
        self.use_headless_browser = use_headless_browser
    
    def login_to_kepler(self) -> None:
        """Starts the driver and performs login."""
        is_repeat = self._started_event.is_set()

        Logger.log("Kepler açılıyor...", silent=is_repeat)
        if self.driver is None:
            self.driver = DriverManager.create_driver(headless=self.use_headless_browser)
        
        self.driver.get(self.url)

        # Wait to see if the URL changes to the login page
        sleep(PAGE_LOAD_DELAY)
        if "girisv3.itu.edu.tr" not in self.driver.current_url: 
            Logger.log("Kepler'e giriş yapılmış, giriş yapma aşaması atlanıyor...", silent=is_repeat)
            return
        
        # Login to the system
        Logger.log("Kepler'e giriş yapılıyor...", silent=is_repeat)
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
        
        if "SelectIdentity" in self.driver.current_url:
            sleep(.1)
            Logger.log("Yatay geçiş hesabı algılandı, aktif İTÜ hesabı seçilecek.", silent=is_repeat)
            identity_cards = self.driver.find_elements(By.CLASS_NAME, "card-body")
            for identity_card in identity_cards:
                rows = identity_card.find_elements(By.TAG_NAME, "tr")
                last_row = rows[-1]
                content = last_row.get_attribute("innerHTML").lower()
                if "durum" in content and "aktif" in content:
                    try:
                        selected_field = rows[1].find_element(By.TAG_NAME, "td").get_attribute("innerHTML").strip()
                        selected_studentid = rows[2].find_element(By.TAG_NAME, "td").get_attribute("innerHTML").strip()
                        Logger.log(f"Seçilen hesap: \"{selected_field} ({selected_studentid})\".")
                    except Exception:
                        pass
                    

                    select_button = identity_card.find_element(By.TAG_NAME, "a")
                    select_button.click()
                    sleep(.1)
                    break
        
        Logger.log("Kepler'e giriş yapıldı, ders seçim sitesine yönlendiriliyor...")
        self.driver.get(self.url)
        sleep(PAGE_LOAD_DELAY)
    
    def _fetch_token_once(self) -> str:
        """Single token fetch operation. Re-login if logged out after refresh."""
        # if the url is not the target url, open the target url
        if self.url not in self.driver.current_url:
            Logger.log("Ders seçim sitesi açılıyor...", silent=self._started_event.is_set())
            self.driver.get(self.url)
            sleep(PAGE_LOAD_DELAY)

        self.driver.refresh()
        sleep(1)

        # Check if we got logged out after refresh (login page detected)
        if "girisv3.itu.edu.tr" in self.driver.current_url:
            Logger.log("Kepler hesabından çıkıldığı algılandı, tekrar giriş yapılıyor...")
            self.login_to_kepler()
            # After re-login, refresh again to ensure requests are captured
            self.driver.refresh()
            sleep(1)

        for request in self.driver.requests:
            # if There is a response and the request is from the token url
            if request.response and TOKEN_URL in request.url:
                token = request.headers["authorization"]
                return token
        return ""
    
    def run(self) -> None:
        """Thread main loop - continuously fetches tokens."""
        self._running = True
        Logger.log("Token fetcher thread başlatıldı, sürekli token alınacak...", silent=True)
        
        while self._running:
            try:
                Logger.log("Yeni API Token aranıyor.", silent=True)
                new_token = self._fetch_token_once()
                if new_token and "ERROR" not in new_token and new_token != self._token:
                    with self._token_lock:
                        self._token = new_token
                    Logger.log("API Token güncellendi.")
                    
                    # Set event when first successful token is received
                    if not self._started_event.is_set():
                        self._started_event.set()
                        Logger.log("İlk token başarıyla alındı.")
            except Exception as e:
                Logger.log(f"Token fetch hatası: {e}", silent=True)
            
            sleep(TOKEN_REFRESH_INTERVAL)
    
    def get_token(self) -> str:
        """Thread-safe token access."""
        with self._token_lock:
            return self._token
    
    def wait_for_first_token(self, timeout: float = 60) -> bool:
        """Waits until the first token is received."""
        return self._started_event.wait(timeout)
    
    def stop(self) -> None:
        """Stops the token fetcher."""
        self._running = False
        Logger.log("Token fetcher thread durduruluyor...")
        if self.driver:
            try:
                self.driver.minimize_window()
            except:
                pass
    
    def has_token(self) -> bool:
        """Checks if a token exists."""
        with self._token_lock:
            return len(self._token) > 0
