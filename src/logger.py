from datetime import datetime
from os import mkdir, path

class Logger:
    logs = ""

    @staticmethod
    def create_message(message):
        return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"

    @staticmethod
    def log(message):
        msg = Logger.create_message(message)
        Logger.logs += msg + "\n"
        print(msg)

        try:
            Logger.save_logs()
        except:
            pass

    @staticmethod
    def save_logs():
        if not path.exists("logs"):
            mkdir("logs")
        
        with open("logs/logs.txt", "w", encoding="utf-8") as f:
            f.write(Logger.logs + Logger.create_message("Çıktılar kaydediliyor...\n"))
