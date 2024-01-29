# === IMPORTS ===
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
from logger import Logger

import atexit


# === DRIVER CLEANUP ===
active_drivers = []
def exit_handler():
    Logger.log("Aktif web sürücüleri temizleniyor...")
    for driver in active_drivers:
        driver.quit()

    Logger.save_logs()

atexit.register(exit_handler)

# === CLASS DEFINITON ===
class DriverManager:
    @staticmethod
    def create_driver():
        chrome_options = Options()

        chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("log-level=2")
        # chrome_options.add_argument("--no-proxy-server")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        active_drivers.append(driver)
        return driver
