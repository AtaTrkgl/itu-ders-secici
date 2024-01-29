from datetime import datetime
from os import mkdir, path

class Logger:
    logs = ""

    @staticmethod
    def log(message):
        msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
        Logger.logs += msg + "\n"
        print(msg)

    @staticmethod
    def save_logs():
        Logger.log("Saving logs...")
        if not path.exists("logs"):
            mkdir("logs")
        with open("logs/logs.txt", "w") as f:
            f.write(Logger.logs)
