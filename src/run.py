# === IMPORTS ===
from token_fetcher import TokenFetcher
import requests
from time import sleep
from datetime import datetime, timedelta
from logger import Logger
from driver_manager import DriverManager
import os

# === CONSTANTS ===
CREDS_FILE_NAME = "creds.txt"
CRNS_FILE_NAME = "crn_list.txt"
SCRNS_FILE_NAME = "scrn_list.txt"
TIME_FILE_NAME = "time.txt"
TARGET_URL = "https://obs.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayit"
REQUEST_URL = "https://obs.itu.edu.tr/api/ders-kayit/v21/"

# Both are in seconds:
DELAY_BETWEEN_TRIES = 3 # WARNING: If you want to tweak this value, decreasing it may cause you to hit the API rate limit.
SPAM_DUR = 50 # Deternimes how long the program will spam the API HTTP request.

def read_inputs() -> tuple[str, str, list[str], list[str], datetime]:
    Logger.log("Input dosyaları okunuyor...")
    with open(f"data/{CREDS_FILE_NAME}") as f:
        [login, password] = [line.strip() for line in f.readlines()]
    Logger.log(f"İTÜ hesap bilgileri okundu: {login}, {len(password) * '*'}.")

    if not os.path.exists(f"data/{SCRNS_FILE_NAME}"):
        scrn_list = []
        Logger.log(f"SCRN listesi bulunamadı.")
    else:
        with open(f"data/{SCRNS_FILE_NAME}") as f:
            scrn_list = list(dict.fromkeys([line.strip() for line in f.readlines()]))
        Logger.log(f"SCRN listesi okundu: {scrn_list}.")

    with open(f"data/{CRNS_FILE_NAME}") as f:
            crn_list = list(dict.fromkeys([line.strip() for line in f.readlines()]))
    Logger.log(f"CRN listesi okundu: {crn_list}.")

    with open(f"data/{TIME_FILE_NAME}") as f:
        time_data = [int(x) for x in f.read().strip().split(" ")]
        start_time = datetime(time_data[0], time_data[1], time_data[2], time_data[3], time_data[4])
    Logger.log(f"Ders seçim zamanı ve tarihi okundu: ({start_time.strftime('%d/%m/%Y %H:%M')}).")

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

    # Wait untill 2 mins before the registration starts.
    delta = (start_time - datetime.now() - timedelta(seconds=120)).total_seconds()
    Logger.log(f"Ders seçimine 2 dakika kalana kadar bekleniyor ({delta} saniye)...")
    sleep(delta)

    # Log into the website.
    token_fetcher = TokenFetcher(TARGET_URL, login, password)
    token_fetcher.start_driver()

    # Wait untill 45 secs before the registration starts.
    delta = (start_time - datetime.now() - timedelta(seconds=45)).total_seconds()
    Logger.log(f"Ders seçimine 45 saniye kalana kadar bekleniyor ({delta} saniye)...")
    sleep(delta)

    # Fetch auth token, until 30 secs before the registration starts.
    token = ""
    while (start_time - datetime.now()).total_seconds() > 30:
        new_token = token_fetcher.fetch_token()
        if "ERROR" not in new_token:
            token = new_token

        sleep(.1)

    # Wait untill the registration starts. (Add a buffer to prevent any possible errors.)
    Logger.log("Ders seçimine kadar bekleniliyor...")
    sleep((start_time - datetime.now()).total_seconds() + 0.1)

    # Select courses, do it until `DURATION_TO_SPAM` secs after the registration starts.
    Logger.log("Dersler Seçiliyor...")
    while (datetime.now() - start_time).total_seconds() < SPAM_DUR:
        Logger.log(request_course_selection(token, crn_list, scrn_list), silent=True)
        sleep(DELAY_BETWEEN_TRIES)

    # Turn off the computer, if asked for it, else, just exit.
    if shutdown_on_complete:
        sleep(5)
        DriverManager.clear_drivers()
        Logger.log("Ders seçimi tamamlandı. Bilgisayar kapatılıyor...")
        os.system("shutdown /s /t 1")
    else:
        Logger.log("Ders seçimi tamamlandı. Program sonlandırılıyor...")
        exit()
