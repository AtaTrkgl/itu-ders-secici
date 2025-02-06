from requests import get
from datetime import datetime
from os import path, mkdir
import json

ITU_HELPER_LESSONS_URL = "https://raw.githubusercontent.com/itu-helper/data/main/lessons.psv"

DATA_DIR = "data"
CONFIG_FILE_NAME = "config.json"
LINE_SPACES = 2

def eval_input(inp: str):
    if inp == "q":
        print("Sihirbaz sonlandırıldı.")
        exit()
    
    return inp.strip()


def ask_for_crn_list() -> list[str]:
    crn_list = []
    last_inp = []
    while last_inp != "":
        last_inp = eval_input(input("CRN: "))
        if last_inp == "":
            continue

        if last_inp not in crn_to_lesson_line.keys():
            ans = input("Girilen CRN, ITU Helper veritabanında bulunamadı, yinede eklemek istiyor musunuz? [e/h]").lower()
            if ans != "e":
                continue
        else:
            print(f"Dersin ITU Helper veritabanında bulunan adı: {crn_to_lesson_line[last_inp]}")

        crn_list.append(last_inp)

    return crn_list


def crn_list_to_lines(crn_list: list[str]) -> list[str]:
    return [crn + ("\n" if i != len(crn_list) - 1 else "") for i, crn in enumerate(crn_list)]

if __name__ == "__main__":
    # Read the course names from ITU Helper.
    lines = get(ITU_HELPER_LESSONS_URL).text.split("\n")
    crn_to_lesson_line = {lesson.split("|")[0] : lesson.split("|")[1] for lesson in lines if len(lesson.split("|")) > 1}
    
    # Print the startup message.
    print("ITU Ders seçici kurulum sihirbazına hoşgeldiniz.")
    print("Herhangi bir adımda \"q\" tuşuna basarak sihibarızı sonlandırabilirsiniz, son adıma kadar girdikleriniz kayıt edilmeyecektir..")

    print("\n"*LINE_SPACES)

    # Ask for credentials.
    user_name = eval_input(input("ITU kullanıcı adınızı girin: "))
    password = eval_input(input("ITU kullanıcı şifrenizi girin: ", ))

    print("\n"*LINE_SPACES)

    # Ask for the course selection time.
    date = eval_input(input("Ders seçim tarihini girin (YYYY.MM.DD, örnek: \"2024.09.08\"): "))
    time = eval_input(input("Ders seçim saaiting girin (HH:mm, örnek: \"17:00\") "))
    time_text = date.replace(".", " ") + " " + time.replace(":", " ")

    print("\n"*LINE_SPACES)

    # Ask for the CRNs.
    print("Almak istediğiniz derslerin CRN'lerini girin, bitirmek için hiç bir şey girmeden Enter tuşuna basın.")
    crn_list = ask_for_crn_list()

    print("\n"*LINE_SPACES)

    # Ask for the SCRNs.
    wants_to_drop = eval_input(input("Bırakmak istediğiniz ders(ler) var mı? [e/h]")).lower() == "e"
    scrn_list = []
    if wants_to_drop:
        print("Bırakmak istediğiniz derslerin CRN'lerini girin, bitirmek için hiç bir şey girmeden Enter tuşuna basın.")
        scrn_list = ask_for_crn_list()

    # Print the summary.
    print("Kurulum Tamamlandı, son olarak her şey doğru görünüyor mu?")
    print("\n"*LINE_SPACES)
    print("ITU Kullanıcı Adı:", user_name)
    print("ITU Kullanıcı Şifresi:", password)
    print("\n"*LINE_SPACES)
    print("Ders Seçim Zamanı: ", datetime(*[int(x) for x in time_text.split(" ")]))
    print("\n"*LINE_SPACES)
    print("Alınacak CRN'ler: ", crn_list)
    print("Bırakılacak CRN'ler: ", scrn_list)
    print("\n"*LINE_SPACES)

    # Ask to save the data.
    eval_input(input("Eğer bir şeyler yanlış görünüyor ise \"q\" tuşuna basarak sihibazı sonlandırın, bilgileri kaydetmek için herhangi bir başka tuşa basın."))

    # Save the data.
    print("Kaydediliyor...")

    time_data = [int(x) for x in time_text.split(" ")]
    data_dict = {
        "account": {
            "username": user_name,
            "password": password
        },
        "time": {
            "year": time_data[0],
            "month": time_data[1],
            "day": time_data[2],
            "hour": time_data[3],
            "minute": time_data[4]
        },
        "courses": {
            "crn": crn_list,
            "scrn": scrn_list
        },
    }

    # Make sure the data dirrectory exists.
    if not path.exists(DATA_DIR):
        mkdir(DATA_DIR)

    with open(path.join(DATA_DIR, CONFIG_FILE_NAME), 'w') as f:
        json.dump(data_dict, f)

    print("Dosya başarıyla kaydedildi. Sihirbaz sonlandırıldı.")
    