from requests import get
from datetime import datetime, timedelta
from os import path, mkdir
import json

ITU_HELPER_LESSONS_URL = "https://raw.githubusercontent.com/itu-helper/data/main/lessons.psv"
ITU_HELPER_COURSES_URL = "https://raw.githubusercontent.com/itu-helper/data/main/courses.psv"

DATA_DIR = "data"
CONFIG_FILE_NAME = "config.json"
LINE_SPACES = 2

def eval_input(inp: str):
    if inp == "q":
        print("Sihirbaz sonlandırıldı.")
        exit()
    
    return inp.strip()


def ask_for_crn_list() -> tuple[list[str], int]:
    crn_list = []
    last_inp = []
    total_creds = 0
    while last_inp != "":
        last_inp = eval_input(input("CRN: "))
        if last_inp == "":
            continue

        if last_inp not in crn_to_lesson.keys():
            ans = input("Girilen CRN, ITU Helper veritabanında bulunamadı, yinede eklemek istiyor musunuz? [e/h]").lower()
            if ans != "e":
                continue
        else:
            course_code = crn_to_lesson[last_inp]
            course_name, course_credits = lesson_to_course[course_code]

            try:
                course_credits = float(course_credits)
            except Exception:
                course_credits = None

            print(f"Dersin ITU Helper veritabanında bulunan adı: {course_code} ({course_name}) [Kredi: {course_credits if course_credits is not None else '???'}]")
            if course_credits is not None:
                total_creds += course_credits

        crn_list.append(last_inp)

    return crn_list, total_creds

def get_formatted_crn_list(crn_list: list[str]) -> list[str]:
    return [f"{crn} ({crn_to_lesson[crn] if crn in crn_to_lesson.keys() else '???'})" for crn in crn_list]

def crn_list_to_lines(crn_list: list[str]) -> list[str]:
    return [crn + ("\n" if i != len(crn_list) - 1 else "") for i, crn in enumerate(crn_list)]

if __name__ == "__main__":
    print("ITU Helper bağlantısı kuruluyor...")
    # Read the course names from ITU Helper.
    lesson_lines = get(ITU_HELPER_LESSONS_URL).text.split("\n")
    crn_to_lesson = {lesson.split("|")[0] : lesson.split("|")[1] for lesson in lesson_lines if len(lesson.split("|")) > 1}
    
    course_lines = get(ITU_HELPER_COURSES_URL).text.split("\n")
    lesson_to_course = {course.split("|")[0] : (course.split("|")[1], course.split("|")[3]) for course in course_lines if len(course.split("|")) > 1}
    
    # Print the startup message.
    print("\n"*100)
    print("ITU Ders seçici kurulum sihirbazına hoşgeldiniz.")
    print("Herhangi bir adımda \"q\" tuşuna basarak sihibarızı sonlandırabilirsiniz, son adıma kadar girdikleriniz kayıt edilmeyecektir..")

    print("\n"*LINE_SPACES)

    # Ask for credentials.
    user_name = eval_input(input("ITU kullanıcı adınızı girin: "))
    password = eval_input(input("ITU kullanıcı şifrenizi girin: ", ))

    print("\n"*LINE_SPACES)

    # Ask for the course selection time.
    date = eval_input(input("Ders seçim tarihini girin (YYYY.MM.DD, örnek: \"2024.09.08\", \" kullanmayın): "))
    time = eval_input(input("Ders seçim saatini girin (HH:mm, örnek: \"17:00\", \" kullanmayın): "))
    time_text = date.replace(".", " ") + " " + time.replace(":", " ")

    print("Programı test ettiyseniz ve İTÜ'nün saati ile lokal saatiniz arasında bir fark var ise, bu farkı saniye cinsinden girin, yok ise boş bırakın.")
    offset_in_seconds = eval_input(input("saniye cinsinden gecikme: "))
    offset_in_seconds = int(offset_in_seconds) if offset_in_seconds.isnumeric() else 0

    print("\n"*LINE_SPACES)

    # Ask for the CRNs.
    print("Almak istediğiniz derslerin CRN'lerini girin, bitirmek için hiç bir şey girmeden Enter tuşuna basın.")
    crn_list, crn_creds = ask_for_crn_list()
    print("Toplam kredi: ", crn_creds)

    print("\n"*LINE_SPACES)

    # Ask for the SCRNs.
    wants_to_drop = eval_input(input("Bırakmak istediğiniz ders(ler) var mı? [e/h]")).lower() == "e"
    scrn_list = []
    if wants_to_drop:
        print("Bırakmak istediğiniz derslerin CRN'lerini girin, bitirmek için hiç bir şey girmeden Enter tuşuna basın.")
        scrn_list, _ = ask_for_crn_list()

    selection_datetime = datetime(*[int(x) for x in time_text.split(" ")]) - timedelta(seconds=offset_in_seconds)

    # Print the summary.
    print("Kurulum Tamamlandı, son olarak her şey doğru görünüyor mu?")
    print("\n"*LINE_SPACES)
    print("ITU Kullanıcı Adı:", user_name)
    print("ITU Kullanıcı Şifresi:", password)
    print("\n"*LINE_SPACES)
    print(f"Ders Seçim Zamanı ({offset_in_seconds}sn gecikme): ", selection_datetime)
    print("\n"*LINE_SPACES)
    print("Alınacak CRN'ler: ", get_formatted_crn_list(crn_list))
    print("Alınacak Kredi: ", crn_creds)
    print("Bırakılacak CRN'ler: ", get_formatted_crn_list(scrn_list))
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
            "year": selection_datetime.year,
            "month": selection_datetime.month,
            "day": selection_datetime.day,
            "hour": selection_datetime.hour,
            "minute": selection_datetime.minute,
            "seconds": selection_datetime.second
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
    