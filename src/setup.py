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


def ask_for_crn_list(allow_backup_crns:bool) -> tuple[list[str], float, list[float]]:
    if allow_backup_crns:
        print("   İPUCU: Yedek CRN girmek için \"CRN:YEDEK_CRN\" formatını kullanabilirsiniz.")
        print("   Örnek: \"21345:21346\" → Asıl CRN: 21345, Yedek CRN: 21346")
        print("   Yedek CRN, asıl CRN'nin kontenjanı dolduğunda otomatik olarak denenecektir.\n")
    
    crn_list = []
    last_inp = []
    total_creds = 0.0
    total_creds_range = [0.0, 0.0]
    while last_inp != "":
        last_inp = eval_input(input("CRN: "))
        if last_inp == "":
            continue

        # Check if backup CRN format is used
        primary_crn = last_inp.split(":")[0] if ":" in last_inp else last_inp
        backup_crn = last_inp.split(":")[1] if ":" in last_inp else None
        
        if not allow_backup_crns and backup_crn is not None:
            last_inp = last_inp.split(":")[0]
            backup_crn = None

        no_match, backup_crn_no_match = False, False
        course_credits, backup_course_credits = None, None
        if primary_crn not in crn_to_lesson.keys():
            no_match = True
        elif backup_crn is not None and backup_crn not in crn_to_lesson.keys():
            backup_crn_no_match = True
        else:
            try:
                course_code = crn_to_lesson[primary_crn]
                course_name, course_credits = lesson_to_course[course_code]

                try:
                    course_credits = float(course_credits)
                except Exception:
                    course_credits = None

                print(f"Dersin ITU Helper veritabanında bulunan adı: {course_code} ({course_name}) [Kredi: {course_credits if course_credits is not None else '???'}].")
                if course_credits is not None:
                    total_creds += course_credits
                
            except Exception as e:
                no_match = True
            
            if backup_crn:
                try:
                    backup_course_code = crn_to_lesson[backup_crn]
                    backup_course_name, backup_course_credits = lesson_to_course[backup_course_code]
                    
                    try:
                        backup_course_credits = float(backup_course_credits)
                    except Exception:
                        backup_course_credits = None
                    
                    print(f"  ↳ Yedek CRN: {backup_crn}.")
                    print(f"  ↳ Yedek dersin ITU Helper veritabanında bulunan adı: {backup_course_code} ({backup_course_name}) [Kredi: {backup_course_credits if backup_course_credits is not None else '???'}].")
                except Exception as e:
                    backup_crn_no_match = True

        if course_credits is not None:
            if backup_course_credits is not None:
                total_creds_range[0] += min(course_credits, backup_course_credits)
                total_creds_range[1] += max(course_credits, backup_course_credits)
            else:
                total_creds_range[0] += course_credits
                total_creds_range[1] += course_credits

        if no_match or backup_crn_no_match:
            error_message = ""
            if no_match and backup_crn_no_match:
                error_message = f"Girilen CRN'ler ({primary_crn} ve {backup_crn}) ITU Helper veritabanında bulunamadı."
            elif no_match:
                error_message = f"Girilen CRN ({primary_crn}) ITU Helper veritabanında bulunamadı."
            else:
                error_message = f"Girilen yedek CRN ({backup_crn}) ITU Helper veritabanında bulunamadı."

            ans = input(f"{error_message} Yinede eklemek istiyor musunuz? [e/h]\n\tℹ️ Sorun İTÜ Helper sisteminde olabilir.").lower()
            if ans != "e":
                continue
        
        crn_list.append(last_inp)

    return crn_list, total_creds, total_creds_range

def get_formatted_crn_list(crn_list: list[str]) -> list[str]:
    formatted = []
    for crn_entry in crn_list:
        if ":" in crn_entry:
            primary, backup = crn_entry.split(":", 1)
            lesson_name = crn_to_lesson.get(primary, '???')
            backup_name = crn_to_lesson.get(backup, '???')
            formatted.append(f"{primary} ({lesson_name}) [Yedek: {backup} ({backup_name})]")
        else:
            lesson_name = crn_to_lesson.get(crn_entry, '???')
            formatted.append(f"{crn_entry} ({lesson_name})")
    return formatted

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

    print("\n"*LINE_SPACES)

    # Ask for the CRNs.
    print("Almak istediğiniz derslerin CRN'lerini girin, bitirmek için hiç bir şey girmeden Enter tuşuna basın.")
    crn_list, crn_creds, crn_creds_range = ask_for_crn_list(allow_backup_crns=True)
    print("Toplam kredi: ", crn_creds)
    if crn_creds_range[0] != crn_creds_range[1]:
        print(f"Toplam kredi aralığı (yedek CRN'ler dahil): {crn_creds_range[0]} - {crn_creds_range[1]}")

    print("\n"*LINE_SPACES)

    # Ask for the SCRNs.
    wants_to_drop = eval_input(input("Bırakmak istediğiniz ders(ler) var mı? [e/h]")).lower() == "e"
    scrn_list = []
    if wants_to_drop:
        print("Bırakmak istediğiniz derslerin CRN'lerini girin, bitirmek için hiç bir şey girmeden Enter tuşuna basın.")
        scrn_list, _, __ = ask_for_crn_list(allow_backup_crns=False)

    selection_datetime = datetime(*[int(x) for x in time_text.split(" ")])

    # Print the summary.
    print("Kurulum Tamamlandı, son olarak her şey doğru görünüyor mu?")
    print("\n"*LINE_SPACES)
    print("ITU Kullanıcı Adı:", user_name)
    print("ITU Kullanıcı Şifresi:", password)
    print("\n"*LINE_SPACES)
    print(f"Ders Seçim Zamanı: ", selection_datetime)
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
            "minute": selection_datetime.minute
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
