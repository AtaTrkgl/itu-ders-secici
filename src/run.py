# === IMPORTS ===
from token_fetcher import TokenFetcher
import requests
from time import sleep
from datetime import datetime, timedelta
from logger import Logger

# === CONSTANTS ===
CREDS_FILE_NAME = "creds.txt"
CRNS_FILE_NAME = "crn_list.txt"
TIME_FILE_NAME = "time.txt"
TARGET_URL = "https://kepler-beta.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayit"
REQUEST_URL = "https://kepler-beta.itu.edu.tr/api/ders-kayit/v21/"
MAX_TRIES = 300
DELAY_BETWEEN_TRIES = .05

def read_inputs() -> tuple[str, str, list[str]]:
    Logger.log("Input dosyaları okunuyor...")
    with open(f"data/{CREDS_FILE_NAME}") as f:
        [login, password] = [line.strip() for line in f.readlines()]

    with open(f"data/{CRNS_FILE_NAME}") as f:
        crn_list = list(dict.fromkeys([line.strip() for line in f.readlines()]))

    with open(f"data/{TIME_FILE_NAME}") as f:
        time_data = [int(x) for x in f.read().strip().split(" ")]
        start_time = datetime(time_data[0], time_data[1], time_data[2], time_data[3], time_data[4])

    return login, password, crn_list, start_time

def request_course_selection(token: str, crn_list: list[str]) -> str:
    response = requests.post(REQUEST_URL, headers={'Authorization': token}, json={"ECRN": crn_list, "SCRN": []})
    
    result_code = response.text
    return result_code

if __name__ == "__main__":
    # Read input files
    login, password, crn_list, start_time = read_inputs()

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

    # Fetch auth token, until 10 secs before the registration starts.
    token = ""
    while (start_time - datetime.now()).total_seconds() > 10:
        new_token = token_fetcher.fetch_token()
        if "ERROR" not in new_token:
            token = new_token

        sleep(.1)

    # Select courses, do it a few times just in case.
    Logger.log("Dersler Seçiliyor...")
    for _ in range(MAX_TRIES):
        request_course_selection(token, crn_list)
        sleep(DELAY_BETWEEN_TRIES)

    # Saving Logs.
    Logger.save_logs()
