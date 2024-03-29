# === IMPORTS ===
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
from logger import Logger

import atexit

# === CLASS DEFINITON ===
class DriverManager:
    active_drivers = []

    @staticmethod
    def create_driver():
        Logger.log("Web sürücüsü başlatılıyor...")
        chrome_options = Options()

        chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("log-level=2")
        # chrome_options.add_argument("--no-proxy-server")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        DriverManager.active_drivers.append(driver)
        return driver
    
    @staticmethod
    def clear_drivers():
        Logger.log("Aktif web sürücüleri temizleniyor...")
        for driver in DriverManager.active_drivers:
            driver.quit()

# === DRIVER CLEANUP ===
atexit.register(DriverManager.clear_drivers)