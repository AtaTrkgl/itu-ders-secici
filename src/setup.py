from requests import get
from datetime import datetime
from os import path, mkdir

ITU_HELPER_LESSONS_URL = "https://raw.githubusercontent.com/itu-helper/data/main/lesson_rows.txt"

CREDENTIALS_FILE_NAME = "creds.txt"
TIME_FILE_NAME = "time.txt"
CRN_FILE_NAME = "crn_list.txt"
SCRN_FILE_NAME = "scrn_list.txt"
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

    # Make sure the data dirrectory exists.
    if not path.exists("data"):
        mkdir("data")

    with open(f"data/{CREDENTIALS_FILE_NAME}", "w") as f:
        f.write(f"{user_name}\n{password}")

    with open(f"data/{TIME_FILE_NAME}", "w") as f:
        f.write(time_text)

    with open(f"data/{CRN_FILE_NAME}", "w") as f:
        f.writelines(crn_list_to_lines(crn_list))

    with open(f"data/{SCRN_FILE_NAME}", "w") as f:
        f.writelines(crn_list_to_lines(scrn_list))

    print("Dosyalar başarıyla kaydedildi. Sihirbaz sonlandırıldı.")
    