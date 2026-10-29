"""APEXUS 1V — точка входу.

Під час запуску сама перевіряє бібліотеки й за потреби завантажує їх через pip.
Запуск:  python main.py
"""
import importlib
import importlib.util
import os
import subprocess
import sys
import traceback

APP_TITLE = "APEXUS 1V"
HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = bool(getattr(sys, "frozen", False))  # True, якщо це зібраний .exe
REQUIRED_MODULES = {"PySide6": "PySide6", "requests": "requests"}


def say(text: str = "") -> None:
    """Безпечний print (у .exe без консолі stdout може бути None)."""
    try:
        if sys.stdout is not None:
            print(text, flush=True)
    except Exception:
        pass


def pause() -> None:
    """Не закриваємо термінал, щоб користувач встиг прочитати повідомлення."""
    if FROZEN or sys.stdin is None:
        return
    try:
        input("\nНатисніть Enter, щоб закрити це вікно…")
    except (EOFError, KeyboardInterrupt, RuntimeError):
        pass


def fatal_dialog(text: str) -> None:
    """Для .exe без консолі: показуємо помилку у вікні Windows."""
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, text, APP_TITLE, 0x10)
    except Exception:
        pass


def setup_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream is not None:
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def check_python() -> bool:
    if sys.version_info < (3, 12):
        say(f"[ПОМИЛКА] Потрібен Python 3.12 або новіший, а у вас {sys.version.split()[0]}.")
        say("Завантажте Python тут: https://www.python.org/downloads/")
        say("Під час встановлення поставте галочку «Add python.exe to PATH».")
        return False
    return True


def missing_modules() -> list[str]:
    return [pkg for mod, pkg in REQUIRED_MODULES.items() if importlib.util.find_spec(mod) is None]


def ensure_dependencies() -> bool:
    """Перевіряє бібліотеки; якщо чогось бракує — встановлює автоматично.

    Повертає True, якщо після встановлення треба перезапустити процес.
    """
    if FROZEN:
        return False
    missing = missing_modules()
    if not missing:
        return False

    say(f"[APEXUS 1V] Не знайдено бібліотеки: {', '.join(missing)}")
    say("[APEXUS 1V] Завантажую їх автоматично (потрібен інтернет, перший запуск може тривати кілька хвилин)…\n")

    if importlib.util.find_spec("pip") is None:
        try:
            import ensurepip

            ensurepip.bootstrap()
        except Exception as exc:
            raise RuntimeError(
                f"pip не встановлено ({exc}). Перевстановіть Python з python.org і "
                "залиште увімкненою опцію «pip»."
            ) from exc

    req = os.path.join(HERE, "requirements.txt")
    cmd = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check"]
    cmd += ["-r", req] if os.path.exists(req) else missing
    code = subprocess.call(cmd)
    if code != 0:
        raise RuntimeError(
            "Не вдалося встановити залежності автоматично.\n"
            "Перевірте інтернет і виконайте вручну в папці проєкту:\n"
            "    python -m pip install -r requirements.txt"
        )
    importlib.invalidate_caches()
    say("\n[APEXUS 1V] Бібліотеки встановлено.\n")
    return True


def run_app() -> int:
    from PySide6.QtWidgets import QApplication

    from interface import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    return app.exec()


def main() -> int:
    setup_console()
    say("=" * 52)
    say(f"  {APP_TITLE} — запуск…")
    say("=" * 52)

    if not check_python():
        pause()
        return 1

    try:
        if ensure_dependencies():
            # Перезапускаємо процес, щоб свіжовстановлені бібліотеки гарантовано підхопилися
            return subprocess.call([sys.executable, os.path.abspath(__file__), *sys.argv[1:]])

        say(f"[{APP_TITLE}] Запускаю інтерфейс… (щоб вийти — закрийте вікно)")
        code = run_app()
        say(f"[{APP_TITLE}] Застосунок закрито.")
        return code
    except Exception as exc:
        details = traceback.format_exc()
        say(f"\n[ПОМИЛКА] {exc}\n")
        say(details)
        if FROZEN:
            try:
                with open(os.path.join(os.path.dirname(sys.executable), "crash.log"), "w", encoding="utf-8") as f:
                    f.write(details)
            except Exception:
                pass
            fatal_dialog(f"{APP_TITLE}: сталася помилка.\n\n{exc}")
        pause()
        return 1


if __name__ == "__main__":
    sys.exit(main())
