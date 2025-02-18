# === IMPORTS ===
from token_fetcher import TokenFetcher
import requests
from time import sleep
from datetime import datetime, timedelta
from logger import Logger
from driver_manager import DriverManager
from request_manager import RequestManager
import os
import json

# === CONSTANTS ===
CONFIG_FILE_PATH = "data/config.json"
TARGET_URL = "https://obs.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayit"
REQUEST_URL = "https://obs.itu.edu.tr/api/ders-kayit/v21/"

# Both are in seconds:
DELAY_BETWEEN_TRIES = 3 # WARNING: If you want to tweak this value, decreasing it may cause you to hit the API rate limit.
SPAM_DUR = 60 * 10 # Deternimes how long the program will spam the API HTTP request, in seconds.

def read_inputs() -> tuple[str, str, list[str], list[str], datetime | None]:
    Logger.log("Input dosyaları okunuyor...")
    data = json.load(open(CONFIG_FILE_PATH))
    
    # Read account details
    account = data.get("account")
    login, password = account.get("username"), account.get("password")
    Logger.log(f"İTÜ hesap bilgileri okundu: {login}, {len(password) * '*'}.")

    # Read course details
    course_data = data.get("courses")

    if "scrn" in course_data.keys():
        scrn_list = [str(scrn) for scrn in course_data.get("scrn")]
        Logger.log(f"SCRN listesi okundu: {scrn_list}.")
    else:
        scrn_list = []
        Logger.log(f"SCRN listesi bulunamadı.")

    if "crn" in course_data.keys():
        crn_list = [str(crn) for crn in course_data.get("crn")]
        Logger.log(f"CRN listesi okundu: {crn_list}.")
    else:
        crn_list = []
        Logger.log(f"CRN listesi bulunamadı.")

    # Read time
    try:
        time_data = data.get("time")
        start_time = datetime(time_data.get("year"), time_data.get("month"), time_data.get("day"), time_data.get("hour"), time_data.get("minute"), time_data.get("seconds") if "seconds" in time_data.keys() else 0)
        Logger.log(f"Ders seçim zamanı ve tarihi okundu: {start_time}.")
    except Exception:
        start_time = None
        Logger.log(f"Ders seçim zamanı ve tarihi girilmedi, ders seçimine hemen başlanacak.")
    
    return login, password, crn_list, scrn_list, start_time

def request_course_selection(token: str, crn_list: list[str], scrn_list: list[str]) -> str:
    response = requests.post(REQUEST_URL, headers={'Authorization': token}, json={"ECRN": crn_list, "SCRN": scrn_list})
    
    result_code = response.text
    return result_code

if __name__ == "__main__":
    shutdown_on_complete = input("Ders seçimi tamamlandıktan sonra bilgisayar kapatılsın mı? (e/h): ").lower() == "e"
    Logger.log(f"Ders seçim tamamlandıktan sonra bilgisayar {'kapatılacak' if shutdown_on_complete else 'kapatılmayacak'}.")

    # Read input files
    login, password, crn_list, scrn_list, start_time = read_inputs()

    if len(crn_list) == 0 and len(scrn_list) == 0:
        Logger.log("CRN ve SCRN listeleri boş, ders seçimi yapılmayacak.")
        exit()

    # Wait untill 5 mins before the registration starts, if time left to selection is < 5 mins, start instantly.
    if start_time is not None:
        delta = (start_time - datetime.now() - timedelta(seconds=60 *5)).total_seconds()

    if start_time is not None:
        if delta > 0:
            Logger.log(f"Ders seçimine 5 dakika kalana kadar bekleniyor ({delta} saniye)...")
            sleep(delta)

    # Log into the website.
    token_fetcher = TokenFetcher(TARGET_URL, login, password)
    token_fetcher.start_driver()

    # Wait untill 45 secs before the registration starts.
    if start_time is not None:
        delta = (start_time - datetime.now() - timedelta(seconds=45)).total_seconds()
        Logger.log(f"Ders seçimine 45 saniye kalana kadar bekleniyor ({delta} saniye)...")
        sleep(delta)

    # Fetch auth token, until 30 secs before the registration starts.
    token = ""
    while start_time is None or (start_time - datetime.now()).total_seconds() > 30:
        new_token = token_fetcher.fetch_token()
        if "ERROR" not in new_token:
            token = new_token

        sleep(.1)

        # If the start time is not set, break the loop on first successful token fetch.
        if start_time is None and "ERROR" not in token:
            break

    # Wait untill the registration starts. (Add a buffer to prevent any possible errors.)
    token_fetcher.driver.minimize_window()
    if start_time is not None:
        Logger.log("Ders seçimine kadar bekleniliyor (Chrome penceresini kapatmayın)...")
        sleep((start_time - datetime.now()).total_seconds() + 0.1)

    # Select courses, do it until `DURATION_TO_SPAM` secs after the registration starts.
    Logger.log("Dersler Seçiliyor...")
    request_manager = RequestManager(token, REQUEST_URL)
    while start_time is None or (datetime.now() - start_time).total_seconds() < SPAM_DUR:
        crn_list, scrn_list = request_manager.request_course_selection(crn_list, scrn_list)
        sleep(DELAY_BETWEEN_TRIES)
        
        if len(crn_list) == 0 and len(scrn_list) == 0:
            Logger.log(f"Bütün dersler başarıyla alındı/bırakıldı.")
            break
        Logger.log("Alınamayan dersler tekrar deneniyor...")
        print()

    if not len(crn_list) == 0 or not len(scrn_list) == 0:
        Logger.log(f"Ders seçimi zaman aşımından dolayı sonlandırıldı. Alınamayan dersler: {crn_list}, Bırakılamayan Dersler {scrn_list}.")

    # Turn off the computer, if asked for it, else, just exit.
    if shutdown_on_complete:
        sleep(5)
        DriverManager.clear_drivers()
        Logger.log("Ders seçimi tamamlandı. Bilgisayar kapatılıyor...")
        os.system("shutdown /s /t 1")
    else:
        Logger.log("Ders seçimi tamamlandı. Program sonlandırılıyor...")
        exit()
