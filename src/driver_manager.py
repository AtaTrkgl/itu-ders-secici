# === IMPORTS ===
import atexit
from typing import ClassVar

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from logger import Logger


# === CLASS DEFINITON ===
class DriverManager:
    active_drivers: ClassVar[list] = []

    @staticmethod
    def create_driver(headless: bool = False):
        Logger.log("Web sürücüsü başlatılıyor...")
        chrome_options = Options()

        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("log-level=2")
        # chrome_options.add_argument("--no-proxy-server")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        if headless:
            chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        DriverManager.active_drivers.append(driver)
        return driver

    @staticmethod
    def clear_drivers():
        Logger.log("Aktif web sürücüleri temizleniyor...")
        for driver in DriverManager.active_drivers:
            driver.quit()


# === DRIVER CLEANUP ===
atexit.register(DriverManager.clear_drivers)
