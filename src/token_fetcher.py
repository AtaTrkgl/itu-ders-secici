# === IMPORTS ===
from driver_manager import DriverManager
from selenium.webdriver.common.by import By
from time import sleep
from logger import Logger

# === CONSTANTS ===
PAGE_LOAD_DELAY = 3
TOKEN_URL = "https://kepler-beta.itu.edu.tr/api/ogrenci/Takvim/KayitZamaniKontrolu"

# === CLASS DEFINITON ===
class TokenFetcher:
    def __init__(self, url: str, login: str, password: str) -> None:
        # Create a new instance of the chrome web driver
        Logger.log("Initializing web driver...")
        self.driver = DriverManager.create_driver()
        self.url = url
        self.creds = [login, password]
        
    def start_driver(self) -> None:
        Logger.log("Opening Kepler Website...")
        self.driver.get(self.url)

        # Wait to see if the URL changes to the login page
        sleep(PAGE_LOAD_DELAY)
        if "girisv3.itu.edu.tr" not in self.driver.current_url: 
            Logger.log("Already logged into Kepler Website, skipping the login process...")
            return
        
        # Login to the system
        Logger.log("Logging into Kepler Website...")
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

        Logger.log("Logged into Kepler Website, reloading the target URL...")
        self.driver.get(self.url)
        sleep(PAGE_LOAD_DELAY)

    def fetch_token(self) -> str:
        # if the url is not the target url, open the target url
        if self.url not in self.driver.current_url:
            Logger.log("Opening the target URL...")
            self.start_driver()

        Logger.log("Fetching API Token...")
        self.driver.refresh()
        sleep(1)
        for request in self.driver.requests:
            # if There is a response and the request is from the token url
            if request.response and TOKEN_URL in request.url:
                token = request.headers["authorization"]
                return token
        return "ERROR"

# # Access requests via the `requests` attribute
# for request in driver.requests:
#     if request.response:
#     # here you need to filter the name of the url request you want
#     # if "name_of_the_url_in_header" in request.url
#         Logger.log(
#             request.url
#             request.headers['cookie']
#         )