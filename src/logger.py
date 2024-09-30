from datetime import datetime
from os import mkdir, path

import atexit

class Logger:
    logs = ""

    @staticmethod
    def create_message(message) -> str:
        return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] {message}"

    @staticmethod
    def log(message, silent: bool = False) -> None:
        msg = Logger.create_message(message)
        Logger.logs += msg + "\n"
        if not silent: print(msg)

        try:
            Logger.save_logs()
        except:
            pass

    @staticmethod
    def save_logs(file_name: str="temp_logs") -> None:
        if not path.exists("logs"):
            mkdir("logs")
        
        with open(f"logs/{file_name}.txt", "w", encoding="utf-8") as f:
            f.write(Logger.logs + Logger.create_message("Çıktılar kaydediliyor...\n"))

    @staticmethod
    def save_logs_with_time_stamp() -> None:
        time_stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        Logger.save_logs(f"logs_{time_stamp}")

atexit.register(Logger.save_logs_with_time_stamp)
