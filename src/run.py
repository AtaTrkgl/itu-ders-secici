# === IMPORTS ===
from token_fetcher import TokenFetcher
import requests
from time import sleep

# === CONSTANTS ===
CREDS_FILE_NAME = "creds.txt"
CRNS_FILE_NAME = "crn_list.txt"
TARGET_URL = "https://kepler-beta.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayit"
REQUEST_URL = "https://kepler-beta.itu.edu.tr/api/ders-kayit/v21/"
MAX_TRIES = 1
DELAY_BETWEEN_TRIES = .05

def read_inputs() -> tuple[str, str, list[str]]:
    print("Reading input files...")
    with open(f"data/{CREDS_FILE_NAME}") as f:
        [login, password] = [line.strip() for line in f.readlines()]

    with open(f"data/{CRNS_FILE_NAME}") as f:
        crn_list = list(set([line.strip() for line in f.readlines()]))

    return login, password, crn_list

def request_course_selection(token: str, crn_list: list[str]) -> str:
    response = requests.post(REQUEST_URL, headers={'Authorization': token}, json={"ECRN": crn_list, "SCRN": []})
    
    result_code = response.text
    return result_code

if __name__ == "__main__":
    # Read input files
    login, password, crn_list = read_inputs()

    # Fetch auth token
    token_fetcher = TokenFetcher(TARGET_URL, login, password)
    token = token_fetcher.fetch_token()
    if "ERROR" in token:
        print("Failed to fetch the token, exiting...")
        exit(1)

    print(f"Fetched Token: {token}")

    # Select courses, do it a few times just in case.
    for _ in range(MAX_TRIES):
        request_course_selection(token, crn_list)
        sleep(DELAY_BETWEEN_TRIES)

    # Report via Telegram.

    pass