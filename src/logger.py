import atexit
import sys
from datetime import datetime
from os import mkdir, path


class Logger:
    logs = ""
    _save_error_reported = False

    @staticmethod
    def create_message(message) -> str:
        return f"[{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] {message}"

    @staticmethod
    def safe_print(text: str) -> None:
        """Prints without ever raising because of an encoding problem.

        Redirected output (a file, a pipe, Task Scheduler) falls back to a
        legacy code page that cannot represent Turkish letters. Course
        selection runs inside these calls, so a display problem has to degrade
        the text instead of aborting the program.
        """
        try:
            print(text)
        except UnicodeEncodeError:
            encoding = getattr(sys.stdout, "encoding", None) or "ascii"
            print(text.encode(encoding, "replace").decode(encoding, "replace"))

    @staticmethod
    def log(message, silent: bool = False) -> None:
        msg = Logger.create_message(message)
        Logger.logs += msg + "\n"
        if not silent:
            Logger.safe_print(msg)

        try:
            Logger.save_logs()
        except Exception as e:  # noqa: BLE001
            # Only warn once; this runs on every log line, and during course
            # selection a repeated warning would drown out the actual output.
            if not Logger._save_error_reported:
                Logger._save_error_reported = True
                Logger.safe_print(f"Loglar dosyaya kaydedilirken bir hata oluştu: {e}")

    @staticmethod
    def save_logs(file_name: str = "temp_logs") -> None:
        if not path.exists("logs"):
            mkdir("logs")

        with open(f"logs/{file_name}.txt", "w", encoding="utf-8") as f:
            f.write(Logger.logs + Logger.create_message("Çıktılar kaydediliyor...\n"))

    @staticmethod
    def save_logs_with_time_stamp() -> None:
        time_stamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
        Logger.save_logs(f"logs_{time_stamp}")


atexit.register(Logger.save_logs_with_time_stamp)
